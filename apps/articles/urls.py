from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ArticleView.as_view(), name="articles"),
    url(r"^(?P<article_id>\d+)/$", views.ArticleDetailView.as_view(), name="article_detail"),
]
