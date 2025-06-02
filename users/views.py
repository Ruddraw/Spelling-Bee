from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Word
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
        if user_input == correct_word:
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
