from rest_framework import generics, status 
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly , IsAuthenticated
from .models import Post
from .serializers import PostSerializer
from .pagination import PostPagination


class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = PostPagination

    
    def get_queryset(self):
        user = self.request.user
        post_type = self.request.query_params.get('type')  # Get 'type' query param
        queryset = Post.objects.none()  # Start with an empty queryset

        if post_type == 'draft':
            if user.is_authenticated:
                # Return only user's drafts
                queryset = Post.objects.filter(author=user, is_published=False).order_by('-created_at')
        elif post_type == 'published':
            if user.is_authenticated:
                # Return all published posts, including user's drafts
                queryset = Post.objects.filter(is_published=True).order_by('-created_at')
            else:
                # Return only published posts for non-authenticated users
                queryset = Post.objects.filter(is_published=True).order_by('-created_at')
        else:
            if user.is_authenticated:
                # Return both published posts and user's drafts
                queryset = Post.objects.filter(author=user).order_by('-created_at') 
            else:
                # Return only published posts for unauthenticated users
                queryset = Post.objects.filter(is_published=True).order_by('-created_at')

        return queryset
        
    def create(self, request, *args, **kwargs):
        data = request.data.copy()  # Copy the request data to modify it
        data['author'] = request.user.pk  # Set the author field to the logged-in user's ID
        print(self.request.user.pk)  # Debugging print statement to check user ID
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

import requests

class ImgurUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')

        # Get access token from Imgur (OAuth2 Client Credentials Flow)
        auth_response = requests.post('https://api.imgur.com/oauth2/token', data={
            'client_id': '8713ed59d0f26e1',
            'client_secret': '666ab954388b03d7f99e132f314ed4aac683b348',
            'grant_type': 'client_credentials',
        })

        if auth_response.status_code != 200:
            return Response({'error': 'Imgur authentication failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = auth_response.json().get('access_token')

        # Upload image to Imgur
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        files = {
            'image': image,
        }
        upload_response = requests.post('https://api.imgur.com/3/image', headers=headers, files=files)

        if upload_response.status_code != 200:
            return Response({'error': 'Image upload failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        imgur_data = upload_response.json()['data']
        image_url = imgur_data['link']
        print('In imgur upload view',image_url)

        # Return the image URL to the frontend
        return Response({'image': image_url}, status=status.HTTP_201_CREATED)
