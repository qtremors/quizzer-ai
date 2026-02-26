from django.db import transaction
from .models import Quiz, Question, Option


def create_quiz_from_ai_data(
    user,
    questions_data,
    *,
    quiz_type='tech',
    language='',
    topic_description='',
    difficulty='intermediate',
    ai_model=None,
    model_used=''
):
    """
    Create a Quiz with Questions and Options from AI-generated data.
    
    Consolidates the shared DB logic from create_quiz, process_chat_message,
    and quick_quiz into a single function.
    
    Args:
        user: The User creating the quiz.
        questions_data: List of question dicts from the AI generator.
        quiz_type: 'tech' or 'general'.
        language: Programming language or subject area.
        topic_description: Human-readable topic description.
        difficulty: 'beginner', 'intermediate', or 'expert'.
        ai_model: Optional AIModel instance for tracking.
        model_used: Model name string for tracking.
    
    Returns:
        The created Quiz instance.
    """
    with transaction.atomic():
        quiz = Quiz.objects.create(
            user=user,
            quiz_type=quiz_type,
            language=language,
            topic_description=topic_description[:255],
            difficulty=difficulty,
            total_questions=len(questions_data),
            ai_model=ai_model,
            model_used=model_used
        )

        options_to_create = []
        for q_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=q_data.get('text', '')[:2000],
                code_snippet=q_data.get('code_snippet') or '',
                explanation=q_data.get('explanation', '')
            )

            for opt in q_data.get('options', []):
                # Handle both string and dict options from AI
                if isinstance(opt, dict):
                    opt_text = str(opt.get('text', ''))[:255]
                else:
                    opt_text = str(opt)[:255]

                options_to_create.append(Option(
                    question=question,
                    text=opt_text,
                    is_correct=(opt_text == str(q_data.get('correct_answer', '')))
                ))

        if options_to_create:
            Option.objects.bulk_create(options_to_create)

    return quiz
