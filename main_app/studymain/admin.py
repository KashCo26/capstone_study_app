from django.contrib import admin
from .models import Folder, Notes, Flashcard, StudySet
# Register your models here.
admin.site.register(Folder)
admin.site.register(Notes)
admin.site.register(Flashcard)
admin.site.register(StudySet)