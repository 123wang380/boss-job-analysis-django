import random
from django.utils import timezone
from datetime import timedelta
from myApp.models import VerifyCode


def generate_code(phone):
    """生成6位验证码并保存到数据库（模拟发送短信）"""
    one_min_ago = timezone.now() - timedelta(minutes=1)
    recent = VerifyCode.objects.filter(phone=phone, create_time__gte=one_min_ago, is_used=False)
    if recent.exists():
        return None

    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    VerifyCode.objects.create(phone=phone, code=code)
    print(f'\n[短信验证码] 手机号:{phone} 验证码:{code}\n')
    return code


def verify_code(phone, code):
    """验证验证码是否有效（5分钟内有效）"""
    five_min_ago = timezone.now() - timedelta(minutes=5)
    vc = VerifyCode.objects.filter(
        phone=phone, code=code, is_used=False,
        create_time__gte=five_min_ago
    ).order_by('-create_time').first()
    if vc:
        vc.is_used = True
        vc.save()
        return True
    return False
