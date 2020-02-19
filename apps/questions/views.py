from apps.utils.api import CustomAPIView
from .serializers import QuestionCreateSerializer, NewQuestionSerializer, AnswerCreateSerializer, \
    QuestionFollowSerializer, FollowedQuestionSerializer
from .models import Answer, QuestionFollow


class QuestionView(CustomAPIView):
    def post(self, request):
        """提问"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_asks = "小学生"  # TODO 虚假的名称

        data = {
            "title": request.data.get("title", None),
            "content": request.data.get("content", ""),
            "labels": request.data.getlist("labels", []),
            "user_id": user_id
        }
        s = QuestionCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)

        instance.who_asks = who_asks
        s = NewQuestionSerializer(instance=instance)
        return self.success(s.data)


class AnswerView(CustomAPIView):
    def post(self, request, question_id):
        """回答问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_answers = "大师"  # TODO 虚假的名称

        data = {
            "question": question_id,
            "content": request.data.get("content", None),
            "user_id": user_id,
        }
        s = AnswerCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)

        data = dict(AnswerCreateSerializer(instance=instance).data)
        data.pop("user_id")
        data["who_answers"] = who_answers
        return self.success(data)

    def put(self, request, question_id):
        """修改回答，只能修改本人的回答"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_answers = "大师"  # TODO 虚假的名称

        content = request.data.get("content", None)
        try:
            instance = Answer.objects.get(question=question_id, user_id=user_id)
            instance.content = content
            instance.save()
        except Exception as e:
            return self.error(e.args, 401)

        data = dict(AnswerCreateSerializer(instance=instance).data)
        data.pop("user_id")
        data["who_answers"] = who_answers
        return self.success(data)

    def delete(self, request, question_id):
        """删除回答，只能删除本人的回答"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            instance = Answer.objects.get(question=question_id, user_id=user_id)
            instance.delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()


class QuestionFollowView(CustomAPIView):
    def post(self, request):
        """关注问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "user_id": user_id,
            "question": request.data.get("question", None)
        }
        s = QuestionFollowSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def delete(self, request):
        """取消关注问题"""

        user = request.user  # TODO 检查用户权限，只能取消自己关注的问题
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        question = request.data.get("question", None)
        try:
            QuestionFollow.objects.get(question=question, user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request):
        """查看本人关注的问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        follows = QuestionFollow.objects.filter(user_id=user_id)
        questions = [i.question for i in follows]
        s = FollowedQuestionSerializer(instance=questions, many=True)
        return self.success(s.data)
