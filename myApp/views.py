from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from myApp.models import User, JobInfo, LoginLog
from .utils.error import *
import hashlib
from .utils import getHomeData,getSelfInfo,getChangePasswordData,getTableData,getHisotryData
from .utils import getSalaryCharData,getCompanyCharData,getEducationalCharData
from .utils import getCompanyStatusCharData,getAddressCharData
from .utils import getSearchData, getTechStackData, getExportData
from .utils.sms_utils import generate_code, verify_code
from .utils.boss_utils import generate_boss_search_url, get_boss_job_url
from . import word_cloud_picture
import random
from datetime import datetime

def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    else:
        uname = request.POST.get('username','').strip()
        pwd = request.POST.get('password','')
        if not uname or not pwd:
            return errorResponse(request,'用户名和密码不能为空！')
        md5 = hashlib.md5()
        md5.update(pwd.encode())
        pwd = md5.hexdigest()
        try:
            user = User.objects.get(username=uname,password=pwd)
            if not user.is_active:
                return errorResponse(request,'该账号已被禁用，请联系管理员！')
            request.session['username'] = user.username
            _log_login(user, request, 'password')
            return redirect('/myApp/home/')
        except User.DoesNotExist:
            return errorResponse(request,'用户名或密码出错！')

def registry(request):
    if request.method == 'GET':
        return render(request,'registry.html')
    else:
        uname = request.POST.get('username','').strip()
        pwd = request.POST.get('password','')
        checkPwd = request.POST.get('checkPassword','')
        # 验证输入
        if not uname or not pwd or not checkPwd:
            return errorResponse(request,'用户名和密码不允许为空！')
        if pwd != checkPwd:
            return errorResponse(request,'两次密码不一致，请重新输入！')
        # 检查用户名是否已存在
        if User.objects.filter(username=uname).exists():
            return errorResponse(request,'该用户名已经被注册！')
        # 创建新用户
        md5 = hashlib.md5()
        md5.update(pwd.encode())
        pwd_hash = md5.hexdigest()
        User.objects.create(username=uname, password=pwd_hash)
        # 注册成功后自动登录，直接跳转首页
        request.session['username'] = uname
        return redirect('/myApp/home')

def logOut(request):
    request.session.clear()
    return redirect('login')

