from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer


def dumps(data_dict, expires):
    serializer = TJWSSerializer(settings.SECRET_KEY, expires)
    return serializer.dumps(data_dict).decode()


def loads(data_str, expires):
    serializer = TJWSSerializer(settings.SECRET_KEY, expires)
    try:
        data_dict = serializer.loads(data_str)
    except:
        return None
    else:
        return data_dict
