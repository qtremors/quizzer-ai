"""
Django management command to sync available Gemini models to the database.

Usage:
    python manage.py sync_models
"""
import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.quizzes.models import AIModel


class Command(BaseCommand):
    help = 'Sync available Gemini AI models to the database'

    def handle(self, *args, **options):
        # Configure the API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        self.stdout.write('🔍 Fetching available models from Gemini API...\n')
        
        synced = 0
        created = 0
        
        try:
            for model in genai.list_models():
                # Only models that support content generation
                if 'generateContent' not in model.supported_generation_methods:
                    continue
                
                # Extract model name (remove 'models/' prefix)
                model_name = model.name.replace('models/', '')
                display_name = model.display_name
                
                # Create or update the model in database
                obj, was_created = AIModel.objects.update_or_create(
                    model_name=model_name,
                    defaults={
                        'display_name': display_name,
                    }
                )
                
                if was_created:
                    created += 1
                    self.stdout.write(f'  ✨ NEW: {display_name} ({model_name})')
                else:
                    synced += 1
                    self.stdout.write(f'  ✓ Synced: {display_name}')
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Done! {created} new, {synced} updated.'
            ))
            
            # Show active models
            active_count = AIModel.objects.filter(is_active=True).count()
            self.stdout.write(f'📊 {active_count} models are currently active.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
