"""Quiz services."""

from decimal import Decimal

from django.contrib.auth import get_user_model

from .models import Quiz, QuizAnswer, QuizAttempt

User = get_user_model()


class QuizService:
    """Service for quiz management."""
    
    @staticmethod
    def calculate_score(attempt: QuizAttempt) -> Decimal:
        """Calculate score for a quiz attempt."""
        quiz = attempt.quiz
        
        if quiz.question_type == Quiz.QuestionType.OPEN:
            # Open answers need manual grading
            return None
        
        answers = attempt.answers.select_related('quiz_option')
        correct_answers = sum(1 for a in answers if a.is_correct)
        total_options = quiz.options.filter(is_correct=True).count()
        
        if total_options == 0:
            return Decimal('0.00')
        
        score = Decimal(str((correct_answers / total_options) * 100))
        return score
    
    @staticmethod
    def get_best_score(user: User, quiz: Quiz) -> Decimal:
        """Get best score for a user on a quiz."""
        attempts = QuizAttempt.objects.filter(user=user, quiz=quiz)
        if not attempts.exists():
            return None
        
        return max(a.score for a in attempts if a.score is not None)