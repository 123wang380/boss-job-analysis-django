"""
BOSS直聘工具模块
提供BOSS直聘URL生成、城市代码映射、实时搜索等功能
"""

import urllib.parse

# ===== BOSS直聘城市代码映射表 =====
# 格式：城市名 → BOSS直聘city_code
BOSS_CITY_MAP = {
    '全国': '100010000',
    '北京': '101010100',
    '上海': '101020100',
    '深圳': '101280600',
    '广州': '101280100',
    '杭州': '101210100',
    '成都': '101270100',
    '南京': '101190100',
    '武汉': '101200100',
    '西安': '101110100',
    '重庆': '100040000',
    '苏州': '101190400',
    '天津': '101030100',
    '长沙': '101250100',
    '东莞': '101281600',
    '郑州': '101180100',
    '合肥': '101220100',
    '厦门': '101230200',
    '青岛': '101120200',
    '济南': '101120100',
    '大连': '101070200',
    '昆明': '101290100',
    '福州': '101230100',
    '佛山': '101280800',
    '无锡': '101190200',
    '宁波': '101210400',
    '沈阳': '101070100',
    '贵阳': '101260100',
    '长春': '101060100',
    '哈尔滨': '101050100',
    '石家庄': '101090100',
    '南宁': '101300100',
    '南昌': '101240100',
    '太原': '101100100',
    '兰州': '101160100',
    '海口': '101310100',
    '乌鲁木齐': '101130100',
}

# BOSS直聘搜索基础URL
BOSS_SEARCH_BASE = 'https://www.zhipin.com/web/geek/job'
# BOSS直聘岗位详情URL模板
BOSS_JOB_DETAIL_BASE = 'https://www.zhipin.com/job_detail/{}.html'


def get_city_code(city_name):
    """
    根据城市名称获取BOSS直聘城市代码
    如果城市名不在映射表中，返回全国代码
    """
    if not city_name or city_name == '不限':
        return '100010000'
    # 精确匹配
    if city_name in BOSS_CITY_MAP:
        return BOSS_CITY_MAP[city_name]
    # 模糊匹配：尝试在城市名中查找
    for name, code in BOSS_CITY_MAP.items():
        if name in city_name or city_name in name:
            return code
    return '100010000'


def generate_boss_search_url(keyword='', city='', education='', experience=''):
    """
    根据搜索参数生成BOSS直聘搜索URL

    参数:
        keyword: 搜索关键词（职位/公司/技能）
        city: 城市名称（中文）
        education: 学历要求（中文）
        experience: 工作经验（中文）

    返回:
        BOSS直聘搜索URL字符串
    """
    city_code = get_city_code(city)

    # 构建查询关键词：将学历、经验等信息追加到关键词中
    query_parts = []
    if keyword and keyword.strip():
        query_parts.append(keyword.strip())
    if education and education != '不限':
        query_parts.append(education)
    if experience and experience != '不限':
        query_parts.append(experience)

    query = ' '.join(query_parts) if query_parts else ''

    # 构建URL
    params = {
        'query': query,
        'city': city_code,
    }
    query_string = urllib.parse.urlencode(params)

    return f"{BOSS_SEARCH_BASE}?{query_string}"


def get_boss_job_url(job):
    """
    获取岗位的BOSS直聘链接
    优先使用 job.detailUrl（爬虫存储的真实链接），
    如果为空则用 job.title 生成搜索链接作为降级方案

    参数:
        job: JobInfo 模型实例

    返回:
        BOSS直聘URL字符串
    """
    # 优先使用已存储的detailUrl
    if job.detailUrl and job.detailUrl.strip():
        return job.detailUrl.strip()

    # 降级：使用岗位名称搜索
    if job.title and job.title.strip():
        return generate_boss_search_url(keyword=job.title)

    # 最终降级：返回BOSS直聘首页
    return 'https://www.zhipin.com/'


def get_boss_company_url(job):
    """
    获取公司页面的BOSS直聘链接
    优先使用 job.companyUrl，为空则用公司名搜索

    参数:
        job: JobInfo 模型实例

    返回:
        BOSS直聘公司页面URL字符串
    """
    # 优先使用已存储的companyUrl
    if job.companyUrl and job.companyUrl.strip():
        return job.companyUrl.strip()

    # 降级：使用公司名搜索
    if job.companyTitle and job.companyTitle.strip():
        return generate_boss_search_url(keyword=job.companyTitle)

    return 'https://www.zhipin.com/'


def get_boss_job_detail_url_by_id(job_id):
    """
    根据BOSS直聘岗位ID生成详情页URL

    参数:
        job_id: BOSS直聘岗位ID

    返回:
        BOSS直聘岗位详情URL
    """
    return BOSS_JOB_DETAIL_BASE.format(job_id)


def extract_job_id_from_url(url):
    """
    从BOSS直聘URL中提取岗位ID

    参数:
        url: BOSS直聘岗位URL

    返回:
        岗位ID字符串，提取失败返回None
    """
    if not url:
        return None
    # 匹配 job_detail/xxxxx.html 格式
    import re
    match = re.search(r'job_detail/([a-f0-9]+)\.html', url)
    if match:
        return match.group(1)
    return None
