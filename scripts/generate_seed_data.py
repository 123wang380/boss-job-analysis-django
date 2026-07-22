"""
生成近半年（2026年1月-7月）招聘岗位种子数据
覆盖多城市、多岗位、多学历、多经验、多薪资段
"""
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '数据可视化分析.settings')

# 将项目根目录加入路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
django.setup()

from myApp.models import JobInfo
import json
import random
from datetime import date, timedelta

random.seed(42)

# ==================== 数据池 ====================

JOB_TYPES = {
    "后端开发": ["Python", "Java", "C++", "Go", "PHP", "Node.js", "C#"],
    "前端开发": ["前端开发", "Web前端", "Vue前端", "React前端"],
    "移动开发": ["Android", "iOS", "Flutter", "React Native"],
    "数据/AI": ["数据分析", "数据挖掘", "NLP算法", "CV算法", "推荐算法", "大数据开发", "AIGC工程师"],
    "测试/运维": ["测试工程师", "自动化测试", "性能测试", "运维工程师", "DevOps", "SRE"],
    "产品/设计": ["产品经理", "UI设计师", "UX设计师", "B端产品", "增长产品"],
    "安全/架构": ["网络安全", "安全工程师", "系统架构师", "技术经理", "技术总监"],
}

CITIES = {
    "北京": ["朝阳区", "海淀区", "西城区", "东城区", "丰台区", "大兴区", "昌平区"],
    "上海": ["浦东新区", "徐汇区", "静安区", "黄浦区", "杨浦区", "闵行区", "长宁区"],
    "深圳": ["南山区", "福田区", "龙岗区", "宝安区", "罗湖区", "龙华区"],
    "成都": ["高新区", "武侯区", "锦江区", "天府新区", "成华区", "金牛区"],
    "杭州": ["余杭区", "西湖区", "滨江区", "拱墅区", "萧山区", "上城区"],
    "广州": ["天河区", "海珠区", "番禺区", "白云区", "黄埔区", "越秀区"],
    "南京": ["鼓楼区", "建邺区", "玄武区", "雨花台区", "江宁区", "栖霞区"],
    "武汉": ["洪山区", "武昌区", "江汉区", "东湖高新区", "汉阳区", "江岸区"],
    "西安": ["雁塔区", "高新区", "未央区", "碑林区", "长安区", "经开区"],
    "天津": ["和平区", "南开区", "河西区", "滨海新区", "西青区", "河东区"],
    "重庆": ["渝北区", "江北区", "南岸区", "九龙坡区", "沙坪坝区", "渝中区"],
    "东莞": ["南城区", "东城区", "虎门镇", "长安镇", "松山湖", "厚街镇"],
    "苏州": ["工业园区", "虎丘区", "姑苏区", "相城区", "吴中区", "昆山市"],
    "郑州": ["金水区", "郑东新区", "高新区", "中原区", "二七区", "管城区"],
}

EDUCATIONS = ["博士", "硕士", "本科", "大专", "高中", "中专/中技", "初中及以下", "学历不限"]
EDUCATION_WEIGHTS = [1, 5, 35, 25, 3, 4, 1, 6]  # 权重分布

WORK_EXPERIENCES = ["在校/应届生", "经验不限", "1-3年", "3-5年", "5-10年", "10年以上"]
EXPERIENCE_WEIGHTS = [5, 10, 30, 30, 18, 7]

COMPANY_NATURES = ["民营", "股份制", "外资", "国企", "合资", "上市公司"]
NATURE_WEIGHTS = [40, 15, 10, 15, 10, 10]

COMPANY_STATUSES = ["已上市", "D轮及以上", "C轮", "B轮", "A轮", "天使轮", "未融资", "不需要融资"]
STATUS_WEIGHTS = [8, 5, 8, 12, 15, 10, 30, 12]

COMPANY_PEOPLE_RANGES = [
    "20人以下", "20-99人", "100-499人", "500-999人",
    "1000-9999人", "10000人以上"
]

WORK_TAGS_POOL = {
    "后端开发": ["微服务", "分布式", "高并发", "Docker", "K8s", "Redis", "消息队列", "RPC", "DDD"],
    "前端开发": ["Vue", "React", "TypeScript", "Webpack", "Node.js", "小程序", "H5", "CSS3"],
    "移动开发": ["Kotlin", "Swift", "Flutter", "性能优化", "组件化", "热修复", "跨平台"],
    "数据/AI": ["机器学习", "深度学习", "PyTorch", "TensorFlow", "Spark", "Flink", "SQL", "数据仓库", "ETL"],
    "测试/运维": ["自动化", "Selenium", "JMeter", "CI/CD", "Jenkins", "监控", "K8s", "Linux"],
    "产品/设计": ["原型设计", "需求分析", "用户研究", "Figma", "Sketch", "Axure", "数据分析"],
    "安全/架构": ["渗透测试", "安全审计", "系统设计", "技术选型", "团队管理", "项目管理"],
}

