import string 
import random
import sys
from io import BytesIO
from PIL import Image
from slugify import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile


def random_string_generator(size = 10, chars = string.ascii_lowercase + string.digits): 
	return ''.join(random.choice(chars) for _ in range(size)) 

def unique_slug_generator(instance, new_slug = None): 
	if new_slug is not None: 
		slug = new_slug 
	else: 
		slug = slugify(instance.title) 
	Klass = instance.__class__ 
	qs_exists = Klass.objects.filter(slug = slug).exists() 
	
	if qs_exists: 
		new_slug = "{slug}-{randstr}".format( 
			slug = slug, randstr = random_string_generator(size = 8)) 
			
		return unique_slug_generator(instance, new_slug = new_slug) 
	return slug


def compress_image(uploaded_image):
	image_temproary = Image.open(uploaded_image)
	outputIOStream = BytesIO()
	rgb_img = image_temproary.convert('RGB')
	# Resize/modify the image
	rgb_img = rgb_img.resize((400, 400))
	rgb_img.save(outputIOStream , format='JPEG', quality=40, optimize=True)
	outputIOStream.seek(0)
	uploadedImage = InMemoryUploadedFile(outputIOStream, 'ImageField', "%s.jpg" % uploaded_image.name.split('.')[0],
										 'image/jpeg', sys.getsizeof(outputIOStream), None)
	return uploadedImage