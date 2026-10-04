from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Author(models.Model):
    first_name= models.CharField(max_length=100)
    last_name= models.CharField(max_length=100)
    bio= models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('Blog_ui:author-detail', args=[str(self.id)])


class Post(models.Model):
    title=models.CharField(max_length=200)
    author=models.ForeignKey(Author,on_delete=models.CASCADE,related_name='posts')
    created_at=models.DateTimeField(default=timezone.now)
    content=models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('Blog_ui:post-detail', args=[str(self.id)])

class Comment(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    description=models.TextField(max_length=1000)
    
    created_at=models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.description[:75] 
    
     # Return the first 75 characters of the comment

