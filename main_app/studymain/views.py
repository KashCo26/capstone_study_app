from django.shortcuts import render, redirect
from .models import Folder, Notes

# Create your views here.
def home_screen(request):
    return render(request, 'homescreen.html')

def study_notes(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            Folder.objects.create(name=folder_name)
            return redirect('notes')

    folders = Folder.objects.all()
    return render(request, 'notes.html', {'folders': folders})

def create_note(request):
    if request.method == 'POST':
        note_name = request.POST.get('note_name')
        if note_name:
            Notes.objects.create(name=note_name)
            return redirect('newnote')
    return render(request, 'newnote.html')