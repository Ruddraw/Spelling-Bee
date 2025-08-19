from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm
from .models import PracticeRecord, Word
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
        
        # Create a practice record
        PracticeRecord.objects.create(
            user=request.user,
            word=word,
            attempted_spelling=user_input,
            is_correct=is_correct
        )
        
        if is_correct:
            messages.success(request, "Correct spelling!")
        else:
            messages.error(request, f"Incorrect. The correct spelling is '{word.word}'.")
        
        # After checking, redirect to show a new word
        return redirect('spelling_practice')
    
    else:  # GET request
        word = Word.objects.order_by('?').first()
        if not word:
            messages.error(request, "No words available.")
            return redirect('home')
        
        request.session['current_word_id'] = word.id  # Save for later checking
        return render(request, 'users/spelling_practice.html', {'word': word})

@login_required
def profile(request):
    user = request.user
    practice_records = PracticeRecord.objects.filter(user=user)
    
    # Calculate statistics
    total_attempts = practice_records.count()
    correct_attempts = practice_records.filter(is_correct=True).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    context = {
        'user': user,
        'practice_records': practice_records[:10],  # Show last 10 records
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'accuracy': accuracy
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def practice_history(request):
    user = request.user
    practice_records = PracticeRecord.objects.filter(user=user)
    
    # Calculate statistics
    total_attempts = practice_records.count()
    correct_attempts = practice_records.filter(is_correct=True).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    context = {
        'practice_records': practice_records,
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'accuracy': accuracy
    }
    
    return render(request, 'users/practice_history.html', context)