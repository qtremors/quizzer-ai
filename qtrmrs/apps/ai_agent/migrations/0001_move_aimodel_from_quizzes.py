"""
ARCH-005: Move AIModel from quizzes to ai_agent (state only).

This migration adds AIModel to ai_agent's state WITHOUT touching the database.
The actual table remains as 'quizzes_aimodel' (controlled by Meta.db_table).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('quizzes', '0009_add_xp_awarded_and_useranswer_ordering'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='AIModel',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('display_name', models.CharField(max_length=100)),
                        ('model_name', models.CharField(help_text="The API string, e.g., 'gemini-1.5-flash'", max_length=100)),
                        ('is_active', models.BooleanField(default=True)),
                        ('is_default', models.BooleanField(default=False)),
                    ],
                    options={
                        'verbose_name': 'AI Model',
                        'verbose_name_plural': 'AI Models',
                        'db_table': 'quizzes_aimodel',
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
