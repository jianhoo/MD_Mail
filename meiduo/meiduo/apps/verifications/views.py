import random

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms_code

# url('^sms_code/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view())
from verifications import constants


class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        发送短信验证码
        :param request: 请求对象,不需要传递
        :param mobile: 手机号,需要传递
        :return: 是否发送成功
        """
        # 数据保存在redis中,获取redis连接
        redis_client = get_redis_connection('sms_code')
        # 判断手机号60秒内是否发送过短信,如果已经发送则不发送
        sms_flag = redis_client.get('sms_flag_' + mobile)
        if sms_flag:
            raise exceptions.ValidationError('发送验证码太频繁,请稍后重试')

        # 随机生成6位的验证码
        sms_code = random.randint(100000, 999999)

        # 使用管道方式交互redis
        redis_pipeline = redis_client.pipeline()
        # 保存验证码
        redis_pipeline.setex('sms_code_' + mobile, constants.SMS_CODE_EXPIRES, sms_code)
        # 保存60秒发送标记
        redis_pipeline.setex('sms_flag_' + mobile, constants.SMS_FLAG_EXPIRES, 1)
        # 执行
        redis_pipeline.execute()

        # 发送短信验证码
        sms_code_expires = str(constants.SMS_CODE_EXPIRES // 60)
        send_sms_code.delay(mobile, sms_code, sms_code_expires, 1)

        return Response({'message': 'OK'})