COMPANY_TAGS_POOL = [
    "五险一金", "六险一金", "年终奖", "绩效奖金", "带薪年假",
    "弹性工作", "双休", "餐补", "房补", "交通补助",
    "股票期权", "技术氛围好", "大牛云集", "扁平管理", "定期团建",
    "免费健身房", "下午茶", "节日福利", "生日福利", "体检",
]

# 薪资基数范围（月薪，单位：元）
# 根据经验和岗位生成
SALARY_BASE = {
    "在校/应届生": (3000, 15000),
    "经验不限": (5000, 20000),
    "1-3年": (8000, 25000),
    "3-5年": (15000, 40000),
    "5-10年": (25000, 60000),
    "10年以上": (35000, 80000),
}

# 年终奖月数范围
SALARY_MONTHS = [12, 13, 14, 15, 16, 17, 18]

# 公司名称前缀
COMPANY_PREFIXES = [
    "字节", "腾讯", "阿里", "百度", "美团", "滴滴", "京东", "网易",
    "华为", "小米", "OPPO", "vivo", "快手", "B站", "小红书", "知乎",
    "商汤", "旷视", "依图", "云从", "第四范式",
    "科大讯飞", "海康威视", "大疆", "蔚来", "理想", "小鹏",
    "某", "星辰", "极光", "微众", "斑马", "数新", "深势", "明略",
    "元戎", "星环", "天云", "启明", "蓝湖", "云智慧", "永洪", "神策",
]

COMPANY_SUFFIXES = [
    "科技", "信息技术", "数据科技", "网络科技", "软件", "云计算",
    "人工智能", "互联网", "大数据", "数字科技", "智能科技", "信息科技",
]


def random_company_name():
    prefix = random.choice(COMPANY_PREFIXES)
    suffix = random.choice(COMPANY_SUFFIXES)
    if random.random() > 0.5:
        return f"{prefix}{suffix}有限公司"
    else:
        return f"{prefix}{suffix}股份有限公司"


def random_salary(experience):
    low, high = SALARY_BASE[experience]
    # 根据学历微调
    mul = random.uniform(0.8, 1.5)
    low = int(low * mul / 1000) * 1000
    high = int(high * mul / 1000) * 1000
    if low >= high:
        high = low + random.choice([3000, 5000, 8000, 10000, 15000])
    # 确保最小值和最大值合理
    low = max(3000, low)
    high = max(low + 1000, high)
    return f"[{low}, {high}]"


def random_company_people():
    choice = random.choices(COMPANY_PEOPLE_RANGES, weights=[5, 15, 20, 20, 25, 15], k=1)[0]
    if choice == "10000人以上":
        return "[0, 10000]"
    elif choice == "20人以下":
        return "[0, 20]"
    elif choice == "20-99人":
        return "[20, 99]"
    elif choice == "100-499人":
        return "[100, 499]"
    elif choice == "500-999人":
        return "[500, 999]"
    elif choice == "1000-9999人":
        return "[1000, 9999]"


def random_work_tags(category):
    tags = WORK_TAGS_POOL.get(category, WORK_TAGS_POOL["后端开发"])
    num = random.randint(2, 5)
    return json.dumps(random.sample(tags, min(num, len(tags))))


def random_company_tags():
    num = random.randint(1, 5)
    tags = random.sample(COMPANY_TAGS_POOL, num)
    return json.dumps(["，".join(tags)])


def random_hr_name():
    surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
                "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗"]
    names = ["经理", "总监", "主管", "专员", "HR", "招聘官",
             "先生", "女士", "同学"]
    return random.choice(surnames) + random.choice(names)


