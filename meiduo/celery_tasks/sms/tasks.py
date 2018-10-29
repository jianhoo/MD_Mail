import logging

from celery_tasks.main import app
from meiduo.utils.ytx_sdk.cpp import CCP

logger = logging.getLogger("django")


@app.task
def send_sms_code(mobile, code, expires, template_id):
    """
    发送短信验证码
    :param mobile:  手机号
    :param code:    验证码
    :param expires: 有效期
    :param template_id:
    :return:
    """

    try:
        ccp = CCP()
        # result = ccp.send_template_sms(mobile, {code, expires}, template_id)
        result = 0
        print(code)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            print(result)
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)