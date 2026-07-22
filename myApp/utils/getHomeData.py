from .getPublicData import *
import time
import json

def getNowTime():
    timeFormat = time.localtime()
    yer = timeFormat.tm_year
    mon = timeFormat.tm_mon
    day = timeFormat.tm_mday
    return yer,monthList[mon - 1],day

def getUserCreateTime():
    users = getAllUsers()
    data = {}
    for u in users:
        # 按年-月聚合，使饼图数据更丰富
        month_key = str(u.createTime)[:7]  # e.g. "2026-07"
        if data.get(month_key, -1) == -1:
            data[month_key] = 1
        else:
            data[month_key] += 1
    result = []
    for k, v in sorted(data.items()):
        # 转换为中文月份名
        year, month = k.split('-')
        month_name = monthList[int(month) - 1]
        result.append({
            'name': f'{year}年{month_name}',
            'value': v
        })
    return result

def getUserTop6():
    users = getAllUsers()
    def sort_fn(item):
        return time.mktime(time.strptime(str(item.createTime),'%Y-%m-%d'))
    users = list(sorted(users,key=sort_fn,reverse=True))[:6]
    return users

def getAllTags():
    jobs = JobInfo.objects.all()
    users = User.objects.all()
    educationsTop = '学历不限'
    salaryTop = 0
    salaryMonthTop = 0
    address = {}
    pratice = {}
    for job in jobs:
        if educations[job.educational] < educations[educationsTop]:
            educationsTop = job.educational
        if job.pratice == 0:
            salary = json.loads(job.salary)[1]
            if salaryTop < salary:
                salaryTop = salary
        if int(job.salaryMonth) > salaryMonthTop:
            salaryMonthTop = int(job.salaryMonth)
        if address.get(job.address,-1) == -1:
            address[job.address] = 1
        else:
            address[job.address] += 1
        if pratice.get(job.pratice,-1) == -1:
            pratice[job.pratice] = 1
        else:
            pratice[job.pratice] += 1

    addressStr = sorted(address.items(),key=lambda x:x[1],reverse=True)[:3]
    addressTop = ''
    praticeMax = sorted(pratice.items(),key=lambda x:x[1],reverse=True)
    for index,item in enumerate(addressStr):
        if index == len(addressStr) - 1:
            addressTop += item[0]
        else:
            addressTop += item[0] +','

    # 取实习和全职中占比最高的
    if praticeMax and len(praticeMax) > 0:
        most_pratice = praticeMax[0][0]
    else:
        most_pratice = None

    return len(jobs),len(users),educationsTop,salaryTop,addressTop,salaryMonthTop,most_pratice

def getAllJobsPBar():
    jobs = getAllJobs()
    tempData = {}
    for job in jobs:
        if tempData.get(str(job.createTime),-1) == -1:
            tempData[str(job.createTime)] = 1
        else:
            tempData[str(job.createTime)] += 1
    def sort_fn(item):
        item = list(item)
        return time.mktime(time.strptime(str(item[0]),'%Y-%m-%d'))
    result = list(sorted(tempData.items(),key=sort_fn,reverse=False))
    def map_fn(item):
        item = list(item)
        item.append(round(item[1] / len(jobs),3))
        return item
    result = list(map(map_fn,result))
    return result

def getTablaData():
    jobs = getAllJobs()
    for i in jobs:
        i.workTag = '/'.join(json.loads(i.workTag))
        if i.companyTags != "无":
            i.companyTags = "/".join(json.loads(i.companyTags)[0].split('，'))
        if i.companyPeople == '[0,10000]':
            i.companyPeople = '10000人以上'
        else:
            i.companyPeople = json.loads(i.companyPeople)
            i.companyPeople = list(map(lambda x:str(x) + '人',i.companyPeople))
            i.companyPeople = '-'.join(i.companyPeople)
        i.salary = json.loads(i.salary)[1]
    return jobs