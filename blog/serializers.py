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

        # Remove unwanted tags (e.g., image, iframe, codeblock)
        for tag in soup.findAll(['img', 'iframe', 'pre']):
            tag.decompose()

        # Extract the text, preserving newlines
        cleaned_text = soup.get_text(separator='\n', strip=True)

        # Truncate the text to the desired length
        return cleaned_text  # Adjust the length as needed

    def get_image(self, obj):
        soup = BeautifulSoup(obj.content, 'html.parser')
        first_image = soup.find('img')  # Find the first <img> tag
        return first_image['src'] if first_image and 'src' in first_image.attrs else None  

class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['image']
