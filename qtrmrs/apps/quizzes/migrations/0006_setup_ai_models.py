from django.db import migrations


def setup_ai_models(apps, schema_editor):
    """Set up the approved AI models and deactivate old ones."""
    AIModel = apps.get_model('quizzes', 'AIModel')
    
    # Deactivate all existing models
    AIModel.objects.all().update(is_active=False, is_default=False)
    
    # Define the new models
    models_to_create = [
        {'display_name': 'Gemini Flash (Latest)', 'model_name': 'gemini-flash-latest', 'is_default': True},
        {'display_name': 'Gemini Flash Lite (Latest)', 'model_name': 'gemini-flash-lite-latest', 'is_default': False},
        {'display_name': 'Gemini 2.5 Flash', 'model_name': 'gemini-2.5-flash', 'is_default': False},
        {'display_name': 'Gemini 2.5 Flash Lite', 'model_name': 'gemini-2.5-flash-lite', 'is_default': False},
        {'display_name': 'Gemini 2.5 Pro', 'model_name': 'gemini-2.5-pro', 'is_default': False},
        {'display_name': 'Gemini Pro (Latest)', 'model_name': 'gemini-pro-latest', 'is_default': False},
    ]
    
    for model_data in models_to_create:
        obj, created = AIModel.objects.update_or_create(
            model_name=model_data['model_name'],
            defaults={
                'display_name': model_data['display_name'],
                'is_active': True,
                'is_default': model_data['is_default'],
            }
        )


def reverse_setup(apps, schema_editor):
    """Reverse the migration - just deactivate all."""
    AIModel = apps.get_model('quizzes', 'AIModel')
    AIModel.objects.all().update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0005_delete_topic_alter_aimodel_options_and_more'),
    ]

    operations = [
        migrations.RunPython(setup_ai_models, reverse_setup),
    ]
