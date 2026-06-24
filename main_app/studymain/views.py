from django.shortcuts import render, redirect, get_object_or_404
from .models import Folder, Notes

# Create your views here.
def home_screen(request):
    return render(request, 'homescreen.html')

def study_folders(request):
    folders = Folder.objects.all()
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        folder_id = request.POST.get('folder_id')
        new_name = request.POST.get('new_folder_name')
        deleted_folder_id = request.POST.get('deleted_folder')
        
        if folder_name:
            Folder.objects.create(name=folder_name.strip())
            return redirect('notes')
        
        elif folder_id and new_name:
            folder = get_object_or_404(Folder, id=folder_id)
            folder.name = new_name.strip()
            folder.save()
            return redirect('notes')
        
        elif deleted_folder_id:
            del_folder = get_object_or_404(Folder, id=deleted_folder_id)
            del_folder.delete()
            return redirect('notes')
        
    return render(request, 'folders.html', {'folders': folders})

def create_note(request):
    folders = Folder.objects.all()
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
        
    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        new_name = request.POST.get('new_note_name')
        deleted_note_id = request.POST.get('deleted_note')
        
        if note_id and new_name:
            note = get_object_or_404(Notes, id=note_id)
            note.name = new_name.strip()
            note.save()
            return redirect(f'/viewnotes/{folder_name}/')
        
        elif deleted_note_id:
            del_note = get_object_or_404(Notes, id=deleted_note_id)
            del_note.delete()
            return redirect(f'/viewnotes/{folder_name}/')
        
    return render(request, 'display_notes.html', {
        'notes': notes_match,
        'searched_folder': folder_name
    })