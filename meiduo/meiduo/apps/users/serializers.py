import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users import constants
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_email
from meiduo.utils import tjws


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


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()

        verify_url = instance.generate_verify_email_url()
        send_verify_email.delay(instance.email, verify_url)

        return instance


class EmailVerifySerializer(serializers.Serializer):
    # 接收激活参数
    token = serializers.CharField(max_length=200)

    # 验证激活参数是否有效
    def validate_token(self, value):
        # 用validate_data形式校验,获取到的value是一个字符串,不是字典!,当return返回一个字符串
        # 后,重新放进字典中,传给create方法和update方法,所有下面的create方法中是用过字典获取键
        # token的值
        data_dict = tjws.loads(value, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        if data_dict is None:
            raise serializers.ValidationError('链接信息无效')

        return data_dict.get('user_id')

    def create(self, validated_data):
        user = User.objects.get(pk=validated_data.get('token'))
        user.email_active = True
        user.save()
        return user


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

