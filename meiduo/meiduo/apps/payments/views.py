from rest_framework.views import APIView
from rest_framework.response import Response
from alipay import AliPay
from django.conf import settings
from orders.models import OrderInfo
from .models import Payment


class PayUrlView(APIView):
    def get(self, request, order_id):
        # 查询订单对象
        try:
            order = OrderInfo.objects.get(pk=order_id)
        except:
            raise Exception('订单编号无效')

        # 1.创建支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=settings.ALIPAY_PRIVATE_KEY_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
            sign_type=settings.ALIPAY_SIGN_TYPE,
            debug=settings.ALIPAY_DEBUG
        )
        # 2.调用方法，构造支付地址
        order_string = alipay.api_alipay_trade_page_pay(
            subject='美多商城-订单支付',
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            return_url=settings.ALIPAY_NOTIFY_URL
        )
        # 3.返回支付链接地址
        alipay_url = settings.ALIPAY_GATE + order_string
        return Response({'alipay_url': alipay_url})


class OrderStatusView(APIView):
    def put(self, request):
        # 1.接收支付宝返回的数据
        aliay_dict = request.query_params.dict()
        # 2.验证是否支付成功
        signature = aliay_dict.pop('sign')
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=settings.ALIPAY_PRIVATE_KEY_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
            sign_type=settings.ALIPAY_SIGN_TYPE,
            debug=settings.ALIPAY_DEBUG
        )
        success = alipay.verify(aliay_dict, signature)
        # print(aliay_dict)
        if success:
            # 3.如果支付成功
            # 3.1修改订单状态
            order_id = aliay_dict.get('out_trade_no')
            try:
                order = OrderInfo.objects.get(pk=order_id)
            except:
                raise Exception('订单编号无效')
            else:
                order.status = 2
                order.save()
            # 3.2创建订单支付对象
            Payment.objects.create(
                order_id=order_id,
                trade_id=aliay_dict.get('trade_no')
            )
            return Response({'trade_id': aliay_dict.get('trade_no')})
        else:
            return Response({'message': '支付失败'})
