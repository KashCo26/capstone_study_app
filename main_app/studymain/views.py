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
            return redirect('folders')
        
        elif folder_id and new_name:
            folder = get_object_or_404(Folder, id=folder_id)
            folder.name = new_name.strip()
            folder.save()
            return redirect('folders')
        
        elif deleted_folder_id:
            notes = Notes.objects.all()
            for note in notes:
                if note.folder == deleted_folder_id:
                    note.delete()
            del_folder = get_object_or_404(Folder, id=deleted_folder_id)
            del_folder.delete()
            return redirect('folders')
        
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
            return redirect('folders')
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
    
def show_note(request, note_name):
    folders = Folder.objects.all()
    note = get_object_or_404(Notes, name=note_name)
    new_name = request.POST.get('note_name')
    new_text = request.POST.get('note_text')
    new_folder_id = request.POST.get('selected_folder')
    
    if new_name and new_text and new_folder_id:
        note.name = new_name.strip()
        note.text = new_text.strip()
        note.folder = Folder.objects.get(id=new_folder_id)
        note.save()
        return redirect(f'/viewnotes/{note.folder}')
    
    return render(request, 'viewnote.html', {
        'searched_note': note_name, 
        'note_text': note.text,
        'folders': folders,
        'chosen_folder_id': note.folder.id,
        'chosen_folder_name': note.folder.name
    })
    
def quiz_options(request):
    folders = Folder.objects.all()
    notes = None
    folder_id = request.GET.get('selected_folder')
    
    if folder_id:
        notes = Notes.objects.filter(folder_id=folder_id)
    else:
        notes = Notes.objects.all()
    
    return render(request, 'choosequiz.html', {
        'folders': folders,
        'notes': notes,
    })
def new_quiz(request):
    return render(request, 'createquiz.html')