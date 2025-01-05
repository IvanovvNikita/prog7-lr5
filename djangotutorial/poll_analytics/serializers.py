from rest_framework import serializers
from polls.models import Question, Choice

class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    
    class Meta:
        model = Question
        fields = '__all__'