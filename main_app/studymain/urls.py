from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Define a list of url patterns
urlpatterns = [
    path('', views.home_screen, name='home'),
    path('folders/', views.study_folders, name='folders'),
    path('newnote/', views.create_note, name='newnote'),
    path('viewnotes/<str:folder_name>/', views.display_notes, name='viewnotes'),
    path('notecontent/<str:note_name>/', views.show_note, name='notecontent'),
    path('quizselect/', views.quiz_options, name='quizselect'),
    path('takelesson/', views.generate_quiz_session, name='takelesson'),
    path('createquiz/', views.new_quiz, name='createquiz'),
    path('viewquizzes/', views.see_quiz, name='viewquizzes'),
    path('editquiz/<str:quiz_id>/', views.quiz_edit, name='editquiz'),
    path('takequiz/<str:set_id>/', views.take_quiz_view, name='takequiz'),
    path('flashcard_summary/<str:set_id>/', views.flashcard_summary_view, name='flashcard-summary'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('settings/', views.settings_view, name='settings'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', views.password_reset_view, name='password_reset')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)