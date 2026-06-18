from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name

class Notes(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.name}, Text: {self.text:.60}..., Date Created: {str(self.created_at):.10}, Folder: {self.folder}"