from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from users import constants
from utils import tjws


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱认证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        data = {'user_id': self.id, 'email':self.email}
        token = tjws.dumps(data, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token


