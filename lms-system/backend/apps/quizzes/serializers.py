"""Quiz serializers."""

from rest_framework import serializers

from .models import Quiz, QuizAnswer, QuizAttempt, QuizOption


class QuizOptionSerializer(serializers.ModelSerializer):
    """Serializer for QuizOption model."""
    
    class Meta:
        model = QuizOption
        fields = ['id', 'text', 'is_correct', 'order_num']
        read_only_fields = ['id', 'order_num']


class QuizOptionListSerializer(serializers.ModelSerializer):
    """Serializer for listing options without correct answer."""
    
    class Meta:
        model = QuizOption
        fields = ['id', 'text', 'order_num']


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model."""
    
    options = QuizOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'question', 'question_type', 'options', 'order_num', 'created_at']
        read_only_fields = ['id', 'order_num', 'created_at']


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for listing quizzes without correct answers."""
    
    options = QuizOptionListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'question', 'question_type', 'options', 'order_num']


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating quizzes."""
    
    options = QuizOptionSerializer(many=True)
    
    class Meta:
        model = Quiz
        fields = ['module', 'question', 'question_type', 'options']
    
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        quiz = Quiz.objects.create(**validated_data)
        for option_data in options_data:
            QuizOption.objects.create(quiz=quiz, **option_data)
        return quiz


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting quiz answer."""
    
    quiz_id = serializers.IntegerField()
    option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    text = serializers.CharField(required=False, allow_blank=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt model."""
    
    quiz_question = serializers.CharField(source='quiz.question', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_question', 'attempt_number', 'score', 'completed_at']
        read_only_fields = ['id', 'attempt_number', 'score', 'completed_at']


class QuizAnswerSerializer(serializers.ModelSerializer):
    """Serializer for QuizAnswer model."""
    
    class Meta:
        model = QuizAnswer
        fields = ['id', 'quiz_option', 'text', 'is_correct', 'created_at']
        read_only_fields = ['id', 'is_correct', 'created_at']