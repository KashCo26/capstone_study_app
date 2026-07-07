from django.shortcuts import render, redirect, get_object_or_404
from .models import Folder, Notes, Flashcard, StudySet

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
    folders = Folder.objects.all()
    notes = None
    folder_id = request.GET.get('folder_label')
    
    if folder_id:
        notes = Notes.objects.filter(folder_id=folder_id)
    else:
        notes = Notes.objects.all()
        
    set_name = request.POST.get('set_name')
    questions = request.POST.getlist('question[]')
    answers = request.POST.getlist('answer[]')
    
    if set_name and questions and answers:    
        study_set = StudySet.objects.create(
                name=set_name.strip()
                # folder=some_folder_object (optional: link to a folder if selected)
            )
            
        flashcards_to_create = []
        for q_text, a_text in zip(questions, answers):
            if q_text.strip() and a_text.strip():
                flashcards_to_create.append(
                    Flashcard(
                        study_set=study_set,
                        front=q_text.strip(),
                        back=a_text.strip()
                    )
                )
            
        if flashcards_to_create:
            Flashcard.objects.bulk_create(flashcards_to_create)
                
            return redirect('viewquizzes')
    
    return render(request, 'createquiz.html', {
        'folders': folders,
        'notes': notes,
    })

def see_quiz(request):
    study_sets = StudySet.objects.all().order_by('-created_at').prefetch_related('cards')
    return render(request, 'viewquizzes.html', {'study_sets': study_sets})

def quiz_edit(request, quiz_id):
    study_set = get_object_or_404(StudySet, id=quiz_id)
        
    if request.method == 'POST':
        new_name = request.POST.get('set_name')
        form_ids = request.POST.getlist('card_id[]')
        new_questions = request.POST.getlist('question[]')
        new_answers = request.POST.getlist('answer[]')
        
        if new_name:
            study_set.name = new_name.strip()
            study_set.save()
            
            saved_card_ids = []
            flashcards_to_create = []
            
            for c_id, q_text, a_text in zip(form_ids, new_questions, new_answers):
                q_clean = q_text.strip()
                a_clean = a_text.strip()
                
                if q_clean and a_clean:
                    if c_id:
                        Flashcard.objects.filter(id=c_id, study_set=study_set).update(
                            front=q_clean,
                            back=a_clean
                        )
                        saved_card_ids.append(int(c_id))
                    else:
                        flashcards_to_create.append(
                            Flashcard(
                                study_set=study_set,
                                front=q_clean,
                                back=a_clean
                            )
                        )
            
            if flashcards_to_create:
                new_cards = Flashcard.objects.bulk_create(flashcards_to_create)
                saved_card_ids.extend([card.id for card in new_cards])
            
            study_set.cards.exclude(id__in=saved_card_ids).delete()
            
            return redirect('viewquizzes')
            
    cards = study_set.cards.all()
    return render(request, 'editquiz.html', {
        'study_set': study_set,
        'cards': cards
    })

import json
from openai import OpenAI

def take_quiz_view(request, set_id):
    client = OpenAI() 
    
    study_set = get_object_or_404(StudySet, id=set_id)
    raw_cards = study_set.cards.all()
    
    cards_input_data = []
    for card in raw_cards:
        cards_input_data.append({
            "id": str(card.id),
            "question": card.front,
            "answer": card.back
        })

    openai_bulk_schema = {
        "type": "object",
        "properties": {
            "quiz_cards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "distractors": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["id", "distractors"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["quiz_cards"],
        "additionalProperties": False
    }

    processed_cards = []
    ai_distractors_map = {}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a quiz generator. Here is a list of flashcards in JSON format:\n"
                        f"{json.dumps(cards_input_data)}\n\n"
                        f"For each card object in the array, look at its 'question' and 'answer' properties. "
                        f"Generate exactly 3 plausible but incorrect multiple-choice options (distractors). "
                        f"Return a mapped JSON response linking each card's 'id' to its generated 'distractors'."
                    )
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "quiz_generation_schema",
                    "strict": True,
                    "schema": openai_bulk_schema
                }
            },
            temperature=0.7
        )
        
        ai_data = json.loads(response.choices[0].message.content)
        for item in ai_data.get('quiz_cards', []):
            item_id = item.get('id')
            ai_distractors_map[str(item_id)] = item.get('distractors', [])
            ai_distractors_map[int(item_id)] = item.get('distractors', [])

    except Exception as e:
        print(f"🚨 Bulk OpenAI API Failure: {e}")

    for card in raw_cards:
        distractors_list = ai_distractors_map.get(str(card.id)) or ai_distractors_map.get(card.id)
        
        if not distractors_list:
            distractors_list = [
                f"Fallback option A for: {card.front[:20]}...",
                f"Fallback option B for: {card.front[:20]}...",
                f"Fallback option C for: {card.front[:20]}..."
            ]
            
        processed_cards.append({
            'id': card.id,
            'front': card.front,
            'back': card.back,
            'ai_distractors': distractors_list[:3]
        })
        
    return render(request, 'practice_cards.html', {'cards': processed_cards})
