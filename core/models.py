# in core/models.py
from django.db import models
from django.urls import reverse


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="A short label for the URL, e.g., 'about-us'")
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'
