from django.urls import path
from . import views

# Define a list of url patterns
urlpatterns = [
    path('', views.home_screen, name='home'),
    path('folders/', views.study_folders, name='folders'),
    path('newnote/', views.create_note, name='newnote'),
    path('viewnotes/<str:folder_name>/', views.display_notes, name='viewnotes'),
    path('notecontent/<str:note_name>/', views.show_note, name='notecontent')
]