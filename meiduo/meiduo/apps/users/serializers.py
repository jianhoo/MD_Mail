import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        min_length=5,
        max_length=20,
        error_messages={
            'min_length': '用户名为5-20个字符',
            'max_length': '用户名为5-20个字符'
        }
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '用户名为5-20个字符',
            'max_length': '用户名为5-20个字符'
        }
    )
    password2 = serializers.CharField(write_only=True)
    mobile = serializers.CharField()
    sms_code = serializers.CharField(write_only=True)
    allow = serializers.CharField(write_only=True)
    # jwt认证字段
    token = serializers.CharField(label='登录状态token', read_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).count() > 0:
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_mobile(self, value):
        if not re.match('^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号码格式错误')
        return value

    def validate_allow(self, value):
        if not value:
            raise serializers.ValidationError('请同意协议')
        return value

    def validate(self, attrs):
        # 短信验证码
        redis_cli = get_redis_connection('sms_code')
        key = 'sms_code_' + attrs.get('mobile')
        sms_code_redis = redis_cli.get(key)
        if not sms_code_redis:
            raise serializers.ValidationError('验证码已过期')
        redis_cli.delete(key)
        sms_code_redis = sms_code_redis.decode()
        sms_code_request = attrs.get('sms_code')
        if sms_code_redis != sms_code_request:
            raise serializers.ValidationError('验证码错误')

        # 密码比对
        pwd1 = attrs.get('password')
        pwd2 = attrs.get('password2')
        if pwd1 != pwd2:
            raise serializers.ValidationError('两次输入的密码不一致')
        return attrs

    def create(self, validated_data):
        user = User()
        user.username = validated_data.get('username')
        user.mobile = validated_data.get('mobile')
        user.set_password(validated_data.get('password'))
        user.save()

        # JWT登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')