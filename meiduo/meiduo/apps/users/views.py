from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view())
from users.serializers import CreateUserSerializer, UserDetailSerializer


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


class UserView(generics.CreateAPIView):
    """
    用户注册
    传入参数:
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = CreateUserSerializer


# url(r'^user/$',views.UserDetailView.as_view())
class UserDetailView(generics.RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


