import base64
import pickle


def dumps(my_dict):
    # 转化成bytes类型
    json_bytes = pickle.dumps(my_dict)
    # 加密,该方法会多编码一次
    json_64 = base64.b64encode(json_bytes)
    # 因为上面编码了两次,所以需要解码一次
    return json_64.decode()


def loads(my_str):
    json_64 = my_str.encode()
    json_bytes = base64.b64decode(json_64)
    return pickle.loads(json_bytes)
