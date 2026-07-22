import os, sys, hashlib

# 添加项目路径，方便在任意目录运行
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '数据可视化分析.settings')

import django
django.setup()
from myApp.models import User


def create(username, password):
    if User.objects.filter(username=username).exists():
        print('用户已存在:', username)
        return
    md5 = hashlib.md5()
    md5.update(password.encode())
    pwd = md5.hexdigest()
    User.objects.create(username=username, password=pwd)
    print('创建用户成功:', username)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python create_user.py <用户名> <密码>')
    else:
        create(sys.argv[1], sys.argv[2])
