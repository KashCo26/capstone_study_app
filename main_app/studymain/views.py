from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
import base64
from django.core.files.base import ContentFile
from httpx import request
from .models import Folder, Notes, Flashcard, StudySet
import json
from openai import OpenAI
import random
from django.core.mail import send_mail

# Create your views here.
# @login_required
def settings_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            cropped_data = request.POST.get('cropped_avatar_data', '')

            if username and email:
                request.user.username = username
                request.user.email = email
                request.user.save()

                if cropped_data.startswith('data:image'):
                    img_format, imgstr = cropped_data.split(';base64,')
                    ext = img_format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f"{request.user.username}_avatar.{ext}")
                    
                    profile = request.user.profile
                    profile.image = data
                    profile.save()

                messages.success(request, 'Profile details and email updated successfully!')
            else:
                messages.error(request, 'Username and Email fields cannot be blank.')

        elif action == 'update_password':
            old_pass = request.POST.get('old_password', '')
            new_pass1 = request.POST.get('new_password1', '')
            new_pass2 = request.POST.get('new_password2', '')

            if not request.user.check_password(old_pass):
                messages.error(request, 'Your current password choice was entered incorrectly.')
            elif new_pass1 != new_pass2:
                messages.error(request, 'The new passwords do not match.')
            else:
                request.user.set_password(new_pass1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Your password security profile keys have been updated successfully!')
                
        elif action == 'delete_account':
            all_notes = Notes.objects.filter(user=request.user)
            all_folders = Folder.objects.filter(user=request.user)
            all_study_sets = StudySet.objects.filter(user=request.user)
            all_flashcards = Flashcard.objects.filter(user=request.user)
            
            all_notes.delete()
            all_folders.delete()
            all_study_sets.delete()
            all_flashcards.delete()
            request.user.delete()
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')

        return redirect('settings')

    return render(request, 'settings.html')

def password_reset_view(request):
    verification_code = str(random.randint(100000, 900000))

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send_code':
            try:
                email = request.POST.get('email')                
                subject = 'Your StudyApp Password Reset Code'
                message = f'Hello,\n\nYour security verification code is: {verification_code}\n\nIf you did not request this, please ignore this email.'
                from_email = 'kashco26@gmail.com'
                recipient_list = [email]
                
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                )
                
                return render(request, 'registration/password_reset.html', {'verification_code': verification_code})
            
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to send code: {str(e)}'})
        
        elif action == 'reset':
            entered_code = request.POST.get('entered_code')
            if entered_code == verification_code:
                email = request.POST.get('email')
                new_password = request.POST.get('new_password')
                
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
                    return redirect('login')
                except User.DoesNotExist:
                    messages.error(request, 'No account found with that email address.')
    

    return render(request, 'registration/password_reset.html', {'verification_code': verification_code})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
            return redirect('register')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        messages.success(request, 'Account created successfully! You can now log in.')
        return redirect('login')

    return render(request, 'registration/register.html')

# @login_required
def home_screen(request):
    return render(request, 'mobile/homescreen.html')

# @login_required
def study_folders(request):
    request.user = User.objects.get(username='kashvig')
    folders = Folder.objects.filter(user=request.user).order_by('-created_at').prefetch_related('notes')
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        folder_id = request.POST.get('folder_id')
        new_name = request.POST.get('new_folder_name')
        deleted_folder_id = request.POST.get('deleted_folder')
        
        if folder_name:
            Folder.objects.create(name=folder_name.strip(), user=request.user)
            return redirect('folders')
        
        elif folder_id and new_name:
            folder = get_object_or_404(Folder, id=folder_id, user=request.user)
            folder.name = new_name.strip()
            folder.save()
            return redirect('folders')
        
        elif deleted_folder_id:
            notes = Notes.objects.filter(user=request.user)
            for note in notes:
                if note.folder == deleted_folder_id:
                    note.delete()
            del_folder = get_object_or_404(Folder, id=deleted_folder_id, user=request.user)
            del_folder.delete()
            return redirect('folders')
        
    return render(request, 'mobile/folders.html', {'folders': folders})

