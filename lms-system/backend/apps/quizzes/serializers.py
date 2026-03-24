"""Quiz serializers."""

from rest_framework import serializers

from .models import Quiz, QuizAnswer, QuizAttempt, QuizOption


# === CHUNK: QUIZ_SERIALIZERS_V1 [QUIZZES] ===
# Описание: Сериализаторы для тестов, вариантов ответов, попыток и ответов.
# Dependencies: QUIZ_MODELS_V1


# [START_QUIZ_OPTION_SERIALIZER]
# ANCHOR: QUIZ_OPTION_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели QuizOption
# PURPOSE: Сериализатор для вариантов ответов (с указанием правильности).
class QuizOptionSerializer(serializers.ModelSerializer):
    """Serializer for QuizOption model."""
    
    class Meta:
        model = QuizOption
        fields = ['id', 'text', 'is_correct', 'order_num']
        read_only_fields = ['id', 'order_num']
# [END_QUIZ_OPTION_SERIALIZER]


# [START_QUIZ_OPTION_LIST_SERIALIZER]
# ANCHOR: QUIZ_OPTION_LIST_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели QuizOption без поля is_correct
# PURPOSE: Сериализатор для отображения вариантов без указания правильности.
class QuizOptionListSerializer(serializers.ModelSerializer):
    """Serializer for listing options without correct answer."""
    
    class Meta:
        model = QuizOption
        fields = ['id', 'text', 'order_num']
# [END_QUIZ_OPTION_LIST_SERIALIZER]


# [START_QUIZ_SERIALIZER]
# ANCHOR: QUIZ_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели Quiz с вложенными вариантами
# PURPOSE: Полный сериализатор для вопроса теста с вариантами ответов.
class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model."""
    
    options = QuizOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'question', 'question_type', 'options', 'order_num', 'created_at']
        read_only_fields = ['id', 'order_num', 'created_at']
# [END_QUIZ_SERIALIZER]


# [START_QUIZ_LIST_SERIALIZER]
# ANCHOR: QUIZ_LIST_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели Quiz без правильных ответов
# PURPOSE: Сериализатор для списка тестов без раскрытия правильных ответов.
class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for listing quizzes without correct answers."""
    
    options = QuizOptionListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'question', 'question_type', 'options', 'order_num']
# [END_QUIZ_LIST_SERIALIZER]


# [START_QUIZ_CREATE_SERIALIZER]
# ANCHOR: QUIZ_CREATE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для создания теста с вариантами
# PURPOSE: Сериализатор для создания вопроса теста с вариантами ответов.
class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating quizzes."""
    
    options = QuizOptionSerializer(many=True)
    
    class Meta:
        model = Quiz
        fields = ['module', 'question', 'question_type', 'options']
    
    # [START_QUIZ_CREATE]
    # ANCHOR: QUIZ_CREATE
    # @PreConditions:
    # - validated_data содержит данные теста и options
    # @PostConditions:
    # - создаёт Quiz и связанные QuizOption
    # - возвращает созданный экземпляр Quiz
    # PURPOSE: Создание вопроса теста с вложенными вариантами ответов.
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        quiz = Quiz.objects.create(**validated_data)
        for option_data in options_data:
            QuizOption.objects.create(quiz=quiz, **option_data)
        return quiz
    # [END_QUIZ_CREATE]


# [END_QUIZ_CREATE_SERIALIZER]


# [START_SUBMIT_ANSWER_SERIALIZER]
# ANCHOR: SUBMIT_ANSWER_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для отправки ответа на тест
# PURPOSE: Сериализатор для отправки ответа пользователя на вопрос теста.
class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting quiz answer."""
    
    quiz_id = serializers.IntegerField()
    option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    text = serializers.CharField(required=False, allow_blank=True)
# [END_SUBMIT_ANSWER_SERIALIZER]


# [START_QUIZ_ATTEMPT_SERIALIZER]
# ANCHOR: QUIZ_ATTEMPT_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели QuizAttempt
# PURPOSE: Сериализатор для попытки прохождения теста.
class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt model."""
    
    quiz_question = serializers.CharField(source='quiz.question', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_question', 'attempt_number', 'score', 'completed_at']
        read_only_fields = ['id', 'attempt_number', 'score', 'completed_at']
# [END_QUIZ_ATTEMPT_SERIALIZER]


# [START_QUIZ_ANSWER_SERIALIZER]
# ANCHOR: QUIZ_ANSWER_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели QuizAnswer
# PURPOSE: Сериализатор для ответа пользователя на вопрос теста.
class QuizAnswerSerializer(serializers.ModelSerializer):
    """Serializer for QuizAnswer model."""
    
    class Meta:
        model = QuizAnswer
        fields = ['id', 'quiz_option', 'text', 'is_correct', 'created_at']
        read_only_fields = ['id', 'is_correct', 'created_at']
# [END_QUIZ_ANSWER_SERIALIZER]


# === END_CHUNK: QUIZ_SERIALIZERS_V1 ===