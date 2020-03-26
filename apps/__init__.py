import os
import re

import requests
from django.conf import settings
from rest_framework.test import APIClient


def xss_safe(value):
    """检查字符串对XSS攻击是否免疫"""

    if not re.search(r"[<>&]", value):
        return True
    else:
        return False


def legal_image_path(path):
    """检查字符串是否是合法的图片路径"""

    file, ext = os.path.splitext(path)
    if not file:
        return False
    if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
        return False
    return True


def common_prepare(obj):
    """准备测试用户、登录和客户端"""

    from apps.userpage.models import UserProfile

    UserProfile.objects.create(uid="e4da3b7fbbce2345d7772b0674a318d5", nickname="haoran·zhang", slug="zhanghaoran")
    UserProfile.objects.create(uid="a87ff679a2f3e71d9181a67b7542122c", nickname="赵军臣", slug="zhao-jun-chen")
    data = {
        "username": "18569938068",
        "password": "1234567",
        "login_type": "normal"
    }
    response = requests.post(settings.USER_CENTER_GATEWAY + "/api/login", data=data)
    obj.headers = {"HTTP_AUTHORIZATION": response.json()["data"]["token"]}
    obj.client = APIClient()
