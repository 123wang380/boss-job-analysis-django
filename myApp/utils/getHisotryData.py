from .getPublicData import *
from myApp.models import History
from django.db.models import F
import json


def addHistory(userInfo, jobId):
    hisData = History.objects.filter(user=userInfo, job_id=jobId)
    if hisData.exists():
        hisData.update(count=F('count') + 1)
    else:
        History.objects.create(user=userInfo, job_id=jobId)


def getHisotryData(userInfo):
    data = list(History.objects.filter(user=userInfo).order_by('-count'))

    def map_fn(item):
        try:
            # 解析薪资
            try:
                item.job.salary = json.loads(item.job.salary)
            except (json.JSONDecodeError, TypeError):
                item.job.salary = [0, 0]
            # 解析公司人数
            try:
                item.job.companyPeople = json.loads(item.job.companyPeople)
            except (json.JSONDecodeError, TypeError):
                item.job.companyPeople = [0, 0]
            # 解析工作标签
            try:
                item.job.workTag = json.loads(item.job.workTag)
            except (json.JSONDecodeError, TypeError):
                item.job.workTag = []
            # 解析公司福利标签
            if item.job.companyTags != '无':
                try:
                    item.job.companyTags = json.loads(item.job.companyTags)[0].split('，')
                except (json.JSONDecodeError, IndexError, TypeError):
                    item.job.companyTags = ['无']
            # 格式化薪资
            if not item.job.pratice:
                item.job.salary = list(map(
                    lambda x: str(int(x / 1000)), item.job.salary))
            else:
                item.job.salary = list(map(lambda x: str(x), item.job.salary))
            if len(item.job.salary) == 2:
                item.job.salary = '-'.join(item.job.salary)
            elif item.job.salary:
                item.job.salary = str(item.job.salary[0])
            else:
                item.job.salary = '面议'
            # 格式化公司人数
            people = item.job.companyPeople
            if people == [0, 10000]:
                item.job.companyPeople = '10000人以上'
            elif isinstance(people, list) and len(people) == 2:
                item.job.companyPeople = f'{people[0]}-{people[1]}人'
            else:
                item.job.companyPeople = '未知'
        except Exception:
            pass
        return item

    data = list(map(map_fn, data))
    return data


def removeHisotry(hisId):
    from django.shortcuts import get_object_or_404
    his = get_object_or_404(History, id=hisId)
    his.delete()
