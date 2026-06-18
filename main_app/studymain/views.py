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
        folder_id = request.POST.get('selected_folder')
        chosen_folder = None
        if folder_id:
            chosen_folder = Folder.objects.get(id=folder_id)
        if note_name and note_text and chosen_folder:
            Notes.objects.create(name=note_name, text=note_text, folder=chosen_folder)
            return redirect('notes')
    return render(request, 'newnote.html', {'folders': folders})

def display_notes(request, folder_name):
    notes_match = None
    if folder_name:
        notes_match = Notes.objects.filter(folder__name__iexact=folder_name)
    else:
        notes_match = Notes.objects.filter(folder__name__iexact=folder_name)
        
    return render(request, 'display_notes.html', {
        'notes': notes_match,
        'searched_folder': folder_name
    })