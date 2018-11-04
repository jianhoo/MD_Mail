from django.shortcuts import render

# Create your views here.
from itsdangerous import BadData
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet

from contents.crons import generate_static_index_html
from users import serializers
from users.models import User

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view())
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, EmailVerifySerializer


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
        # generate_static_index_html()
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


class AddressViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserAddressSerializer

    def list(self, request, *args, **kwargs):
        addresses = self.get_queryset()
        serializer = self.get_serializer(addresses, many=True)
        return Response({
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id,
            'limit': 5,
            'addresses': serializer.data
        })

    def get_queryset(self):
        # 当前登录用户的未删除的收货地址
        return self.request.user.addresses.filter(is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        # 默认实现是物理删除,当前实现逻辑删除
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=204)

    @action(methods=['put'], detail=True)
    def title(self, request, pk):
        # 接收请求报文中的标题
        title = request.data.get('title')
        # 修改对象的属性
        address = self.get_object()
        address.title = title
        address.save()
        return Response({'title': title})

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        # 获取当前登录的用户
        user = self.request.user
        # 修改这个用户的默认收货地址
        user.default_address_id = pk
        user.save()
        return Response({'message': 'OK'})

