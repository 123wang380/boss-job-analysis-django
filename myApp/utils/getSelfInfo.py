from .getPublicData import *
from myApp.models import User
def getPageData():
    jobs = getAllJobs()
    jobType = {}
    for job in jobs:
        if jobType.get(job.type,-1) == -1:
            jobType[job.type] = 1
        else:
            jobType[job.type] += 1

    return list(educations.keys()),workExperience,list(jobType.keys())

def changeSelfInfo(newInfo,fileInfo):
    user = User.objects.get(username=newInfo.get('username'))
    educational = newInfo.get('educational', '')
    workExpirence = newInfo.get('workExperience', '')
    address = newInfo.get('address', '')
    work = newInfo.get('work', '')

    user.educational = educational
    user.workExpirence = workExpirence
    user.address = address
    user.work = work
    if fileInfo.get('avatar') != None:
        user.avatar = fileInfo.get('avatar')
    user.save()