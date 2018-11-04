import os
from django.conf import settings
from django.shortcuts import render

from contents.models import ContentCategory
from meiduo.utils.get_category_list import get_categories


def generate_static_index_html():
    """
    生成静态的主页html文件
    """
    categories = get_categories()

    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    data = {
        'categories': categories,
        'contents': contents
    }

    tem = render(None, 'index.html', data)
    html_text = tem.content.decode()

    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

    print('OK')
