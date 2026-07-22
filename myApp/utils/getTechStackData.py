from .getPublicData import *
from myApp.models import JobInfo
import json
from collections import Counter


def getTechStats():
    """统计所有技术标签出现频率"""
    jobs = getAllJobs()
    tech_counter = Counter()
    tech_salary = {}  # 每种技术的平均薪资

    for job in jobs:
        try:
            tags = json.loads(job.workTag)
        except:
            continue
        if not tags:
            continue
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            tech_counter[tag] += 1
            # 记录薪资用于计算平均
            try:
                salary_data = json.loads(job.salary)
                if job.pratice == 0:
                    s = salary_data[1] if len(salary_data) > 1 else 0
                else:
                    s = 0
            except:
                s = 0
            if tag not in tech_salary:
                tech_salary[tag] = []
            tech_salary[tag].append(s)

    # 取前30个热门技术
    top_techs = tech_counter.most_common(30)
    max_count = top_techs[0][1] if top_techs else 1

    tech_names = []
    tech_counts = []
    tech_avg_salaries = []
    tech_list = []  # 用于模板直接遍历
    for name, count in top_techs:
        tech_names.append(name)
        tech_counts.append(count)
        salaries = tech_salary.get(name, [0])
        avg_s = round(sum(salaries) / len(salaries) / 1000, 1) if salaries else 0
        tech_avg_salaries.append(avg_s)
        # 用于表格展示的结构化数据
        tech_list.append({
            'name': name,
            'count': count,
            'avg_salary': avg_s,
            'pct': round(count / max_count * 100, 1)
        })

    return tech_names, tech_counts, tech_avg_salaries, tech_list, max_count


def getTechByCategory(category):
    """按职位类别分析技术需求"""
    if category == 'all':
        jobs = getAllJobs()
    else:
        jobs = JobInfo.objects.filter(type=category)

    tech_counter = Counter()
    for job in jobs:
        try:
            tags = json.loads(job.workTag)
        except:
            continue
        if not tags:
            continue
        for tag in tags:
            tag = tag.strip()
            if tag:
                tech_counter[tag] += 1

    return tech_counter.most_common(20)


def getJobCategories():
    """获取所有职位类别"""
    jobs = getAllJobs()
    categories = list(set([j.type for j in jobs if j.type]))
    categories.sort()
    return categories
