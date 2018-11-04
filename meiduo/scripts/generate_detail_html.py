#!/usr/bin/env python
# 在当前的环境中查找python解释器的路径
# !/home/python/.virtualenvs/meiduo/bin/python
# 指定python解释器

# 指定当前项目的运行环境
import sys
import os
import django

sys.path.insert(0, '../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo.settings.dev")
django.setup()

from goods.models import SKU
from celery_tasks.html.tasks import generate_static_sku_detail_html

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generate_static_sku_detail_html(sku.id)
    print('ok')
