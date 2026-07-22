"""
数据增强脚本：
1. 将用户创建时间分散到近半年各个月份
2. 扩充岗位数据到1000+条
"""
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '数据可视化分析.settings')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
django.setup()

from myApp.models import User, JobInfo
import json
import random
from datetime import date, timedelta

random.seed(2026)

# ==================== 1. 分散用户创建时间 ====================
print("=== 分散用户创建时间到近半年 ===")
users = list(User.objects.all())
# 为每个用户随机分配2026-01到2026-07之间的创建日期
for u in users:
    day_offset = random.randint(0, 202)  # 0~202天，覆盖1月1日到7月22日
    new_date = date(2026, 1, 1) + timedelta(days=day_offset)
    u.createTime = new_date
User.objects.bulk_update(users, ['createTime'])
print(f"已更新 {len(users)} 个用户的创建时间")

# 统计月份分布
from collections import Counter
month_dist = Counter()
for u in User.objects.all():
    month_dist[str(u.createTime)[:7]] += 1
for m in sorted(month_dist.keys()):
    print(f"  {m}: {month_dist[m]} 人")
print()

# ==================== 2. 扩充岗位数据 ====================
print("=== 扩充岗位数据 ===")
current = JobInfo.objects.count()
target = 1200
need = target - current
print(f"当前: {current}, 目标: {target}, 需添加: {need}")

if need <= 0:
    print("数据已足够，跳过")