def home(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    yea,month,day = getHomeData.getNowTime()
    userCreateData = getHomeData.getUserCreateTime()
    top6Users = getHomeData.getUserTop6()
    jobsLen,usersLen,educationsTop,salaryTop,addressTop,salaryMonthTop,praticeMax = getHomeData.getAllTags()
    jobsPBarData = getHomeData.getAllJobsPBar()
    tablaData = getHomeData.getTablaData()
    # 获取最近数据更新日期
    last_job = JobInfo.objects.order_by('-createTime').first()
    last_update = str(last_job.createTime) if last_job else '暂无数据'
    return render(request,'home.html',{
        'userInfo':userInfo,
        'dateInfo':{
            'year':yea,
            'month':month,
            'day':day
        },
        'last_update': last_update,
        'userCreateData':userCreateData,
        'top6Users':top6Users,
        'tagDic':{
            'jobsLen':jobsLen,
            'usersLen':usersLen,
            'educationsTop':educationsTop,
            'salaryTop':salaryTop,
            'addressTop':addressTop,
            'salaryMonthTop':salaryMonthTop,
            "praticeMax":praticeMax
        },
        'jobsPBarData':jobsPBarData,
        'tableData':tablaData
    })

def selfInfo(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    educations,workExperience,jobList = getSelfInfo.getPageData()
    if request.method == 'POST':
        getSelfInfo.changeSelfInfo(request.POST,request.FILES)
        userInfo = User.objects.get(username=uname)
    return render(request,'selfInfo.html',{
        'userInfo':userInfo,
        'pageData':{
            'educations':educations,
            'workExperience':workExperience,
            'jobList':jobList
        }
    })

def selfInfo_redirect(request, extra=None):
    # 将 /myApp/selfInfo/xxx 形式的错误URL重定向到正确的个人信息页
    return redirect('selfInfo')

def changePassword(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    if request.method == 'POST':
        res = getChangePasswordData.changePassword(userInfo,request.POST)
        if res != None:
            return errorResponse(request,res)
        userInfo = User.objects.get(username=uname)
    return render(request, 'changePassword.html', {
        'userInfo': userInfo
    })

def tableData(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    tableData = getTableData.getTableData()
    paginator = Paginator(tableData,10)
    cur_page = 1
    if request.GET.get('page'):cur_page = int(request.GET.get('page'))
    c_page = paginator.page(cur_page)

    page_range = []
    visibleNumber = 10
    min = int(cur_page - visibleNumber / 10)
    if min < 1:
        min = 1
    max = min + visibleNumber
    if max > paginator.page_range[-1]:
        max = paginator.page_range[-1]
    for i in range(min,max):
        page_range.append(i)

    return render(request,'tableData.html',{
        'userInfo':userInfo,
        'c_page':c_page,
        'page_range':page_range,
        'paginator':paginator
    })

def historyTableData(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    historyData = getHisotryData.getHisotryData(userInfo)
    return render(request,'historyTableData.html',{
        'userInfo':userInfo,
        'historyData':historyData
    })

def addHistory(request,jobId):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    getHisotryData.addHistory(userInfo,jobId)
    return redirect('historyTableData')

def removeHisotry(request,hisId):
    getHisotryData.removeHisotry(hisId)
    return redirect('historyTableData')

def salary(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    educations,workExperiences = getSalaryCharData.getPageData()
    defaultEducation = '不限'
    defaultWorkExperience = '不限'
    if request.GET.get('educational'):defaultEducation = request.GET.get('educational')
    if request.GET.get('workExperience'):defaultWorkExperience = request.GET.get('workExperience')
    salaryList,barData,legends = getSalaryCharData.getBarData(defaultEducation,defaultWorkExperience)
    pieData = getSalaryCharData.pieData()
    louDouData = getSalaryCharData.getLouDouData()
    return render(request,'salaryChar.html',{
        'userInfo':userInfo,
        'educations':educations,
        'workExperiences':workExperiences,
        'defaultEducation':defaultEducation,
        'defaultWorkExperience':defaultWorkExperience,
        'salaryList':salaryList,
        'barData':barData,
        'legends':legends,
        'pieData':pieData,
        'louDouData':louDouData
    })

def company(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    typeList = getCompanyCharData.getPageData()
    type = 'all'
    if request.GET.get('type'):type = request.GET.get('type')
    rowBarData,columnBarData = getCompanyCharData.getCompanyBar(type)
    pieData = getCompanyCharData.getCompanyPie(type)
    companyPeople,lineData = getCompanyCharData.getCompanPeople(type)
    return render(request, 'companyChar.html', {
        'userInfo': userInfo,
        'typeList':typeList,
        "type":type,
        "rowBarData":rowBarData,
        "columnBarData":columnBarData,
        'pieData':pieData,
        "companyPeople":companyPeople,
        "lineData":lineData
    })

def companTags(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    return render(request, 'companyTags.html', {
        'userInfo': userInfo
    })

def educational(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    defaultEducation = '不限'
    if request.GET.get('educational') :defaultEducation = request.GET.get('educational')
    educations = getEducationalCharData.getPageData()
    workExperiences,charDataColumnOne,charDataColumnTwo,hasEmpty = getEducationalCharData.getExpirenceData(defaultEducation)
    barDataRow,barDataColumn = getEducationalCharData.getPeopleData()
    return render(request, 'educationalChar.html', {
        'userInfo': userInfo,
        'educations':educations,
        'defaultEducation':defaultEducation,
        'workExperiences':workExperiences,
        'charDataColumnOne':charDataColumnOne,
        'charDataColumnTwo':charDataColumnTwo,
        'hasEmpty':hasEmpty,
        'barDataRow':barDataRow,
        'barDataColumn':barDataColumn
    })

def companyStatus(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    defaultType = '不限'
    if request.GET.get('type'): defaultType = request.GET.get('type')
    typeList = getCompanyStatusCharData.getPageData()
    teachnologyRow,teachnologyColumn = getCompanyStatusCharData.getTechnologyData(defaultType)
    companyStatusData = getCompanyStatusCharData.getCompanyStatusData()
    return render(request, 'companyStatusChar.html', {
        'userInfo': userInfo,
        'typeList':typeList,
        'defaultType':defaultType,
        'teachnologyRow':teachnologyRow,
        'teachnologyColumn':teachnologyColumn,
        'companyStatusData':companyStatusData
    })

def address(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    defaultCity = '北京'
    if request.GET.get('city'):defaultCity = request.GET.get('city')
    hotCities = getAddressCharData.getPageData()
    salaryRows,salaryColumns = getAddressCharData.getSalaryData(defaultCity)
    companyPeopleData = getAddressCharData.companyPeopleData(defaultCity)
    educationData = getAddressCharData.getEducationData(defaultCity)
    distData = getAddressCharData.getDistData(defaultCity)
    import hashlib
    cache_key = hashlib.md5(defaultCity.encode()).hexdigest()
    word_cloud_picture.get_img('companyTags','./static/3.png','./static/wc_' + cache_key + '.png')
    return render(request, 'addressChar.html', {
        'userInfo': userInfo,
        'hotCities':hotCities,
        'defaultCity':defaultCity,
        'salaryRows':salaryRows,
        'salaryColumns':salaryColumns,
        'companyPeopleData':companyPeopleData,
        'educationData':educationData,
        'distData':distData,
        'url':'wc_' + cache_key
    })


# ========== 新增功能：职位搜索 ==========
def search(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)

    keyword = request.GET.get('keyword', '')
    salary_range = request.GET.get('salary', '不限')
    education = request.GET.get('education', '不限')
    experience = request.GET.get('experience', '不限')
    city = request.GET.get('city', '不限')
    order_by = request.GET.get('order', 'date_desc')
    page = int(request.GET.get('page', 1))

    results = getSearchData.getSearchResults(keyword, salary_range, education, experience, city, order_by)
    educations_list, workExperiences, cities_list, salary_ranges = getSearchData.getFilterOptions()

    # 手动分页
    page_size = 15
    total = len(results)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    page_results = results[start:end]

    # 分页导航
    page_range = []
    visible = 10
    p_min = max(1, page - visible // 2)
    p_max = min(total_pages, p_min + visible - 1)
    p_min = max(1, p_max - visible + 1)
    for i in range(p_min, p_max + 1):
        page_range.append(i)

    # 生成BOSS直聘搜索链接
    boss_search_url = generate_boss_search_url(
        keyword=keyword, city=city, education=education, experience=experience
    )

    return render(request, 'search.html', {
        'userInfo': userInfo,
        'results': page_results,
        'total': total,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'start_index': (page - 1) * page_size,
        'keyword': keyword,
        'salary_range': salary_range,
        'education': education,
        'experience': experience,
        'city': city,
        'order_by': order_by,
        'educations': educations_list,
        'workExperiences': workExperiences,
        'cities': cities_list,
        'salary_ranges': salary_ranges,
        'boss_search_url': boss_search_url,
    })


# ========== 新增功能：技术栈分析 ==========
def techstack(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)

    category = request.GET.get('category', 'all')
    categories = getTechStackData.getJobCategories()

    tech_names, tech_counts, tech_avg_salaries, tech_list, max_count = getTechStackData.getTechStats()
    category_techs = getTechStackData.getTechByCategory(category)

    return render(request, 'techstack.html', {
        'userInfo': userInfo,
        'tech_names': tech_names,
        'tech_counts': tech_counts,
        'tech_avg_salaries': tech_avg_salaries,
        'tech_list': tech_list,
        'max_count': max_count,
        'categories': categories,
        'category': category,
        'category_techs': category_techs,
    })


# ========== 新增功能：数据导出Excel ==========
def exportExcel(request):
    excel_file = getExportData.export_jobs_to_excel()
    file_data = excel_file.getvalue()
    response = HttpResponse(file_data,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="招聘数据_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    response['Content-Length'] = len(file_data)
    return response


# ========== 辅助：记录登录日志 ==========
def _log_login(user, request, login_type='password'):
    ip = request.META.get('REMOTE_ADDR', '')
    LoginLog.objects.create(user=user, ip_address=ip, login_type=login_type)


# ========== 新增：发送验证码 ==========
def sendCode(request):
    phone = request.POST.get('phone', '').strip()
    if not phone or len(phone) != 11:
        return JsonResponse({'success': False, 'msg': '请输入正确的手机号'})
    code = generate_code(phone)
    if code is None:
        return JsonResponse({'success': False, 'msg': '验证码已发送，请1分钟后再试'})
    # 演示环境：验证码直接返回（实际项目只发短信不返回）
    return JsonResponse({'success': True, 'msg': '验证码已发送', 'demo_code': code})


# ========== 新增：手机号验证码登录 ==========
def phoneLogin(request):
    if request.method == 'GET':
        return render(request, 'phone_login.html')
    phone = request.POST.get('phone', '').strip()
    code = request.POST.get('code', '').strip()
    if not phone or not code:
        return errorResponse(request, '手机号和验证码不能为空！')
    # 演示环境：支持万能验证码1234
    if code == '1234' or verify_code(phone, code):
        user = User.objects.filter(phone=phone).first()
        if not user:
            # 新用户自动注册
            uname = 'user_' + phone[-6:]
            # 避免用户名重复
            while User.objects.filter(username=uname).exists():
                uname = 'user_' + phone[-6:] + str(random.randint(10, 99))
            user = User.objects.create(username=uname, phone=phone)
        if not user.is_active:
            return errorResponse(request, '该账号已被禁用，请联系管理员')
        request.session['username'] = user.username
        _log_login(user, request, 'phone')
        return redirect('/myApp/home')
    return errorResponse(request, '验证码错误或已过期！')


# ========== 新增：忘记密码 ==========
def forgotPassword(request):
    if request.method == 'GET':
        return render(request, 'forgot_password.html')
    phone = request.POST.get('phone', '').strip()
    code = request.POST.get('code', '').strip()
    new_pwd = request.POST.get('newPassword', '')
    if not phone or not code or not new_pwd:
        return errorResponse(request, '请填写完整信息！')
    if len(new_pwd) < 6:
        return errorResponse(request, '密码长度不能少于6位！')
    if code == '1234' or verify_code(phone, code):
        user = User.objects.filter(phone=phone).first()
        if not user:
            return errorResponse(request, '该手机号未注册！')
        md5 = hashlib.md5()
        md5.update(new_pwd.encode())
        user.password = md5.hexdigest()
        user.save()
        return redirect('/myApp/login/')
    return errorResponse(request, '验证码错误或已过期！')


# ========== 新增：账号注销 ==========
def deleteAccount(request):
    uname = request.session.get('username')
    if not uname:
        return redirect('login')
    user = User.objects.get(username=uname)
    if request.method == 'POST':
        pwd = request.POST.get('password', '')
        md5 = hashlib.md5()
        md5.update(pwd.encode())
        if md5.hexdigest() == user.password:
            user.is_active = False
            user.save()
            request.session.clear()
            return redirect('/myApp/login/')
        return errorResponse(request, '密码错误，注销失败！')
    return render(request, 'delete_account.html', {'userInfo': user})


# ========== 新增：隐私协议页面 ==========
def privacyPolicy(request):
    return render(request, 'privacy_policy.html')


# ========== 新增：用户服务协议页面 ==========
def userAgreement(request):
    return render(request, 'user_agreement.html')


# ========== 新增：账号安全中心 ==========
def accountSecurity(request):
    uname = request.session.get('username')
    if not uname:
        return redirect('login')
    user = User.objects.get(username=uname)
    # 手机号脱敏
    phone_masked = user.phone[:3] + '****' + user.phone[-4:] if len(user.phone) == 11 else '未绑定'
    # 登录记录
    logs = LoginLog.objects.filter(user=user).order_by('-login_time')[:10]
    return render(request, 'account_security.html', {
        'userInfo': user,
        'phone_masked': phone_masked,
        'login_logs': logs,
    })


# ========== 新增：绑定/修改手机号 ==========
def bindPhone(request):
    uname = request.session.get('username')
    if not uname:
        return redirect('login')
    user = User.objects.get(username=uname)
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        code = request.POST.get('code', '').strip()
        if not phone or not code:
            return errorResponse(request, '手机号和验证码不能为空！')
        if code == '1234' or verify_code(phone, code):
            if User.objects.filter(phone=phone).exclude(id=user.id).exists():
                return errorResponse(request, '该手机号已被其他账号绑定！')
            user.phone = phone
            user.save()
            return redirect('/myApp/accountSecurity/')
        return errorResponse(request, '验证码错误或已过期！')
    return render(request, 'bind_phone.html', {'userInfo': user})


# ========== 内部详情页 ==========
def jobDetail(request, jobId):
    """岗位详情页（系统内部）"""
    uname = request.session.get('username')
    if not uname:
        return redirect('login')
    userInfo = User.objects.get(username=uname)
    try:
        job = JobInfo.objects.get(id=jobId)
    except JobInfo.DoesNotExist:
        return errorResponse(request, '抱歉，该岗位不存在！')
    import json
    try:
        job.salary = json.loads(job.salary)
    except (json.JSONDecodeError, TypeError):
        job.salary = [0, 0]
    try:
        job.companyPeople = json.loads(job.companyPeople)
        if job.companyPeople == [0, 10000]:
            job.companyPeople = '10000人以上'
        elif len(job.companyPeople) == 2:
            job.companyPeople = f'{job.companyPeople[0]}-{job.companyPeople[1]}人'
        else:
            job.companyPeople = '未知'
    except:
        job.companyPeople = '未知'
    try:
        job.workTag = json.loads(job.workTag)
    except:
        job.workTag = []
    if job.companyTags != '无':
        try:
            job.companyTags = json.loads(job.companyTags)[0].split('，')
        except:
            job.companyTags = ['无']
    # 薪资格式化
    if not job.pratice:
        job.salary = '-'.join([str(int(x/1000)) for x in job.salary]) + 'K'
        if job.salaryMonth != '0':
            job.salary += f' · {job.salaryMonth}薪'
    else:
        job.salary = '-'.join([str(x) for x in job.salary]) + '元/天'
    return render(request, 'job_detail.html', {
        'userInfo': userInfo,
        'job': job,
    })


def companyDetail(request, jobId):
    """公司详情页 - 展示该公司所有岗位"""
    uname = request.session.get('username')
    if not uname:
        return redirect('login')
    userInfo = User.objects.get(username=uname)
    try:
        job = JobInfo.objects.get(id=jobId)
    except JobInfo.DoesNotExist:
        return errorResponse(request, '抱歉，该公司不存在！')
    company_jobs = JobInfo.objects.filter(companyTitle=job.companyTitle)
    import json
    for j in company_jobs:
        try:
            j.salary = json.loads(j.salary)
        except:
            j.salary = [0, 0]
        if not j.pratice:
            j.salary = '-'.join([str(int(x/1000)) for x in j.salary]) + 'K'
        else:
            j.salary = '-'.join([str(x) for x in j.salary]) + '元/天'
        try:
            j.workTag = json.loads(j.workTag)
        except:
            j.workTag = []
    return render(request, 'company_detail.html', {
        'userInfo': userInfo,
        'company': job,
        'jobs': company_jobs,
    })


# ========== API：BOSS直聘实时搜索 ==========
def api_boss_search(request):
    """
    BOSS直聘实时搜索API
    GET参数：
        keyword - 搜索关键词（必填）
        city - 城市名称（选填，默认"全国"）
        page - 页码（选填，默认1）
    返回：JSON
    """
    uname = request.session.get('username')
    if not uname:
        return JsonResponse({'success': False, 'error': '请先登录'}, status=401)

    keyword = request.GET.get('keyword', '').strip()
    if not keyword:
        return JsonResponse({'success': False, 'error': '请输入搜索关键词'})

    city = request.GET.get('city', '全国').strip()
    page = int(request.GET.get('page', 1))

    # 获取城市代码
    from .utils.boss_utils import get_city_code
    city_code = get_city_code(city)

    # 执行实时搜索
    try:
        import sys
        import os
        spider_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'spider'
        )
        if spider_path not in sys.path:
            sys.path.insert(0, spider_path)

        from boss_live_search import BossLiveSearch

        searcher = BossLiveSearch(headless=True)
        try:
            result = searcher.search(keyword, city_code=city_code, page=page, max_results=15)
        finally:
            searcher.close()

        return JsonResponse(result)

    except FileNotFoundError as e:
        return JsonResponse({
            'success': False,
            'error': 'ChromeDriver未找到，请确保 chromedriver.exe 在 spider 目录下',
            'detail': str(e),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'搜索失败：{str(e)}',
        })