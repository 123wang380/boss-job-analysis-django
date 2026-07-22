from .getPublicData import *
from myApp.models import JobInfo
from django.db.models import Q
import json


def getSearchResults(keyword, salary_range, education, experience, city, order_by):
    """职位高级搜索"""
    qs = JobInfo.objects.all()

    # 关键词搜索（职位名称、公司名称、技能标签）
    if keyword:
        qs = qs.filter(
            Q(title__icontains=keyword) |
            Q(companyTitle__icontains=keyword) |
            Q(workTag__icontains=keyword) |
            Q(type__icontains=keyword)
        )

    # 学历筛选
    if education and education != '不限':
        qs = qs.filter(educational=education)

    # 经验筛选
    if experience and experience != '不限':
        qs = qs.filter(workExperience=experience)

    # 城市筛选
    if city and city != '不限':
        qs = qs.filter(address=city)

    # 处理薪资范围筛选（需要在Python层面做，因为salary是JSON字段）
    results = []
    for job in qs:
        try:
            salary_data = json.loads(job.salary)
            if job.pratice == 0:
                salary_val = salary_data[1] if len(salary_data) > 1 else 0
            else:
                salary_val = 0  # 实习岗位不按正式薪资筛选
        except:
            salary_val = 0

        # 薪资范围筛选
        if salary_range and salary_range != '不限':
            if salary_range == '0-10k' and salary_val >= 10000:
                continue
            elif salary_range == '10-20k' and (salary_val < 10000 or salary_val >= 20000):
                continue
            elif salary_range == '20-30k' and (salary_val < 20000 or salary_val >= 30000):
                continue
            elif salary_range == '30-40k' and (salary_val < 30000 or salary_val >= 40000):
                continue
            elif salary_range == '40k以上' and salary_val < 40000:
                continue

        # 处理显示数据（元转K）
        job.salary_display = round(salary_val / 1000, 1)
        job.workTag_display = ' / '.join(json.loads(job.workTag)) if job.workTag else ''
        if job.companyTags != '无' and job.companyTags:
            try:
                job.companyTags_display = json.loads(job.companyTags)[0]
            except:
                job.companyTags_display = job.companyTags
        else:
            job.companyTags_display = '无'
        results.append(job)

    # 排序
    if order_by == 'salary_desc':
        results.sort(key=lambda x: x.salary_display, reverse=True)
    elif order_by == 'salary_asc':
        results.sort(key=lambda x: x.salary_display)
    elif order_by == 'date_desc':
        results.sort(key=lambda x: x.createTime, reverse=True)

    return results


def getFilterOptions():
    """获取筛选选项"""
    jobs = getAllJobs()
    cities = list(set([j.address for j in jobs if j.address]))
    cities.sort()
    return list(educations.keys()), workExperience, cities, salaryList
