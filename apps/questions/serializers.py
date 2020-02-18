from rest_framework import serializers

from .models import Question
from apps.labels.models import Label


class QuestionCreateSerializer(serializers.ModelSerializer):
    """用于提问时的反序列化验证和写入数据库"""
    labels = serializers.ListField(required=True)

    class Meta:
        model = Question
        fields = ("title", "content", "user_id", "labels")

    def validate_labels(self, value):
        value = Label.objects.filter(name__in=value)
        if not value:
            raise serializers.ValidationError("问题的标签不存在")
        return value


class NewQuestionSerializer(serializers.ModelSerializer):
    """用于提问成功后的序列化"""
    who_asks = serializers.CharField()
    labels = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = ("title", "content", "who_asks", "labels", "pk")
