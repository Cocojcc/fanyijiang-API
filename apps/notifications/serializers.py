from rest_framework import serializers
from .models import Notification

from apps.questions.models import Answer, Question


class NotificationsSerializer(serializers.ModelSerializer):
    # detail = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    verb = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    format_time = serializers.DateTimeField(format="%Y-%m-%d", read_only=True, source='created_at')

    class Meta:
        model = Notification
        fields = ('actor', 'verb', 'target', 'created_at', 'format_time')

    def get_actor(self, obj):
        actor = obj.actor
        data = {
            'nickname': actor.nickname,
            'slug': actor.slug
        }
        return data

    def get_verb(self, obj):
        return obj.get_verb_display()

    def get_target(self, obj):
        action_object = obj.action_object
        verb = obj.verb
        data = {}
        if action_object == None:
            return '作者已删除'
        if verb == 'O':
            # 关注了你
            pass

        if verb == 'I':
            # 的提问等你来答
            data['title'] = action_object.title
            data['id'] = action_object.id
            data['link'] = ''  # 问题详情

        if verb == 'R':
            # 回复了你
            data['title'] = action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 问题评论详情或者问题详情

        if verb == 'A':
            # 回答了你的问题
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 回答详情页

        if verb == 'AF':
            # 某人回答了你关注的问题，回答对象
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 回答详情页

        if verb == 'LAN':
            # 赞了你的问答
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 回答详情页

        if verb == 'LAR':
            # 赞了你的文章
            data['title'] = action_object.title
            data['id'] = action_object.id
            data['link'] = ''  # 文章详情

        if verb == 'LQAC':
            # 赞了你的评论
            content_object = action_object.content_object
            if isinstance(content_object, Question):
                data['title'] = action_object.title
                data['id'] = content_object.id
                data['link'] = ''  # 评论详情
            if isinstance(content_object, Answer):
                data['title'] = content_object.content
                data['id'] = content_object.id
                data['link'] = ''  # 评论详情

        if verb == 'LAC':
            # 赞了你的文章评论
            data['title'] = action_object.article.title
            data['id'] = action_object.article.id
            data['link'] = ''  # 文章详情

        if verb == 'LIC':
            # 赞了你的想法评论
            data['title'] = action_object.think.content
            data['id'] = action_object.think.id
            data['link'] = ''  # 想法详情

        if verb == 'CAN':
            # 评论了你的回答
            data['title'] = action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 回答详情

        if verb == 'CAR':
            # 评论了你的文章
            data['title'] = action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 文章评论详情 或者文章详情

        if verb == 'CQ':
            # 评论了你的问题
            data['title'] = action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 问题详情

        if verb == 'CI':
            # 评论了你的想法
            data['title'] = action_object.content[:8] + '...' if len(
                action_object.content) > 8 else action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 想法详情
        return data
