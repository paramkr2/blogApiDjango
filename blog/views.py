from rest_framework import generics, status 
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly , IsAuthenticated,IsAdminUser
from .models import Post,Profile,Query
from .serializers import PostSerializer,ProfileSerializer,QuerySerializer
from .pagination import PostPagination
from django.shortcuts import get_object_or_404
from .utils import resize_image


class IsOwnerOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET requests
        if request.method in ['GET']:
            return True
        # Write permissions are only allowed to the owner of the post
        return obj.author == request.user

class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        user = self.request.user
        post_type = self.request.query_params.get('type')  # Get 'type' query param
        queryset = Post.objects.none()  # Start with an empty queryset

        if user.is_authenticated:
            if post_type == 'draft':
                queryset = Post.objects.filter(author=user, is_published=False).order_by('-created_at')
            elif post_type == 'published':
                queryset = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
            else:
                # Return both published posts and user's drafts
                queryset = Post.objects.filter(author=user).order_by('-created_at')
        else:
            # Return only published posts for unauthenticated users
            queryset = Post.objects.filter(is_published=True).order_by('-created_at')

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  # Copy the request data to modify it
        data['author'] = request.user.pk  # Set the author field to the logged-in user's ID
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        post = serializer.instance
        # Reverse the URL for the newly created post
        new_path = reverse('post-detail', kwargs={'pk': post.pk}, request=request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        # This method retrieves the post based on the primary key in the URL (e.g., /posts/<id>/)
        print('here')
        return super().get_object()



class PostDraftView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.is_published = False
        post.save()
        return Response({"status": "Post reverted to draft successfully."}, status=status.HTTP_200_OK)

class PostPublishView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.is_published = True
        post.save()
        return Response({"status": "Post published successfully."}, status=status.HTTP_200_OK)


from .models import ImageUpload  # Make sure to create this model
from .serializers import ImageUploadSerializer  # Create this serializer

class ImageUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from django.views.decorators.csrf import csrf_exempt
from firebase_admin import storage
import uuid

  
class FirebaseImageUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # Check if the request contains a file
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}.jpg"

        # Get a reference to the storage bucket
        bucket = storage.bucket()
        blob = bucket.blob(unique_filename)

        # Upload the image to Firebase Storage
        blob.upload_from_file(image.file, content_type=image.content_type)
        
        # Make the file publicly accessible
        blob.make_public()

        return Response({'image': blob.public_url}, status=status.HTTP_201_CREATED)




class ProfileDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        user_identifier = self.kwargs.get('user_identifier')

        if user_identifier:
            # Fetch the user based on primary key or username
            if user_identifier.isdigit():
                user_profile = get_object_or_404(Profile, user__id=user_identifier)
            else:
                user_profile = get_object_or_404(Profile, user__username=user_identifier)
        else:
            # If no user_identifier is provided, return the authenticated user's profile
            return self.request.user.profile

        return user_profile

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        old_image_url = profile.image_url

        # Handle the image upload to Firebase if an image is provided
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Resize the image
            resized_image = resize_image(image)
            unique_filename = f"{uuid.uuid4()}.jpg"
            bucket = storage.bucket()
            blob = bucket.blob(unique_filename)
            blob.upload_from_file(resized_image, content_type=image.content_type)
            blob.make_public()
            new_image_url = blob.public_url

            # Update the profile with the new image URL
            profile.image_url = new_image_url

            # Delete the old image from Firebase if it exists
            if old_image_url:
                old_blob = bucket.blob(old_image_url.split('/')[-1])
                old_blob.delete()

        # Proceed with updating the rest of the profile (e.g., fullname)
        return super().update(request, *args, **kwargs)



class QueryCreateView(generics.CreateAPIView):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = []  # No authentication needed for POST requests



from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class QueryListView(generics.ListAPIView):
    pagination_class = PostPagination
    queryset = Query.objects.all().order_by('-created_at')
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'message']  # Allows search in these fields
    filterset_fields = ['done','starred']  # Allows filtering by 'done'
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Example of adding custom filters using query params
        done_param = self.request.query_params.get('done')
        if done_param is not None:
            queryset = queryset.filter(done=done_param.lower() == 'true')

        return queryset




class UpdateDeleteQueryView(generics.GenericAPIView):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser]  # Only admins can modify

    def patch(self, request, *args, **kwargs):
        query = self.get_object()  # Get the specific query instance
        update_data = request.data  # The JSON body from the request

        # Check for the 'done' field in the request and update if present
        if 'done' in update_data:
            query.done = update_data.get('done', query.done)
        if 'starred' in update_data:
            query.starred = update_data.get('starred',query.starred);

        # Add more fields here if you want to update other fields in the future

        query.save()  # Save the updated query object
        return Response({'message': 'Query updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        query = self.get_object()  # Get the specific query instance
        query.delete()  # Delete the query from the database
        return Response({'message': 'Query deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
