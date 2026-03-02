"""
Django management command to verify Gemini API connectivity and list available models.

Usage:
    python manage.py check_ai_config
"""
from django.core.management.base import BaseCommand
from apps.ai_agent.client import get_gemini_client


class Command(BaseCommand):
    help = 'Verify Gemini API connectivity and list available content generation models'

    def handle(self, *args, **options):
        try:
            client = get_gemini_client()
            api_key = client._api_client.api_key
            self.stdout.write(self.style.SUCCESS(
                f"✅ Authenticated successfully with key: ...{api_key[-4:]}"
            ))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"❌ {e}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection failed: {e}"))
            return

        self.stdout.write('\n🔍 Fetching available models that support text generation...\n')

        count = 0
        try:
            for m in client.models.list():
                if 'generateContent' in m.supported_actions:
                    self.stdout.write(f" • {m.name}")
                    self.stdout.write(f"   (Display Name: {m.display_name})")
                    self.stdout.write("-" * 40)
                    count += 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error listing models: {e}"))
            return

        if count == 0:
            self.stdout.write(self.style.WARNING(
                "⚠️ No content generation models found. Your API key might lack permissions."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✨ Found {count} usable models."))
