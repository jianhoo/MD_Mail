from django.shortcuts import render

# Create your views here.
from itsdangerous import BadData
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view())
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, EmailVerifySerializer
from utils import tjws


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


class EmailView(generics.UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):

    """
    邮箱验证
    """

    def get(self, request):
        serializer = serializers.EmailVerifySerializer(data=request.query_params)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'OK'})
        return Response({'message': serializer.errors})



