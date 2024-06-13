# myapp/models.py

from django.db import models

class Post(models.Model):
    content = models.TextField()
    category = models.IntegerField()

    def __str__(self):
        return self.content
