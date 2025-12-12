from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.quiz_setup, name='quiz_setup'),
    path('create/', views.create_quiz, name='create_quiz'),
    
    path('play/<int:quiz_id>/', views.quiz_player, name='quiz_player'),
    path('play/<int:quiz_id>/submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
    
    path('results/<int:quiz_id>/', views.quiz_results, name='quiz_results'),
    path('results/<int:quiz_id>/explain-all/', views.generate_all_explanations, name='generate_all_explanations'),
    path('<int:quiz_id>/retry/', views.retry_quiz, name='retry_quiz'),
    
    # Quick Quiz (Demo Mode for guests)
    path('quick/', views.quick_quiz, name='quick_quiz'),
    path('demo/', views.demo_player, name='demo_player'),
    path('demo/submit/', views.demo_submit, name='demo_submit'),
    path('demo/results/', views.demo_results, name='demo_results'),
]