# @login_required
def create_note(request):
    request.user = User.objects.get(username='kashvig')
    folders = Folder.objects.filter(user=request.user)
    if request.method == 'POST':
        note_name = request.POST.get('note_name')
        note_text = request.POST.get('note_text')
        folder_id = request.POST.get('selected_folder')
        chosen_folder = None
        if folder_id:
            chosen_folder = Folder.objects.get(id=folder_id)
        if note_name and note_text and chosen_folder:
            Notes.objects.create(name=note_name, text=note_text, folder=chosen_folder, user=request.user)
            return redirect(f'/viewnotes/{chosen_folder.name}')
    return render(request, 'mobile/newnote.html', {'folders': folders})

# @login_required
def display_notes(request, folder_name):
    request.user = User.objects.get(username='kashvig')
    notes_match = None
    
    if folder_name:
        notes_match = Notes.objects.filter(folder__name__iexact=folder_name, user=request.user).order_by('-created_at')
    else:
        notes_match = Notes.objects.filter(folder__name__iexact=folder_name, user=request.user).order_by('-created_at')
    
    num_notes = len(notes_match)
        
    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        new_name = request.POST.get('new_note_name')
        deleted_note_id = request.POST.get('deleted_note')
        
        if note_id and new_name:
            note = get_object_or_404(Notes, id=note_id, user=request.user)
            note.name = new_name.strip()
            note.save()
            return redirect(f'/viewnotes/{folder_name}/')
        
        elif deleted_note_id:
            del_note = get_object_or_404(Notes, id=deleted_note_id, user=request.user)
            del_note.delete()
            return redirect(f'/viewnotes/{folder_name}/')
        
    return render(request, 'mobile/display_notes.html', {
        'notes': notes_match,
        'searched_folder': folder_name,
        'num_notes': num_notes
    })
    
# @login_required
def show_note(request, note_name):
    request.user = User.objects.get(username='kashvig')
    folders = Folder.objects.filter(user=request.user)
    note = get_object_or_404(Notes, name=note_name, user=request.user)
    new_name = request.POST.get('note_name')
    new_text = request.POST.get('note_text')
    new_folder_id = request.POST.get('selected_folder')
    
    if new_name and new_text and new_folder_id:
        note.name = new_name.strip()
        note.text = new_text.strip()
        note.folder = Folder.objects.get(id=new_folder_id)
        note.save()
        return redirect(f'/viewnotes/{note.folder}')
    
    return render(request, 'mobile/viewnote.html', {
        'searched_note': note_name, 
        'note_text': note.text,
        'folders': folders,
        'chosen_folder_id': note.folder.id,
        'chosen_folder_name': note.folder.name
    })
    
# @login_required
def quiz_options(request):
    #if folders is on mobile then do the line below else remove prefetch related and keep the ifs
    folders = Folder.objects.filter(user=request.user).prefetch_related('notes')
    notes = None
    folder_id = request.GET.get('selected_folder')
    
    if folder_id:
        notes = Notes.objects.filter(folder_id=folder_id, user=request.user)
    else:
        notes = Notes.objects.filter(user=request.user)
    
    return render(request, 'mobile/choosequiz.html', {
        'folders': folders,
        'notes': notes,
    })

