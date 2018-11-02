from fdfs_client.client import Fdfs_client

client = Fdfs_client('client.conf')

ret = client.upload_by_filename('/Users/huangjianhao/Desktop/1.jpg')
print(ret)
