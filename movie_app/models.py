from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)