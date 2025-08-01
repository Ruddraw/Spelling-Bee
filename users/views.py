from django.http import JsonResponse
from django.utils import timezone  
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm
from .models import PracticeSession, Word, WordAttempt
import random

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Error creating account. Please check the form.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def practice(request):
    word = Word.objects.order_by('?').first()
    if not word:
        messages.error(request, "No words available.")
        return redirect('home')
    return render(request, 'users/practice.html', {'word': word})

@login_required
def spelling_practice(request):
    # Restart logic
    if 'restart_session' in request.GET:
        if 'practice_session_id' in request.session:
            try:
                session = PracticeSession.objects.get(
                    id=request.session['practice_session_id'],
                    user=request.user,
                    end_time__isnull=True
                )
                session.end_time = timezone.now()
                session.duration = session.end_time - session.start_time
                session.save()
            except PracticeSession.DoesNotExist:
                pass
            del request.session['practice_session_id']
        return redirect('spelling_practice')

    # Create or get session
    session = None
    elapsed_time = 0
    session_active = False
    if 'practice_session_id' in request.session:
        try:
            session = PracticeSession.objects.get(
                id=request.session['practice_session_id'],
                user=request.user,
                end_time__isnull=True
            )
            elapsed_time = (timezone.now() - session.start_time).total_seconds()
            session_active = True
        except PracticeSession.DoesNotExist:
            del request.session['practice_session_id']  # Clean up invalid session

    if request.method == 'POST':
        if not session_active:
            messages.error(request, "Start a session before submitting.")
            return redirect('spelling_practice')
        user_input = request.POST.get('user_input', '').strip().lower()
        correct_word_id = request.session.get('current_word_id')
        if correct_word_id:
            try:
                word = Word.objects.get(id=correct_word_id)
                is_correct = user_input == word.word.lower()
                WordAttempt.objects.create(
                    session=session,
                    word=word,
                    user_input=user_input,
                    is_correct=is_correct
                )
                if is_correct:
                    messages.success(request, "Correct!")
                else:
                    messages.error(request, f"Incorrect. The correct spelling is {word.word}.")
            except Word.DoesNotExist:
                messages.error(request, "Word not found. Please try again.")
        else:
            messages.error(request, "No word selected. Please refresh the page.")
        # Clear the current word ID to force a new word on redirect
        if 'current_word_id' in request.session:
            del request.session['current_word_id']
        return redirect('spelling_practice')

    # In GET: Only pick word if session active
    if session_active:
        word = Word.objects.order_by('?').first()
        if not word:
            messages.error(request, "No words available.")
            return redirect('home')
        request.session['current_word_id'] = word.id
    else:
        word = None  # No word until session starts

    # In context: Pass word only if active
    return render(request, 'users/spelling_practice.html', {
        'word': word,
        'elapsed_time': elapsed_time,
        'session_active': session_active,
        'word_json': word.to_json() if word else '{}',
    })

@login_required
def start_session(request):
    if request.method == 'POST':
        if 'practice_session_id' not in request.session:
            session = PracticeSession.objects.create(user=request.user)
            request.session['practice_session_id'] = session.id
            return JsonResponse({
                'status': 'success',
                'start_time': session.start_time.isoformat(),
                'message': 'Session started!'
            })
        return JsonResponse({'status': 'error', 'message': 'Session already active'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def end_session(request):
    if request.method == 'POST':  # Change to only accept POST requests
        if 'practice_session_id' in request.session:
            try:
                session = PracticeSession.objects.get(
                    id=request.session['practice_session_id'],
                    user=request.user,
                    end_time__isnull=True
                )
                session.end_time = timezone.now()
                session.duration = session.end_time - session.start_time
                session.save()
                del request.session['practice_session_id']
                return JsonResponse({
                    'status': 'success',
                    'duration': session.duration.seconds,
                    'message': f"Session completed! Duration: {session.duration.seconds // 60} minutes"
                })
            except PracticeSession.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=400)
        return JsonResponse({'status': 'error', 'message': 'No active session'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def profile(request):
    user = request.user
    return render(request, 'users/profile.html', {'user': user})
