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
    # Clear any existing session when starting fresh
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
    # Get or create practice session
    if 'practice_session_id' not in request.session:
        session = PracticeSession.objects.create(user=request.user)
        request.session['practice_session_id'] = session.id
    else:
        try:
            session = PracticeSession.objects.get(
                id=request.session['practice_session_id'],
                user=request.user,
                end_time__isnull=True
            )
        except PracticeSession.DoesNotExist:
            session = PracticeSession.objects.create(user=request.user)
            request.session['practice_session_id'] = session.id

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip().lower()
        correct_word_id = request.session.get('current_word_id')

        if correct_word_id is None:
            messages.error(request, "Session expired or invalid. Try again.")
            return redirect('spelling_practice')

        try:
            word = Word.objects.get(id=correct_word_id)
        except Word.DoesNotExist:
            messages.error(request, "Word not found.")
            return redirect('spelling_practice')

        correct_word = word.word.lower()
        is_correct = user_input == correct_word
        
        # Create word attempt
        WordAttempt.objects.create(
            session=session,
            word=word,
            user_input=user_input,
            is_correct=is_correct
        )

        if is_correct:
            messages.success(request, "Correct spelling!")
        else:
            messages.error(request, f"Incorrect. The correct spelling is '{word.word}'.")

        return redirect('spelling_practice')

    else:  # GET request
        word = Word.objects.order_by('?').first()
        if not word:
            messages.error(request, "No words available.")
            return redirect('home')

        request.session['current_word_id'] = word.id
        elapsed_time = (timezone.now() - session.start_time).total_seconds()
        
        return render(request, 'users/spelling_practice.html', {
            'word': word,
            'session_start_time': session.start_time.isoformat(),
            'elapsed_time': elapsed_time
        })
    
    

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