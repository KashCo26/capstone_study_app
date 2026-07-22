from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Folder(models.Model):
    name = models.CharField(max_length=None)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders', null=True, blank=True)
        
    def __str__(self):
        return self.name

class Notes(models.Model):
    name = models.CharField(max_length=None)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    def __str__(self):
        return f"{self.name}, Text: {self.text:.60}..., Date Created: {str(self.created_at):.10}, Folder: {self.folder}"

class StudySet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sets', null=True, blank=True)
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='study_sets', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Flashcard', null=True, blank=True)
    study_set = models.ForeignKey(StudySet, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField()
    back = models.TextField()

    def __str__(self):
        return f"{self.front[:20]} (Set: {self.study_set.name})"
    
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)