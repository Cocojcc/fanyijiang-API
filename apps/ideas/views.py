from apps.utils.api import CustomAPIView

from .serializers import IdeaValidator, IdeaDetailSerializer, IdeaCommentValidator, IdeaCommentSerializer
from .models import Idea, IdeaComment, IdeaLike


class IdeaView(CustomAPIView):
    def post(self, request):
        """发表想法"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        avatar = "images/001.png"  # TODO 虚假的头像
        nickname = "新手"  # TODO 虚假的昵称

        data = {
            "user_id": user_id,
            "content": request.data.get("content", None)
        }
        s = IdeaValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            idea = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        idea.avatar = avatar
        idea.nickname = nickname
        s = IdeaDetailSerializer(instance=idea)
        return self.success(s.data)

    def get(self, request):
        """查看本人的所有想法"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        avatar = "images/001.png"  # TODO 虚假的头像
        nickname = "新手"  # TODO 虚假的昵称

        try:
            ideas = Idea.objects.filter(user_id=user_id)
        except Exception as e:
            return self.error(e.args, 401)
        for idea in ideas:
            idea.avatar = avatar
            idea.nickname = nickname
        s = IdeaDetailSerializer(instance=ideas, many=True)
        return self.success(s.data)


class MonoIdeaView(CustomAPIView):
    def delete(self, request, idea_pk):
        """删除自己的想法"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            idea = Idea.objects.get(pk=idea_pk, user_id=user_id)
            idea.delete()  # TODO 收藏、点赞等都自动删除了吗
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request, idea_pk):
        """查看想法详情"""

        try:
            idea = Idea.objects.get(pk=idea_pk)
        except Idea.DoesNotExist as e:
            return self.error(e.args, 401)
        avatar = "images/001.png"  # TODO 虚假的头像
        nickname = "新手"  # TODO 虚假的昵称
        idea.avatar = avatar
        idea.nickname = nickname
        s = IdeaDetailSerializer(instance=idea)
        return self.success(s.data)

    def put(self, request, idea_pk):
        """修改自己的想法"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "user_id": user_id,
            "content": request.data.get("content", None)
        }
        s = IdeaValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            idea = Idea.objects.get(pk=idea_pk, user_id=user_id)
            idea.content = s.validated_data["content"]
            idea.save()
        except Exception as e:
            return self.error(e.args, 401)
        avatar = "images/001.png"  # TODO 虚假的头像
        nickname = "新手"  # TODO 虚假的昵称
        idea.avatar = avatar
        idea.nickname = nickname
        s = IdeaDetailSerializer(instance=idea)
        return self.success(s.data)


class IdeaCommentView(CustomAPIView):
    def post(self, request, idea_pk):
        """想法评论"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "user_id": user_id,
            "think": idea_pk,
            "content": request.data.get("content", None)
        }
        s = IdeaCommentValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            comment = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comment)
        return self.success(s.data)

    def get(self, request, idea_pk):
        """查看想法的所有评论"""

        try:
            idea = Idea.objects.get(pk=idea_pk)
            comments = idea.ideacomment_set.all()
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comments, many=True)
        return self.success(s.data)


class MonoIdeaCommentView(CustomAPIView):
    def delete(self, request, idea_pk, comment_pk):
        """删除评论"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            IdeaComment.objects.get(pk=comment_pk, user_id=user_id, think=idea_pk).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def put(self, request, idea_pk, comment_pk):
        """修改评论"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "user_id": user_id,
            "think": idea_pk,
            "content": request.data.get("content", None)
        }
        s = IdeaCommentValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            comment = IdeaComment.objects.get(pk=comment_pk, think=idea_pk, user_id=user_id)
            comment.content = s.validated_data["content"]
            comment.save()
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comment)
        return self.success(s.data)

    def get(self, request, idea_pk, comment_pk):
        """查看评论"""

        try:
            comment = IdeaComment.objects.get(pk=comment_pk, think=idea_pk)
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comment)
        return self.success(s.data)


class IdeaLikeView(CustomAPIView):
    def post(self, request):
        """想法及其评论点赞"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        which_model = Idea if request.data.get("type", "") == "idea" else IdeaComment
        try:
            which_object = which_model.objects.get(pk=request.data.get("id", None))  # TODO 能否给自己点赞
            which_object.agree.create(user_id=user_id)
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def delete(self, request):
        """取消点赞"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            IdeaLike.objects.get(pk=request.data.get("id", None), user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()
