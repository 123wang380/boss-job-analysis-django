from django.urls import path,re_path
from myApp import views

urlpatterns = [
    path('login/',views.login,name='login'),
    path('registry/', views.registry, name='registry'),
    path('home/',views.home, name='home'),
    path('logOut/',views.logOut, name='logOut'),
    path('selfInfo/', views.selfInfo, name='selfInfo'),
    # 匹配 selfInfo/xxx 格式的错误URL，重定向到个人信息页
    re_path(r'^selfInfo/.+$', views.selfInfo_redirect),
    path('changePassword/', views.changePassword, name='changePassword'),
    path('tableData/', views.tableData, name='tableData'),
    path('historyTableData/',views.historyTableData,name='historyTableData'),
    path('addHistorys/<int:jobId>', views.addHistory, name='addHistory'),
    path('removeHisotry/<int:hisId>',views.removeHisotry,name='removeHisotry'),
    path('salary/',views.salary,name='salary'),
    path('company/', views.company, name='company'),
    path('companyTags/', views.companTags, name='companTags'),
    path('educational/',views.educational,name='educational'),
    path('companyStatus/', views.companyStatus, name='companyStatus'),
    path('address/', views.address, name='address'),
    # 新增功能
    path('search/', views.search, name='search'),
    path('techstack/', views.techstack, name='techstack'),
    path('exportExcel/', views.exportExcel, name='exportExcel'),
    # 手机验证码登录
    path('sendCode/', views.sendCode, name='sendCode'),
    path('phoneLogin/', views.phoneLogin, name='phoneLogin'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('deleteAccount/', views.deleteAccount, name='deleteAccount'),
    path('privacyPolicy/', views.privacyPolicy, name='privacyPolicy'),
    path('userAgreement/', views.userAgreement, name='userAgreement'),
    path('accountSecurity/', views.accountSecurity, name='accountSecurity'),
    path('bindPhone/', views.bindPhone, name='bindPhone'),
    # 内部详情页
    path('jobDetail/<int:jobId>', views.jobDetail, name='jobDetail'),
    path('companyDetail/<int:jobId>', views.companyDetail, name='companyDetail'),
    # API：BOSS直聘实时搜索
    path('api/boss_search/', views.api_boss_search, name='api_boss_search'),
]