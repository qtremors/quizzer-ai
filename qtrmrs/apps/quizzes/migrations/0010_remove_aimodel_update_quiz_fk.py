"""
ARCH-005: Remove AIModel from quizzes state, update Quiz FK (state only).

Companion to ai_agent.0001_move_aimodel_from_quizzes.
Removes AIModel from quizzes' Django state and re-points the Quiz.ai_model FK
to 'ai_agent.AIModel'. No database changes — the FK column and table are unchanged.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0009_add_xp_awarded_and_useranswer_ordering'),
        ('ai_agent', '0001_move_aimodel_from_quizzes'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='AIModel',
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='quiz',
                    name='ai_model',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='quizzes',
                        to='ai_agent.aimodel',
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
