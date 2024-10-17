from django.db import models
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from django.utils.text import slugify

class Post(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    slug = models.CharField(max_length=80,blank=True, null=True) 
    

    def save(self, *args, **kwargs):
        # Only generate the slug if it's being published and there's no slug yet
        if self.is_published and not self.slug:
            
            self.slug = slugify(self.title)[:80]

        super().save(*args, **kwargs)

    def get_full_url(self):
        return f"/post/{self.slug}-{self.id}/"

    def __str__(self):
        return self.title

  


class ImageUpload(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.url

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullname = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(max_length=500, blank=True)  # Store the Firebase URL here

    def __str__(self):
        return self.user.username



class Query(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    done = models.BooleanField(default=False)
    starred = models.BooleanField(default=False)

    def __str__(self):
        return self.name


