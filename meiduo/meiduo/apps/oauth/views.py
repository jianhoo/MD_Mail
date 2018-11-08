from django.shortcuts import render

# Create your views here.

#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from oauth.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.qq_sdk import OAuthQQ
from oauth.serializers import OAuthQQUserSerializer
from meiduo.utils.generate_jwt_token import generate_jwt_token


class QQAuthURLView(APIView):
    """
    获取QQ登录的url
    """

    def get(self, request):
        """
        提供用于QQ登录的url
        """
        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()
        return Response({'login_url': login_url})


class QQAuthUserView(APIView):
    """
    QQ登录的用户
    """
    def get(self, request):
        """
        获取qq登录的用户数据
        :param request:
        :return:
        """
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ()
        # 获取用户openid
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_openid(access_token)
        except QQAPIError:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 判断用户是否存在
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 用户第一次使用QQ登录
            token = oauth.generate_save_user_token(openid)
            return Response({'access_token': token})
        else:
            # 找到用户,生成token
            user = qq_user.user
            token = generate_jwt_token(user)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
            response = merge_cart_cookie_to_redis(request, user, response)
            return response

    def post(self, request):
        serializer = OAuthQQUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = Response({
            'token': user.token,
            'user_id': user.id,
            'username': user.username
        })
        response = merge_cart_cookie_to_redis(request, user, response)

        return response

