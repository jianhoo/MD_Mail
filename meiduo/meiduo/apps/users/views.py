from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view())
from users.serializers import CreateUserSerializer


class UsernameCountView(APIView):
    """
    用户名数量
    """

    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserView(CreateAPIView):
    """
    用户注册
    传入参数:
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = CreateUserSerializer

