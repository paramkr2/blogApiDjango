# blog/serializers.py
from rest_framework import serializers
from .models import Post
from .models import ImageUpload
from bs4 import BeautifulSoup

class PostSerializer(serializers.ModelSerializer):
    
    truncated_content = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_truncated_content(self, obj):
        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(obj.content, 'html.parser')

        # Remove unwanted tags (e.g., img, iframe, pre)
        for tag in soup.findAll(['img', 'iframe', 'pre']):
            tag.decompose()

        # Convert the modified soup object back to a string (preserving tags)
        cleaned_html = str(soup)  # or soup.prettify() if you want indented formatting

        # Optional: Truncate the HTML string to the desired length (e.g., 300 characters)
        return cleaned_html

    

    def get_image(self, obj):
        soup = BeautifulSoup(obj.content, 'html.parser')
        first_image = soup.find('img')  # Find the first <img> tag
        return first_image['src'] if first_image and 'src' in first_image.attrs else None  

class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['image']
