from django.core.management.base import BaseCommand
from apps.quizzes.models import AIModel

class Command(BaseCommand):
    help = 'Configures active and default AI models based on user preference'

    def handle(self, *args, **options):
        target_models = [
            'gemini-2.5-flash-lite',
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-flash-lite-latest',
            'gemini-flash-latest',
            'gemini-pro-latest',
        ]
        default_model = 'gemini-flash-lite-latest'

        # 1. Deactivate all first
        AIModel.objects.update(is_active=False, is_default=False)
        self.stdout.write("Deactivated all models.")

        # 2. Activate target models
        # We use strict filtering. If a model name from the list doesn't exist in DB, it's skipped.
        count = AIModel.objects.filter(model_name__in=target_models).update(is_active=True)
        self.stdout.write(f"Activated {count} models matching the target list.")
        
        # Verify which ones were activated
        active_now = list(AIModel.objects.filter(is_active=True).values_list('model_name', flat=True))
        missing = set(target_models) - set(active_now)
        if missing:
             self.stdout.write(self.style.WARNING(f"Missing active models (not in DB): {', '.join(missing)}"))

        # 3. Set default
        try:
            obj = AIModel.objects.get(model_name=default_model)
            obj.is_default = True
            obj.save()
            self.stdout.write(f"Set default model to: {default_model}")
        except AIModel.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Default model {default_model} not found in DB!"))

        # 4. List final status
        self.stdout.write("\nFinal Active Models:")
        for m in AIModel.objects.filter(is_active=True):
            status = "(Default)" if m.is_default else ""
            self.stdout.write(f" - {m.model_name} {status}")
