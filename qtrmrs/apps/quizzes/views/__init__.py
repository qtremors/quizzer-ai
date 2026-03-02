# Quiz views package
# Re-exports all views so urls.py continues to work with `from . import views`

from .setup import quiz_setup, create_quiz
from .player import quiz_player, submit_answer
from .results import quiz_results, generate_all_explanations, retry_quiz, delete_quiz
from .demo import quick_quiz, demo_player, demo_submit, demo_results

__all__ = [
    'quiz_setup', 'create_quiz',
    'quiz_player', 'submit_answer',
    'quiz_results', 'generate_all_explanations', 'retry_quiz', 'delete_quiz',
    'quick_quiz', 'demo_player', 'demo_submit', 'demo_results',
]