else:
    # 数据池
    JOB_TYPES = {
        "后端开发": ["Python开发工程师", "Java高级开发", "C++开发工程师", "Go后端开发",
                    "PHP开发工程师", "Node.js开发", "C#开发工程师", "Golang工程师"],
        "前端开发": ["前端开发工程师", "Web前端开发", "Vue前端工程师", "React前端工程师",
                    "高级前端开发", "小程序前端开发"],
        "移动开发": ["Android开发", "iOS开发", "Flutter开发", "React Native开发",
                    "移动端架构师", "鸿蒙开发工程师"],
        "数据/AI": ["数据分析师", "数据挖掘工程师", "NLP算法工程师", "CV算法工程师",
                   "推荐算法工程师", "大数据开发", "AIGC工程师", "数据架构师",
                   "机器学习工程师", "深度学习工程师"],
        "测试/运维": ["测试工程师", "自动化测试", "性能测试工程师", "运维工程师",
                    "DevOps工程师", "SRE工程师", "测试开发工程师"],
        "产品/设计": ["产品经理", "UI设计师", "UX设计师", "B端产品经理",
                    "增长产品经理", "高级产品经理", "交互设计师"],
        "安全/架构": ["网络安全工程师", "安全工程师", "系统架构师", "技术经理",
                    "技术总监", "安全架构师", "渗透测试工程师"],
    }

    CITIES = {
        "北京": ["朝阳区", "海淀区", "西城区", "东城区", "丰台区", "大兴区", "昌平区", "通州区"],
        "上海": ["浦东新区", "徐汇区", "静安区", "黄浦区", "杨浦区", "闵行区", "长宁区", "虹口区"],
        "深圳": ["南山区", "福田区", "龙岗区", "宝安区", "罗湖区", "龙华区", "坪山区"],
        "成都": ["高新区", "武侯区", "锦江区", "天府新区", "成华区", "金牛区", "双流区"],
        "杭州": ["余杭区", "西湖区", "滨江区", "拱墅区", "萧山区", "上城区", "钱塘区"],
        "广州": ["天河区", "海珠区", "番禺区", "白云区", "黄埔区", "越秀区", "荔湾区"],
        "南京": ["鼓楼区", "建邺区", "玄武区", "雨花台区", "江宁区", "栖霞区", "浦口区"],
        "武汉": ["洪山区", "武昌区", "江汉区", "东湖高新区", "汉阳区", "江岸区", "硚口区"],
        "西安": ["雁塔区", "高新区", "未央区", "碑林区", "长安区", "经开区", "莲湖区"],
        "天津": ["和平区", "南开区", "河西区", "滨海新区", "西青区", "河东区", "河北区"],
        "重庆": ["渝北区", "江北区", "南岸区", "九龙坡区", "沙坪坝区", "渝中区", "巴南区"],
        "苏州": ["工业园区", "虎丘区", "姑苏区", "相城区", "吴中区", "昆山市", "吴江区"],
        "东莞": ["南城区", "东城区", "虎门镇", "长安镇", "松山湖", "厚街镇", "塘厦镇"],
        "郑州": ["金水区", "郑东新区", "高新区", "中原区", "二七区", "管城区", "惠济区"],
        "长沙": ["岳麓区", "芙蓉区", "天心区", "雨花区", "开福区", "望城区"],
        "合肥": ["蜀山区", "包河区", "庐阳区", "瑶海区", "高新区", "经开区"],
    }

    EDUCATIONS = ["博士", "硕士", "本科", "大专", "高中", "中专/中技", "初中及以下", "学历不限"]
    EDU_WEIGHTS = [1, 8, 38, 22, 3, 3, 1, 4]
    WORK_EXPS = ["在校/应届生", "经验不限", "1-3年", "3-5年", "5-10年", "10年以上"]
    EXP_WEIGHTS = [8, 12, 28, 27, 18, 7]
    COMPANY_NATURES = ["民营", "股份制", "外资", "国企", "合资"]
    NATURE_WEIGHTS = [35, 18, 12, 20, 15]
    COMPANY_STATUSES = ["已上市", "D轮及以上", "C轮", "B轮", "A轮", "天使轮", "未融资", "不需要融资"]
    STATUS_WEIGHTS = [10, 6, 10, 14, 16, 8, 25, 11]
    PEOPLE_OPTIONS = [
        ("20人以下", "[0, 20]"), ("20-99人", "[20, 99]"),
        ("100-499人", "[100, 499]"), ("500-999人", "[500, 999]"),
        ("1000-9999人", "[1000, 9999]"), ("10000人以上", "[0, 10000]"),
    ]
    PEOPLE_WEIGHTS = [5, 15, 22, 20, 25, 13]

    WORK_TAGS_POOL = {
        "后端开发": ["Docker", "Kubernetes", "Redis", "MySQL", "PostgreSQL", "微服务",
                    "分布式系统", "高并发", "消息队列", "RPC", "DDD", "Serverless"],
        "前端开发": ["Vue3", "React18", "TypeScript", "Webpack5", "Vite", "小程序",
                    "H5", "CSS-in-JS", "Next.js", "Nuxt"],
        "移动开发": ["Kotlin", "Swift", "Flutter", "Jetpack Compose", "性能优化",
                    "组件化", "热修复", "跨平台"],
        "数据/AI": ["PyTorch", "TensorFlow", "Transformer", "Spark", "Flink",
                   "SQL优化", "数据仓库", "ETL", "特征工程", "模型部署"],
        "测试/运维": ["自动化测试", "Selenium", "JMeter", "CI/CD", "Jenkins",
                    "Docker", "Kubernetes", "Prometheus", "Grafana"],
        "产品/设计": ["原型设计", "需求分析", "用户研究", "Figma", "Sketch", "Axure",
                    "A/B测试", "数据驱动"],
        "安全/架构": ["渗透测试", "安全审计", "系统设计", "技术选型", "项目管理",
                    "代码审查", "性能调优", "高可用架构"],
    }

    COMPANY_TAGS = [
        "五险一金", "六险一金", "年终奖", "绩效奖金", "带薪年假",
        "弹性工作", "周末双休", "餐补", "房补", "交通补助",
        "股票期权", "技术氛围好", "大牛云集", "扁平管理", "定期团建",
        "免费健身房", "下午茶", "节日福利", "生日福利", "年度体检",
    ]

    SALARY_RANGES = {
        "在校/应届生": [(3000, 8000), (5000, 12000), (8000, 15000)],
        "经验不限": [(5000, 15000), (8000, 20000), (10000, 25000)],
        "1-3年": [(8000, 20000), (12000, 28000), (15000, 35000)],
        "3-5年": [(15000, 30000), (20000, 40000), (25000, 50000)],
        "5-10年": [(25000, 45000), (30000, 55000), (35000, 70000)],
        "10年以上": [(40000, 70000), (50000, 80000), (60000, 100000)],
    }

    COMPANY_PREFIX = [
        "字节跳动", "腾讯", "阿里巴巴", "百度", "美团", "滴滴出行", "京东", "网易",
        "华为", "小米集团", "OPPO", "vivo", "快手", "哔哩哔哩", "小红书", "知乎",
        "商汤科技", "旷视科技", "依图科技", "云从科技", "第四范式",
        "科大讯飞", "海康威视", "大疆创新", "蔚来汽车", "理想汽车", "小鹏汽车",
        "星辰", "极光", "微众银行", "斑马网络", "数新智能", "深势科技", "明略数据",
        "元戎启行", "星环科技", "天云数据", "启明星辰", "蓝湖", "云智慧",
        "永洪科技", "神策数据", "数梦工场", "青云", "UCloud", "七牛云",
        "又拍云", "青云科技", "金山云", "白山云", "网宿科技",
    ]

    def random_salary(exp):
        lo, hi = random.choice(SALARY_RANGES[exp])
        lo = max(3000, int(lo * random.uniform(0.85, 1.3) / 1000) * 1000)
        hi = max(lo + 1000, int(hi * random.uniform(0.85, 1.3) / 1000) * 1000)
        return f"[{lo}, {hi}]"

    def random_company_people():
        label, code = random.choices(PEOPLE_OPTIONS, weights=PEOPLE_WEIGHTS, k=1)[0]
        return code

    def random_date_2026():
        day_offset = random.randint(0, 202)
        return date(2026, 1, 1) + timedelta(days=day_offset)

    jobs_batch = []
    batch_size = 200

    for i in range(need):
        category = random.choice(list(JOB_TYPES.keys()))
        title = random.choice(JOB_TYPES[category])
        city = random.choice(list(CITIES.keys()))
        district = random.choice(CITIES[city])
        edu = random.choices(EDUCATIONS, weights=EDU_WEIGHTS, k=1)[0]
        exp = random.choices(WORK_EXPS, weights=EXP_WEIGHTS, k=1)[0]
        salary = random_salary(exp)

        is_practice = 0
        if exp == "在校/应届生" and random.random() < 0.35:
            is_practice = 1
            salary = f"[{random.randint(120, 300)}, {random.randint(180, 400)}]"

        company = random.choice(COMPANY_PREFIX)
        if random.random() > 0.6:
            suffix = random.choice(["科技", "信息技术", "网络科技", "软件", "云计算",
                                    "数据科技", "数字科技", "智能科技"])
            company = company + suffix + random.choice(["有限公司", "股份有限公司"])

        nature = random.choices(COMPANY_NATURES, weights=NATURE_WEIGHTS, k=1)[0]
        status = random.choices(COMPANY_STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        people_code = random_company_people()
        work_tag = json.dumps(random.sample(
            WORK_TAGS_POOL.get(category, WORK_TAGS_POOL["后端开发"]),
            random.randint(2, 5)))
        company_tag = json.dumps(
            ["，".join(random.sample(COMPANY_TAGS, random.randint(1, 5)))])
        hr_work = random.choice(["HRBP", "招聘专员", "HR经理", "人事主管", "HRD"])

        surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
                    "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗"]
        hr_name = random.choice(surnames) + random.choice(["经理", "主管", "专员", "HR"])

        salary_month = str(random.choice([12, 13, 14, 15, 16, 17, 18]))

        create_date = random_date_2026()

        jobs_batch.append(JobInfo(
            title=title, address=city, type=title,
            educational=edu, workExperience=exp,
            workTag=work_tag, salary=salary,
            salaryMonth=salary_month, companyTags=company_tag,
            hrWork=hr_work, hrName=hr_name, pratice=is_practice,
            companyTitle=company, companyAvatar="",
            companyNature=nature, companyStatus=status,
            companyPeople=people_code,
            detailUrl=f"https://www.zhipin.com/job_detail/{random.randint(100000, 999999)}.html",
            companyUrl=f"https://www.zhipin.com/company/{random.randint(100000, 999999)}.html",
            dist=district,
        ))
        jobs_batch[-1]._custom_date = create_date

        if len(jobs_batch) >= batch_size:
            created = JobInfo.objects.bulk_create(jobs_batch, batch_size=batch_size)
            for j, obj in enumerate(created):
                obj.createTime = jobs_batch[j]._custom_date
            JobInfo.objects.bulk_update(created, ['createTime'], batch_size=len(created))
            print(f"  已插入 {min(current + i + 1, target)}/{target}")
            jobs_batch = []

    # 插入剩余
    if jobs_batch:
        created = JobInfo.objects.bulk_create(jobs_batch, batch_size=len(jobs_batch))
        for j, obj in enumerate(created):
            obj.createTime = jobs_batch[j]._custom_date
        JobInfo.objects.bulk_update(created, ['createTime'], batch_size=len(created))
        print(f"  已插入 {target}/{target}")

final = JobInfo.objects.count()
print(f"\n=== 完成！总岗位数: {final} ===")

# 快速统计
from django.db.models import Count
print(f"日期范围: {JobInfo.objects.earliest('createTime').createTime} ~ {JobInfo.objects.latest('createTime').createTime}")
print(f"城市数: {JobInfo.objects.values('address').distinct().count()}")
print(f"岗位类型数: {JobInfo.objects.values('type').distinct().count()}")
