from django.contrib import admin
from myApp.models import JobInfo, User, History, LoginLog, VerifyCode

class JobManager(admin.ModelAdmin):
    list_display = ["id","title", "address", "type", "educational", "workExperience", "salary",
                     "companyTitle", "companyNature", "companyStatus", "createTime"]
    list_display_links = ["title"]
    list_filter = ['type', 'address', 'educational']
    search_fields = ['title', 'companyTitle']
    list_per_page = 20
    date_hierarchy = 'createTime'

class UserManager(admin.ModelAdmin):
    list_display = ["id", 'username', 'phone', 'is_active', 'address', 'educational', 'work', 'createTime']
    list_display_links = ["username"]
    list_filter = ['is_active', 'educational', 'address']
    search_fields = ['username', 'phone']
    list_editable = ['is_active']
    list_per_page = 20
    date_hierarchy = 'createTime'

class HistoryManager(admin.ModelAdmin):
    list_display = ["id", "job", "user", "count"]

class LoginLogManager(admin.ModelAdmin):
    list_display = ["id", "user", "login_time", "ip_address", "login_type"]
    list_filter = ['login_type']
    search_fields = ['user__username']
    date_hierarchy = 'login_time'
    list_per_page = 30

class VerifyCodeManager(admin.ModelAdmin):
    list_display = ["id", "phone", "code", "create_time", "is_used"]
    list_filter = ['is_used']
    list_per_page = 30

admin.site.register(JobInfo, JobManager)
admin.site.register(User, UserManager)
admin.site.register(History, HistoryManager)
admin.site.register(LoginLog, LoginLogManager)
admin.site.register(VerifyCode, VerifyCodeManager)
