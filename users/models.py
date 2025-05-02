from django.db import models

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



