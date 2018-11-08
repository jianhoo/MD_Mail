from django.db import models

from meiduo.utils.BaseModel import BaseModel


class Payment(BaseModel):
    order = models.ForeignKey('orders.OrderInfo', verbose_name='订单')
    # 各支付平台返回的唯一编号
    trade_id = models.CharField(max_length=100, verbose_name='支付编号')

    class Meta:
        db_table = 'tb_payments'
        verbose_name = '支付表'
        verbose_name_plural = verbose_name
