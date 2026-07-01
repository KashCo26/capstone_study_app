from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=None)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name

class Notes(models.Model):
    name = models.CharField(max_length=None)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.name}, Text: {self.text:.60}..., Date Created: {str(self.created_at):.10}, Folder: {self.folder}"

class StudySet(models.Model):
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='study_sets', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Flashcard(models.Model):
    study_set = models.ForeignKey(StudySet, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField()
    back = models.TextField()

    def __str__(self):
        return f"{self.front[:20]} (Set: {self.study_set.name})"