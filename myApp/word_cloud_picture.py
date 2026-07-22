import json
import os
import jieba
import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np
from myApp.models import JobInfo


# 自动查找系统中可用的中文字体
def _get_font_path():
    font_names = ['STHUPO.TTF', 'simhei.ttf', 'msyh.ttc']
    font_dirs = ['C:/Windows/Fonts', '/usr/share/fonts', '/System/Library/Fonts']
    for font_dir in font_dirs:
        if os.path.isdir(font_dir):
            for font_name in font_names:
                font_path = os.path.join(font_dir, font_name)
                if os.path.isfile(font_path):
                    return font_path
    # 如果找不到中文字体，使用matplotlib自带的字体目录
    mpl_font_dir = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
    if os.path.isdir(mpl_font_dir):
        for fn in os.listdir(mpl_font_dir):
            if fn.lower().endswith('.ttf'):
                return os.path.join(mpl_font_dir, fn)
    return 'STHUPO.TTF'


def get_img(field, targetImageSrc, resImageSrc):
    # 使用Django ORM替代直接的MySQL连接
    data = JobInfo.objects.values_list(field, flat=True).all()
    text = ''
    for item in data:
        if item and item != '无':
            try:
                companyTagsArr = json.loads(item)[0].split('，')
                for j in companyTagsArr:
                    text += j
            except (json.JSONDecodeError, IndexError, TypeError):
                pass

    # jieba分词后生成词云
    data_cut = jieba.cut(text, cut_all=False)
    string = ' '.join(data_cut)

    img = Image.open(targetImageSrc)
    img_arr = np.array(img)
    wc = WordCloud(
        background_color='white',
        mask=img_arr,
        font_path=_get_font_path()
    )
    wc.generate_from_text(string)

    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off')
    plt.savefig(resImageSrc, dpi=800)
    plt.close(fig)
