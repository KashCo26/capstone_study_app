from django.shortcuts import render, redirect
from .models import Folder, Notes

folders = Folder.objects.all()

# Create your views here.
def home_screen(request):
    return render(request, 'homescreen.html')

def study_notes(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            Folder.objects.create(name=folder_name)
            return redirect('notes')

    return render(request, 'notes.html', {'folders': folders})

def create_note(request):
    if request.method == 'POST':
        note_name = request.POST.get('note_name')
        note_text = request.POST.get('note_text')
        if note_name and note_text:
            Notes.objects.create(name=note_name, text=note_text)
            return redirect('notes')
    return render(request, 'newnote.html', {'folders': folders})