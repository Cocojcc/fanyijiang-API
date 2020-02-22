from rest_framework import serializers
from django.conf import settings

from apps.userpage.models import (UserProfile, UserEmploymentHistory, UserEducationHistory,
                                  UserLocations, UserFavorites, FollowedFavorites, FavoriteCollection)

from apps.labels.models import Label
from apps.labels.serializers import LabelCreateSerializer

from apps.questions.models import Question, QuestionFollow, Answer
from apps.questions.serializers import AnswerCreateSerializer


class UserInfoSerializer(serializers.ModelSerializer):
    employment_history = serializers.SerializerMethodField()
    education_history = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('uid', 'nickname', 'avatar', 'autograph', 'industry',
                  'employment_history', 'education_history', 'locations',
                  'description', 'slug')

    def get_employment_history(self, obj):
        history = obj.user_employment_history.all()
        data = UserEmploymentHistorySerializer(history, many=True).data
        return data

    def get_education_history(self, obj):
        history = obj.user_education_history.all()
        data = UserEducationHistorySerializer(history, many=True).data
        return data

    def get_locations(self, obj):
        locations = obj.location.all()
        data = UserLocationSerializer(locations, many=True).data
        return data


class UserEmploymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmploymentHistory
        fields = ('company', 'position')


class UserEducationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducationHistory
        fields = ('school', 'major', 'education', 'in_year', 'out_year')


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocations
        fields = ('name', 'location_pic')


class FavoritesSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()
    follow_count = serializers.SerializerMethodField()

    class Meta:
        model = UserFavorites
        fields = ('id', 'title', 'status', 'content_count', 'follow_count', 'update_time')

    def get_content_count(self, obj):
        return obj.mark_content.all().count()

    def get_follow_count(self, obj):
        return FollowedFavorites.objects.filter(bm=obj).count()


# class FavoritesAnswerSerializer(serializers.ModelSerializer):
#     class Meta:


class FollowsUserSerializer(serializers.ModelSerializer):
    fans_count = serializers.SerializerMethodField()  # 关注者
    articles_count = serializers.SerializerMethodField()  # 文章数
    answers_count = serializers.SerializerMethodField()  # 回答数

    class Meta:
        model = UserProfile
        fields = ('avatar', 'nickname', 'autograph', 'slug', 'uid', 'fans_count', 'articles_count', 'answers_count')

    def get_fans_count(self, obj):
        return UserProfile.objects.filter(as_fans__idol__uid=obj.uid).count()

    def get_articles_count(self, obj):
        # TODO 数据库查询
        return 0

    def get_answers_count(self, obj):
        # TODO 数据库查询
        return 0


class FavoritesContentSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteCollection
        fields = ('details',)

    def get_details(self, obj):
        content_object = obj.content_object
        if isinstance(content_object, Label):
            content_data = LabelCreateSerializer(content_object).data

        if isinstance(content_object, UserProfile):
            content_data = UserInfoSerializer(content_object).data

        if isinstance(content_object, Answer):
            content_data = AnswerCreateSerializer(instance=content_object).data
        # TODO 查询其他对象：文章、回答等
        return content_data


class UserPageQuestionSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="create_at", read_only=True)
    answer_count = serializers.SerializerMethodField()
    follow_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'content', 'create_time', 'answer_count',)

    def get_answer_count(self, obj):
        return obj.answer_set.all().count()

    def get_follow_count(self, obj):
        return QuestionFollow.objects.filter(question=obj).count()


class UserPageAnswerSerializer(serializers.ModelSerializer):
    question_title = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'content', 'question_id', 'question_title', 'user_info',
                  )

    def get_user_info(self, obj):
        user = UserProfile.objects.filter(uid=obj.user_id).only('nickname', 'avatar', 'slug')
        data = {'nickname': user.nickname, 'avatar': user.avatar, 'user_slug': user.slug}
        return data

    def get_question_title(self, obj):
        return obj.question.title