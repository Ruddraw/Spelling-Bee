from datetime import timezone
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



class PracticeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    attempted_spelling = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.word.word} - {'Correct' if self.is_correct else 'Incorrect'}"
