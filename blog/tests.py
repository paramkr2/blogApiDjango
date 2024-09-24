from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Post, ImageUpload
import tempfile

class PostIntegrationTests(APITestCase):

    def setUp(self):
        # Set up a user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()


    def test_create_post_as_authenticated_user(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Create a post
        url = reverse('post-list-create')
        data = {
            'title': 'Test Post',
            'content': 'This is a test post content',
            'is_published': True
        }
        response = self.client.post(url, data, format='json')
        
        # Assert that the post was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    

    def test_create_post_as_anonymous_user(self):
        # Try to create a post without authentication
        url = reverse('post-list-create')
        data = {
            'title': 'Anonymous Post',
            'content': 'Anonymous content'
        }
        response = self.client.post(url, data, format='json')
        
        # Assert that the post was not created and returns unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_publish_post(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        post = Post.objects.create(author=self.user, content='<h1> testing </h1> <p> something</p>', is_published=False)
        
        url = reverse('post-publish', kwargs={'pk': post.pk})
        response = self.client.put(url)
    
        # Assert that the post was published successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertTrue(post.is_published)

    def test_list_posts(self):
        # Create some posts
        Post.objects.create(author=self.user, content='Published Post 1', is_published=True)
        Post.objects.create(author=self.user, content='Draft Post 1', is_published=False)

        # Request the list of published posts
        url = reverse('post-list-create') + '?type=published'
        response = self.client.get(url)

        # Assert that only published posts are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

