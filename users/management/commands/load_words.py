import json
import re
from django.core.management.base import BaseCommand
from users.models import Word
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Load words from JSON file into the Word model'

    def handle(self, *args, **kwargs):
        json_file_path = settings.BASE_DIR / 'data' / 'words.json'

        self.stdout.write(f"Attempting to load file from: {json_file_path}")
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f"File does not exist at: {json_file_path}"))
            return

        try:
            with open(json_file_path, 'r') as file:
                words_data = json.load(file)

            Word.objects.all().delete()
            self.stdout.write("Cleared existing words from database")

            for word_data in words_data:
                # Parse spellings (e.g., "sept [H: Sept.]" -> ["sept", "Sept."])
                word_text = word_data['word']
                # Extract primary spelling (before space) and alternatives (in brackets)
                primary_spelling = word_text.split(' ', 1)[0].strip()
                spellings = [primary_spelling]
                # Find alternatives in brackets, e.g., [H: Sept.]
                bracket_matches = re.findall(r'\[H:\s*([^\]]+)\]', word_text)
                spellings.extend([match.strip() for match in bracket_matches])

                Word.objects.create(
                    index=word_data['index'],
                    spellings=','.join(spellings),  # Store as comma-separated string
                    pronunciation=word_data['pronunciation'],
                    part_of_speech=word_data['part_of_speech'],
                    definition=word_data['definition'],
                    sentence=word_data['sentence']
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(words_data)} words.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: words.json not found at {json_file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Error: Invalid JSON format in words.json'))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'Error: Missing key in JSON data: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))