# @login_required  
def generate_quiz_session(request):
    if request.method != 'POST':
        return redirect('quiz_options')
        
    selected_format = request.POST.get('selected_format')
    time_chosen = request.POST.get('time-chosen')
    selected_note_ids = request.POST.getlist('selected_notes') 
    
    if not selected_note_ids:
        return redirect('quiz_options')

    selected_notes_records = Notes.objects.filter(id__in=selected_note_ids, user=request.user)
    combined_notes_text = ""
    for note in selected_notes_records:
        combined_notes_text += f"\n--- Section: {note.name} ---\n{note.text}\n"

    if selected_format == 'all':
        format_instruction = "mix of True or False, Multiple Choice, Select all that Apply, and Written Responses"
    elif selected_format == 'true-false':
        format_instruction = "Strictly True or False"
    elif selected_format == 'mcq':
        format_instruction = "Strictly Multiple Choice (single answer)"
    elif selected_format == 'allthatapply':
        format_instruction = "Strictly Select all that Apply (checkboxes with multiple true options)"
    elif selected_format == 'written':
        format_instruction = "Strictly Written Short Answers"
    else:
        format_instruction = "General Review Questions"

    client = OpenAI()
    
    quiz_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "cards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string", 
                            "enum": ["true-false", "mcq", "allthatapply", "written"],
                            "description": "Categorize the structured type of question."
                        },
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of options for mcq, true-false, or allthatapply. Leave empty for written."
                        },
                        "answer": {
                            "type": "string",
                            "description": "For true-false/mcq: matching string. For allthatapply: comma-separated true options. For written: model answer string."
                        }
                    },
                    "required": ["type", "question", "options", "answer"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["title", "cards"],
        "additionalProperties": False
    }

    generated_cards = []
    quiz_title = "AI Study Session"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional teacher's assistant. Build structured quiz items conforming to the targeted parameters."
                },
                {
                    "role": "user", 
                    "content": (
                        f"Generate dynamic flashcard test items matching a {time_chosen} minute study load in the layout format of: {format_instruction}.\n"
                        f"Notes material:\n{combined_notes_text}\n\n"
                        f"CRITICAL RULES:\n"
                        f"1. For 'allthatapply', include multiple valid options in the options array, and make the 'answer' field a clean comma-separated string of all correct values.\n"
                        f"2. For 'mcq', provide 1 correct answer and 3 distinct distractors in the options array.\n"
                        f"3. For 'true-false', options must strictly be ['True', 'False']."
                    )
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "quiz_generation_schema",
                    "strict": True,
                    "schema": quiz_schema
                }
            }
        )
        
        import json
        ai_payload = json.loads(response.choices[0].message.content)
        quiz_title = ai_payload.get('title', 'AI Study Session')
        generated_cards = ai_payload.get('cards', [])

    except Exception as e:
        print(f"Failed to generate quiz: {e}")
    
    return render(request, 'active_quiz_session.html', {
        'title': quiz_title,
        'quiz_cards': generated_cards,
        'duration': time_chosen
    })
    

# @login_required
def new_quiz(request):
    folders = Folder.objects.filter(user=request.user)
    notes = None
    folder_id = request.GET.get('folder_label')
    
    if request.method == 'POST':
        set_name = request.POST.get('set_name', 'Untitled Set')
        questions = request.POST.getlist('question[]')
        answers = request.POST.getlist('answer[]')
        action = request.POST.get('action')
        note_id = request.POST.get('note_source')
    
        client = OpenAI()
        if action == 'generate_ai':
            prompt_material = ""
            
            if note_id:
                selected_note = get_object_or_404(Notes, id=note_id, user=request.user)
                prompt_material = f"Generate questions based strictly on these notes:\n{selected_note.text}"
            else:
                prompt_material = f"Generate broad foundational quiz questions regarding this general topic: '{set_name}'"
            
            quiz_schema = {
                "type": "object",
                "properties": {
                    "cards": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "answer": {"type": "string"}
                            },
                            "required": ["question", "answer"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["cards"],
                "additionalProperties": False
            }
            
            try:
                response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a professional teacher assistant compiling study flashcard decks."},
                            {"role": "user", "content": f"{prompt_material}\nGenerate exactly 5 comprehensive matching card items containing clear questions and concise answers."}
                        ],
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": "quiz_set_generation",
                                "strict": True,
                                "schema": quiz_schema
                            }
                        }
                )
                ai_data = json.loads(response.choices[0].message.content)
                generated_cards = ai_data.get('cards', [])
                print(generated_cards)
                
                return render(request, 'createquiz.html', {
                    'folders': folders,
                    'prefilled_name': set_name,
                    'prefilled_cards': generated_cards
                })
            
            except Exception as e:
                print(f"AI Generation failed: {e}")
                    
        
        if folder_id:
            notes = Notes.objects.filter(folder_id=folder_id, user=request.user)
        else:
            notes = Notes.objects.filter(user=request.user)
        
        if set_name and questions and answers:    
            study_set = StudySet.objects.create(
                    name=set_name.strip(), user=request.user
            )
                
            flashcards_to_create = []
            for q_text, a_text in zip(questions, answers):
                if q_text.strip() and a_text.strip():
                    flashcards_to_create.append(
                        Flashcard(
                            study_set=study_set,
                            front=q_text.strip(),
                            back=a_text.strip(),
                            user=request.user
                        )
                    )
                
            if flashcards_to_create:
                Flashcard.objects.bulk_create(flashcards_to_create)
                    
                return redirect('viewquizzes')
                
    
    return render(request, 'createquiz.html', {
        'folders': folders,
        'notes': notes
        })

