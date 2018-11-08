from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from itsdangerous import BadData
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from carts.utils import merge_cart_cookie_to_redis
from contents.crons import generate_static_index_html
from goods.models import SKU
from goods.serializers import SKUSerializer
from users import serializers, constants
from users.models import User

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view())
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, EmailVerifySerializer, \
    AddUserBrowsingHistorySerializer


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


class UserBrowsingHistoryView(CreateAPIView):
    """
    # 用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取
        """
        user_id = request.user.id

        redis_conn = get_redis_connection("history")
        history = redis_conn.lrange("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)
        skus = []
        # 为了保持查询的顺序与用户的浏览历史保存顺序一致
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        s = SKUSerializer(skus, many=True)
        return Response(s.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """
    用户认证
    """
    def post(self, request, *args, **kwargs):
        # 调用父类的方法，获取drf jwt扩展默认的认证用户处理结果
        response = super().post(request, *args, **kwargs)
        # 仿照drf jwt扩展对于用户登录的认证方式，判断用户是否认证登录成功
        # 如果用户登录认证成功，则合并购物车
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, user, response)

        return response



