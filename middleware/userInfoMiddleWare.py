from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect
import re


class UserMW(MiddlewareMixin):
    # 登录验证中间件：未登录用户自动跳转到登录页
    def process_request(self, request):
        path = request.path_info
        # 无需登录即可访问的路径
        public_paths = [
            '/myApp/login/', '/myApp/registry/', '/myApp/phoneLogin/',
            '/myApp/sendCode/', '/myApp/forgotPassword/',
            '/myApp/privacyPolicy/', '/myApp/userAgreement/',
        ]
        if path in public_paths or re.search('^/admin.*', path):
            return None
        else:
            if not request.session.get('username'):
                return redirect('login')
        return None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        return None

    def process_response(self, request, response):
        return response