# @login_required
def see_quiz(request):
    study_sets = StudySet.objects.filter(user=request.user).order_by('-created_at').prefetch_related('cards')
    return render(request, 'viewquizzes.html', {'study_sets': study_sets})

# @login_required
def quiz_edit(request, quiz_id):
    study_set = get_object_or_404(StudySet, id=quiz_id, user=request.user)
    saved_card_ids = []
    flashcards_to_create = []
        
    if request.method == 'POST':
        new_name = request.POST.get('set_name')
        form_ids = request.POST.getlist('card_id[]')
        new_questions = request.POST.getlist('question[]')
        new_answers = request.POST.getlist('answer[]')
        action = request.POST.get('action')
        
        if new_name:
            study_set.name = new_name.strip()
    
        if action == 'generate_ai':
            cards_list = []
            for c_id, q_text, a_text in zip(form_ids, new_questions, new_answers):
                cards_list.append(
                    Flashcard(
                        id=int(c_id) if c_id is not None else None,
                        front=q_text,
                        back=a_text,
                        study_set=study_set,
                        user=request.user
                    )
                )

            client = OpenAI()
            prompt_material = f"Generate broad foundational quiz questions regarding this general topic: '{study_set.name}'"
            
            quiz_schema = {
                "type": "object",
                "properties": {
                    "cards": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "answer": {"type": "string"}
                            },
                            "required": ["question", "answer"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["cards"],
                "additionalProperties": False
            }
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional teacher assistant compiling study flashcard decks."},
                        {"role": "user", "content": f"{prompt_material}\nGenerate exactly 5 comprehensive matching card items containing clear questions and concise answers."}
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "quiz_set_generation",
                            "strict": True,
                            "schema": quiz_schema
                        }
                    }
                )
                ai_data = json.loads(response.choices[0].message.content)
                generated_cards = ai_data.get('cards', [])
                
                for item in generated_cards:
                    q_text = item.get('question', '').strip()
                    a_text = item.get('answer', '').strip()
                    if q_text and a_text:
                        cards_list.append(
                            Flashcard(
                                study_set=study_set,
                                front=q_text,
                                back=a_text,
                                user=request.user
                            )
                        )
                
            except Exception as e:
                print(f"AI Generation failed: {e}")
            
            return render(request, 'editquiz.html', {
                'study_set': study_set,
                'cards': cards_list
            })
            
        elif action == 'delete_set': 
            cards = study_set.cards.all()
            for card in cards:
                card.delete()
            study_set.delete()
            
            return redirect('viewquizzes')
        
        else:
            if new_name:
                study_set.save()
                
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
                                    back=a_clean,
                                    user=request.user
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

# @login_required
def take_quiz_view(request, set_id):
    client = OpenAI() 
    
    study_set = get_object_or_404(StudySet, id=set_id, user=request.user)
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
        
    return render(request, 'practice_cards.html', {'cards': processed_cards, 'set_id': set_id})

# @login_required
def flashcard_summary_view(request, set_id):
    study_set = get_object_or_404(StudySet, id=set_id, user=request.user)
    cards = study_set.cards.all()
    
    raw_correct = request.GET.get('correct', 0)
    raw_wrong = request.GET.get('wrong', 0)

    if '${' in raw_correct or not raw_correct.isdigit():
        raw_correct = 0
    if '${' in raw_wrong or not raw_wrong.isdigit():
        raw_wrong = 0
        
    total_correct = int(raw_correct)
    total_wrong = int(raw_wrong)
    
    total_questions = total_correct + total_wrong
    if total_questions > 0:
        average_score = round((total_correct / total_questions) * 100)
    else:
        average_score = 0

    context = {
        'total_correct': total_correct,
        'total_wrong': total_wrong,
        'average_score': average_score, 
    }

    return render(request, 'flashcard_summary.html', {
        'study_set': study_set,
        'cards': cards,
        'context': context
    })
