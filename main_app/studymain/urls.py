from django.urls import path
from . import views

# Define a list of url patterns
urlpatterns = [
    path('', views.home_screen, name='home'),
    path('notes/', views.study_notes, name='notes'),
    path('newnote/', views.create_note, name='newnote')
]