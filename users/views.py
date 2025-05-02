from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm

def register(request):
  if request.method == 'POST':
    form = UserRegisterForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)  # Log the user in after registration
      messages.success(request, f'Account created for {user.username}!')
      return redirect('home')  # Redirect to homepage (define later)
    else:
      messages.error(request, 'Error creating account. Please check the form.')
  else:
    form = UserRegisterForm()
  return render(request, 'users/register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages

def custom_logout(request):
    logout(request) 
    messages.success(request, 'You have been logged out.')
    return redirect('home')  