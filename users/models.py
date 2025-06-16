# users/models.py
from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    index = models.IntegerField(unique=True)
    word = models.CharField(max_length=100)
    pronunciation = models.CharField(max_length=100, blank=True)
    part_of_speech = models.CharField(max_length=10, blank=True)
    definition = models.TextField()
    sentence = models.TextField(blank=True)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['index']


class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Session for {self.user.username} at {self.start_time}"


class WordAttempt(models.Model):
    session = models.ForeignKey(
        PracticeSession, on_delete=models.CASCADE, related_name='attempts')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    user_input = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt: {self.word.word} - {'Correct' if self.is_correct else 'Incorrect'}"
