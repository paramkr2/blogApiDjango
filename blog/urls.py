from django.urls import path 
from .views import PostListCreateView, PostDetailView , PostDraftView , PostPublishView 

urlpatterns = [
	path('posts/', PostListCreateView.as_view(), name='post-list-create' ),
	path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
	path('posts/<pk>/drafts/', PostDraftView.as_view(), name="post-draft"),
	path('posts/<pk>/publish/',PostPublishView.as_view(),name="post-publish")
]


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # For logging in and obtaining JWT token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # For refreshing the JWT token
]



from .views import ImageUploadView , FirebaseImageUploadView

urlpatterns += [
    path('images/', ImageUploadView.as_view(), name='image-upload'),
    path('firebase/images/',FirebaseImageUploadView.as_view(),name='firebaseImage-upload'),
]


