from django.db import transaction

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from .serializers import ArticleCreateSerializer, NewArticleSerializer, ArticleDetailSerializer, \
    ArticleCommentSerializer
from .models import Article, ArticleComment, ArticleVote

from apps.taskapp.tasks import articles_pv_record


class ArticleView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """发表文章"""

        data = {
            "user_id": request._request.uid,
            "title": request.data.get("title", None),
            "content": request.data.get("content", None),  # 注意HTML转义
            "image": request.data.get("image", ""),
            "status": request.data.get("status", "draft"),
            "labels": request.data.getlist("labels", []),
        }
        s = ArticleCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)

        try:
            article = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = NewArticleSerializer(instance=article)
        return self.success(s.data)

    @validate_identity
    def put(self, request):
        """更新文章，成品不能改为草稿"""

        user_id = request._request.uid
        data = {
            "user_id": user_id,
            # TODO 使用序列化器来验证数据，需要绕过作者和标题的唯一性，因此使用假标题。
            # TODO 这会造成BUG：用户发表了标题为a的文章后，就不能更新自己的文章了
            "title": "a",
            "content": request.data.get("content", None),  # 注意HTML转义
            "image": request.data.get("image", ""),
            "status": request.data.get("status", "draft"),
            "labels": request.data.getlist("labels", []),
        }
        s = ArticleCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)

        try:
            article = Article.objects.get(pk=request.data.get("pk", None), user_id=user_id)
        except Article.DoesNotExist as e:
            return self.error(e.args, 401)
        title = request.data.get("title", "")
        if not title:
            return self.error("文章没有标题", 401)
        status = s.validated_data["status"]
        if article.status == "published":
            status = "published"

        article.title = title
        article.content = s.validated_data["content"]
        article.image = s.validated_data["image"]
        article.status = status
        try:
            with transaction.atomic():
                article.save()
                article.labels.set(s.validated_data["labels"])
        except Exception as e:
            return self.error(e.args)
        s = NewArticleSerializer(instance=article)
        return self.success(s.data)

    @validate_identity
    def patch(self, request):
        """把草稿变为成品"""

        try:
            article = Article.objects.get(pk=request.data.get("pk", None), user_id=request._request.uid)
        except Article.DoesNotExist as e:
            return self.error(e.args, 401)
        try:
            if article.status == "draft":
                article.status = "published"
                article.save()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request):
        """查看文章，不包括草稿"""

        articles = Article.objects.filter(status="published")
        # TODO 返回哪部分数据？
        data = self.paginate_data(request, query_set=articles, object_serializer=NewArticleSerializer)
        return self.success(data)


class ArticleDetailView(CustomAPIView):
    @validate_identity
    def get(self, request, article_id):
        """查看文章详情，只有作者能查看草稿"""

        try:
            article = Article.objects.get(pk=article_id)
        except Article.DoesNotExist as e:
            return self.error(e.args, 401)
        if article.status == "draft":
            if article.user_id != request._request.uid:  # TODO 查看草稿必须登录，非草稿不需要@validate_identity
                return self.error("草稿只有作者可以查看", 401)
        s = ArticleDetailSerializer(instance=article)

        # TODO 记录阅读量
        articles_pv_record.delay(request.META.get('REMOTE_ADDR'), article.id)
        return self.success(s.data)


class DraftView(CustomAPIView):
    @validate_identity
    def get(self, request):
        """查看草稿箱"""

        drafts = Article.objects.filter(user_id=request._request.uid, status="draft")
        # TODO 返回哪部分数据？
        data = self.paginate_data(request, query_set=drafts, object_serializer=ArticleDetailSerializer)
        return self.success(data)


class CommentView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """评论文章，必须是已发表的文章"""

        data = {
            "article": request.data.get("pk", None),
            "user_id": request._request.uid,
            "content": request.data.get("content", None),
        }
        s = ArticleCommentSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        article = s.validated_data["article"]
        s.validated_data["reply_to_user"] = article.user_id
        try:
            comment = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = ArticleCommentSerializer(instance=comment)

        # TODO 触发消息通知

        return self.success(s.data)

    @validate_identity
    def delete(self, request):
        """删除本人的评论"""

        user_id = request._request.uid
        try:
            ArticleComment.objects.get(pk=request.data.get("pk", None), user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    @validate_identity
    def put(self, request):
        """修改本人的评论"""

        user_id = request._request.uid
        content = request.data.get("content", None)
        if not content:
            return self.error("评论不能为空", 401)
        try:
            comment = ArticleComment.objects.get(pk=request.data.get("pk", None), user_id=user_id)
            comment.content = content
            comment.save()
        except Exception as e:
            return self.error(e.args, 401)
        s = ArticleCommentSerializer(instance=comment)
        return self.success(s.data)


class VoteView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """文章及其评论的投票"""

        user_id = request._request.uid
        which_model = Article if request.data.get("type", "") == "article" else ArticleComment
        try:
            which_object = which_model.objects.get(pk=request.data.get("id", None))  # TODO 能否给自己投票
        except which_model.DoesNotExist as e:
            return self.error(e.args, 401)
        value = request.data.get("value", None)
        value = bool(value)  # TODO value的具体规则
        try:
            vote = which_object.vote.create(user_id=user_id, value=value)
        except Exception as e:
            return self.error(e.args, 401)
        data = {
            "user_id": vote.user_id,
            "value": vote.value,
            "ac_id": vote.object_id,
            "pk": vote.pk
        }

        # TODO 触发消息通知
        return self.success(data)

    @validate_identity
    def delete(self, request):
        """撤销投票"""

        user_id = request._request.uid
        pk = request.data.get("pk", None)
        try:
            ArticleVote.objects.get(pk=pk, user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()


class ArticleCommentDetailView(CustomAPIView):
    def get(self, request, article_id):
        """获取指定文章的所有评论"""

        try:
            article = Article.objects.get(pk=article_id, status="published")
        except Article.DoesNotExist as e:
            return self.error(e.args, 401)
        comments = article.articlecomment_set.all()  # TODO 过滤条件
        s = ArticleCommentSerializer(instance=comments, many=True)
        return self.success(s.data)
