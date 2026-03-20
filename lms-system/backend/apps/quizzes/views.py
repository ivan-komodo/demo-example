"""Quiz views."""

from decimal import Decimal

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser

from .models import Quiz, QuizAnswer, QuizAttempt, QuizOption
from .serializers import (
    QuizAttemptSerializer,
    QuizCreateSerializer,
    QuizListSerializer,
    QuizSerializer,
    SubmitAnswerSerializer,
)


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz model."""
    
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuizCreateSerializer
        if self.action == 'list':
            return QuizListSerializer
        return QuizSerializer
    
    def get_queryset(self):
        queryset = Quiz.objects.prefetch_related('options').select_related('module')
        module_id = self.request.query_params.get('module_id')
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit quiz answers."""
        quiz = self.get_object()
        
        # Check if user can attempt
        if not QuizAttempt.can_attempt(request.user, quiz):
            return Response(
                {'error': 'Достигнут лимит попыток (максимум 3).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create attempt
        attempt_number = QuizAttempt.get_next_attempt_number(request.user, quiz)
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_number=attempt_number
        )
        
        # Process answers
        score = Decimal('0.00')
        total_questions = 1
        
        if quiz.question_type == Quiz.QuestionType.OPEN:
            # Open answer - needs manual grading
            QuizAnswer.objects.create(
                attempt=attempt,
                text=serializer.validated_data.get('text', ''),
                is_correct=None  # Needs manual grading
            )
        else:
            # Multiple choice or single choice
            option_ids = serializer.validated_data.get('option_ids', [])
            correct_options = quiz.options.filter(is_correct=True)
            selected_options = quiz.options.filter(id__in=option_ids)
            
            # Calculate score
            correct_count = selected_options.filter(is_correct=True).count()
            total_correct = correct_options.count()
            
            if quiz.question_type == Quiz.QuestionType.SINGLE:
                # Single correct answer
                if correct_count == 1 and selected_options.count() == 1:
                    score = Decimal('100.00')
            else:
                # Multiple correct answers
                if total_correct > 0:
                    score = Decimal(str((correct_count / total_correct) * 100))
            
            # Save answers
            for option in selected_options:
                QuizAnswer.objects.create(
                    attempt=attempt,
                    quiz_option=option,
                    is_correct=option.is_correct
                )
        
        # Update attempt score
        attempt.score = score
        attempt.save(update_fields=['score'])
        
        return Response({
            'attempt': QuizAttemptSerializer(attempt).data,
            'score': score,
            'is_correct': score == 100
        })
    
    @action(detail=True, methods=['get'])
    def attempts(self, request, pk=None):
        """Get user attempts for a quiz."""
        quiz = self.get_object()
        attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for QuizAttempt model."""
    
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = QuizAttempt.objects.select_related('quiz').filter(user=self.request.user)
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        return queryset