import html

from rest_framework import serializers

from apps import xss_safe, legal_image_path
from apps.userpage.models import UserProfile
from .models import Label


class LabelChecker(serializers.ModelSerializer):
    """用于新建或修改标签时检查数据"""

    class Meta:
        model = Label
        fields = ("name", "intro", "avatar",)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("标签名称不能为空")
        if value.capitalize() == str(None):
            return None
        if not xss_safe(value):
            raise serializers.ValidationError("标签名称含有特殊字符")
        return value

    def validate_intro(self, value):
        if not value:
            return None
        if value.capitalize() == str(None):
            return None
        return html.escape(value)

    def validate_avatar(self, value):
        if not value:
            return None
        if value.capitalize() == str(None):
            return None
        if not legal_image_path(value):
            raise serializers.ValidationError("图片路径或类型无效")
        return value


class SimpleLabelSerializer(serializers.ModelSerializer):
    """用于标签的序列化，需要传入当前登录用户"""

    is_followed = serializers.SerializerMethodField()
    follower_count = serializers.IntegerField(source="followers.count")
    type = serializers.CharField(source="kind")

    class Meta:
        model = Label
        fields = ("id", "type", "name", "intro", "avatar", "is_followed", "follower_count",)

    def get_is_followed(self, obj):
        me = self.context["me"]
        if not me:
            return False
        return obj.followers.filter(pk=me.pk).exists()


class DetailedLabelSerializer(SimpleLabelSerializer):
    """用于标签的序列化，需要传入当前登录用户"""

    question_count = serializers.SerializerMethodField()  # TODO 问题个数

    class Meta:
        model = Label
        fields = ("id", "type", "name", "intro", "avatar", "is_followed", "follower_count", "question_count",)

    def get_question_count(self, obj):
        return 0  # TODO 改成真实数据


class SimpleUserSerializer(serializers.ModelSerializer):
    """用于用户的序列化"""

    id = serializers.CharField(source="uid")
    type = serializers.CharField(source="kind")
    homepage = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "type", "slug", "nickname", "gender", "avatar", "autograph", "homepage")

    def get_homepage(self, obj):
        return ""  # TODO 用户主页的地址