def random_date():
    start = date(2026, 1, 1)
    end = date(2026, 7, 22)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_jobs(count=600):
    """生成指定数量的岗位数据"""
    jobs = []
    existing_titles = set()

    for i in range(count):
        # 随机选择岗位类别和具体岗位
        category = random.choice(list(JOB_TYPES.keys()))
        job_title = random.choice(JOB_TYPES[category])

        # 随机城市和区
        city = random.choice(list(CITIES.keys()))
        district = random.choice(CITIES[city])

        # 随机学历
        education = random.choices(EDUCATIONS, weights=EDUCATION_WEIGHTS, k=1)[0]

        # 随机工作经验
        experience = random.choices(WORK_EXPERIENCES, weights=EXPERIENCE_WEIGHTS, k=1)[0]

        # 薪资
        salary = random_salary(experience)

        # 实习判断（在校/应届生有一定比例是实习）
        is_practice = 0
        if experience == "在校/应届生" and random.random() < 0.4:
            is_practice = 1
            salary = f"[{random.randint(120, 300)}, {random.randint(180, 400)}]"

        # 公司信息
        company_title = random_company_name()
        # 避免太多重复公司名
        retry = 0
        while company_title in existing_titles and retry < 5:
            company_title = random_company_name()
            retry += 1
        existing_titles.add(company_title)

        company_nature = random.choices(COMPANY_NATURES, weights=NATURE_WEIGHTS, k=1)[0]
        company_status = random.choices(COMPANY_STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        company_people = random_company_people()

        # 标签
        work_tag = random_work_tags(category)
        company_tags = random_company_tags()

        # HR信息
        hr_work = random.choice(["HRBP", "招聘专员", "HR经理", "人事主管", "HRD"])
        hr_name = random_hr_name()

        # 日期
        create_date = random_date()

        # 薪资月数
        salary_month = str(random.choice(SALARY_MONTHS))

        jobs.append(JobInfo(
            title=job_title,
            address=city,
            type=job_title,  # 岗位名称作为type
            educational=education,
            workExperience=experience,
            workTag=work_tag,
            salary=salary,
            salaryMonth=salary_month,
            companyTags=company_tags,
            hrWork=hr_work,
            hrName=hr_name,
            pratice=is_practice,
            companyTitle=company_title,
            companyAvatar="",
            companyNature=company_nature,
            companyStatus=company_status,
            companyPeople=company_people,
            detailUrl=f"https://www.zhipin.com/job_detail/{random.randint(100000, 999999)}.html",
            companyUrl=f"https://www.zhipin.com/company/{random.randint(100000, 999999)}.html",
            dist=district,
        ))

        # 每个对象单独设置创建日期（需要 save 后更新）
        jobs[-1]._custom_date = create_date

    return jobs


def main():
    print("开始生成种子数据...")

    # 清空旧数据
    old_count = JobInfo.objects.count()
    if old_count > 0:
        confirm = input(f"当前数据库有 {old_count} 条岗位记录，是否清空？(y/n): ")
        if confirm.lower() == 'y':
            JobInfo.objects.all().delete()
            print(f"已清空 {old_count} 条旧数据")
        else:
            print("保留旧数据，增量添加")

    # 生成数据
    total = 600
    print(f"正在生成 {total} 条岗位数据...")
    jobs = generate_jobs(total)

    # 批量插入
    batch_size = 100
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        # 先批量创建
        created = JobInfo.objects.bulk_create(batch, batch_size=batch_size)

        # 手动设置 createTime（bulk_create 不会自动设置 auto_now_add）
        for j, obj in enumerate(created):
            obj.createTime = batch[j]._custom_date
        JobInfo.objects.bulk_update(created, ['createTime'], batch_size=batch_size)

        print(f"  已插入 {min(i + batch_size, len(jobs))}/{total}")

    # 验证
    final_count = JobInfo.objects.count()
    print(f"\n数据生成完毕！共 {final_count} 条岗位记录")

    # 统计
    from django.db.models import Count
    print("\n===== 城市分布 =====")
    for item in JobInfo.objects.values('address').annotate(c=Count('id')).order_by('-c')[:10]:
        print(f"  {item['address']}: {item['c']} 条")

    print("\n===== 学历分布 =====")
    for item in JobInfo.objects.values('educational').annotate(c=Count('id')).order_by('-c'):
        print(f"  {item['educational']}: {item['c']} 条")

    print("\n===== 经验分布 =====")
    for item in JobInfo.objects.values('workExperience').annotate(c=Count('id')).order_by('-c'):
        print(f"  {item['workExperience']}: {item['c']} 条")

    print("\n===== 时间分布 =====")
    for item in JobInfo.objects.values('createTime').annotate(c=Count('id')).order_by('createTime'):
        if item['createTime']:
            print(f"  {item['createTime']}: {item['c']} 条")

    print("\n===== 公司性质分布 =====")
    for item in JobInfo.objects.values('companyNature').annotate(c=Count('id')).order_by('-c'):
        print(f"  {item['companyNature']}: {item['c']} 条")

    print("\n===== 融资阶段分布 =====")
    for item in JobInfo.objects.values('companyStatus').annotate(c=Count('id')).order_by('-c'):
        print(f"  {item['companyStatus']}: {item['c']} 条")

    print("\n[OK] 完成！所有图表功能均有充足数据支持。")


if __name__ == "__main__":
    main()
