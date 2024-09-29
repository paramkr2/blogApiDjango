from PIL import Image
import io

def resize_image(image, max_width=200):
    # Open the image using PIL
    img = Image.open(image)
    img.thumbnail((max_width, max_width))
    
    # Save the resized image to a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=85)
    img_io.seek(0)
    
    return img_io
