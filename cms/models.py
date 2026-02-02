from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
# Create your models here.
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the blog category")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    
    
class Blog(models.Model):
    title = models.CharField(max_length=255, help_text="Enter the Title of the blog")
    sub_title = models.CharField(max_length=255,  null=True, blank=True, help_text="Enter the Sub-title of the blog")
    author = models.CharField(max_length=255, help_text="Author of the blog",null=True,blank=True)
    category = models.ForeignKey('BlogCategory', on_delete=models.SET_NULL, null=True, blank=True, help_text="Category of the blog")
    tags = models.TextField(null=True, blank=True, help_text="Comma-separated tags")
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True, help_text="Upload a cover image")
    description = models.TextField(help_text="Enter the blog Description", null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Is the blog active?")
    send_as_newsletter = models.BooleanField(default=False, help_text="Send this blog as a newsletter?")
   

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        # reverse() returns a relative URL, so we prepend the domain
        relative_url = reverse('blog-detail', kwargs={'slug': self.slug})
        return f"{settings.SITE_URL.rstrip('/')}{relative_url}"
    
    
class ContactUs(models.Model):
   
    name = models.CharField(max_length=100)
    
    message = models.TextField(blank=True, null=True)
    subject =models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name}"

class Newsletters(models.Model):
   
    subject_header = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notification_templates', blank=True)
    is_active = models.BooleanField(default=True)
  



class NowKnowIt(models.Model):
    common_nepali_english=models.CharField(max_length=255)
    natural_english=models.CharField(max_length=255)
    reason=models.TextField()
    is_active=models.BooleanField(default=True)
    used_status=models.BooleanField(default=False)
    forced_publish = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.common_nepali_english
    
    
    
class Videos(models.Model):
    video = models.FileField(upload_to='videos/')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class ExpandVocab(models.Model):
  
    word=models.CharField(max_length=255)
    answer=models.CharField(max_length=255)
    is_active=models.BooleanField(default=False)
    grade=models.CharField(max_length=255)
    is_active=models.BooleanField(default=True)
    used_status=models.BooleanField(default=False)
    forced_publish = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word