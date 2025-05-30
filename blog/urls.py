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


from .views import ProfileDetailUpdateView

urlpatterns += [
    path('profile/', ProfileDetailUpdateView.as_view(), name='profile-detail-update'),
    path('profile/<str:user_identifier>/', ProfileDetailUpdateView.as_view(), name='profile-detail-update-by-identifier'),
]


from .views import QueryCreateView, QueryListView,UpdateDeleteQueryView

urlpatterns  += [
    path('contact-us/', QueryCreateView.as_view(), name='contact-us'),
    path('queries/', QueryListView.as_view(), name='queries'),
    path('queries/<int:pk>/', UpdateDeleteQueryView.as_view(), name='update-done-status'),
]

