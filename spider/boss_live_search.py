"""
BOSS直聘实时搜索模块
基于 spiderMain.py 重构，提供Selenium实时搜索功能，返回结构化JSON数据

使用方法：
    from spider.boss_live_search import BossLiveSearch
    searcher = BossLiveSearch(headless=True)
    results = searcher.search('Python', city_code='101010100', page=1)
    searcher.close()
"""

import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BossLiveSearch:
    """BOSS直聘实时搜索类"""

    # BOSS直聘搜索URL模板
    SEARCH_URL = 'https://www.zhipin.com/web/geek/job?query=%s&city=%s&page=%s'

    # ChromeDriver路径（相对于项目根目录）
    CHROMEDRIVER_PATH = './chromedriver.exe'

    def __init__(self, headless=False, driver_path=None):
        """
        初始化BOSS直聘搜索器

        参数:
            headless: 是否使用无头模式（服务端运行时推荐True）
            driver_path: chromedriver路径，默认使用spider目录下的chromedriver.exe
        """
        self.headless = headless
        self.driver_path = driver_path or self.CHROMEDRIVER_PATH
        self.browser = None

    def _get_browser(self):
        """获取或创建Chrome浏览器实例"""
        if self.browser is not None:
            return self.browser

        service = Service(self.driver_path)
        options = webdriver.ChromeOptions()

        # 反检测：隐藏自动化标记
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--disable-blink-features=AutomationControlled')

        if self.headless:
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

        # 禁用图片加载加速搜索
        prefs = {'profile.managed_default_content_settings.images': 2}
        options.add_experimental_option('prefs', prefs)

        self.browser = webdriver.Chrome(service=service, options=options)
        return self.browser

    def search(self, keyword, city_code='100010000', page=1, max_results=30):
        """
        在BOSS直聘上执行实时搜索

        参数:
            keyword: 搜索关键词（如 "Python", "Java开发"）
            city_code: BOSS直聘城市代码（默认100010000=全国）
            page: 页码（从1开始）
            max_results: 最大返回结果数

        返回:
            dict: {
                'success': True/False,
                'total_count': 结果总数,
                'results': [职位数据列表],
                'search_url': 搜索URL,
                'error': 错误信息（仅失败时）
            }
        """
        search_url = self.SEARCH_URL % (keyword, city_code, page)

        try:
            browser = self._get_browser()
            browser.get(search_url)

            # 等待页面加载（BOSS直聘需要较长时间渲染）
            time.sleep(8)

            # 尝试等待职位列表出现
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//ul[@class="job-list-box"]/li'))
                )
            except TimeoutException:
                pass  # 超时也继续尝试解析

            # 解析职位卡片
            job_cards = browser.find_elements(By.XPATH, '//ul[@class="job-list-box"]/li')
            results = []

            for idx, card in enumerate(job_cards[:max_results]):
                try:
                    job_data = self._parse_job_card(card, keyword)
                    if job_data:
                        job_data['index'] = idx + 1
                        results.append(job_data)
                except Exception:
                    continue

            return {
                'success': True,
                'total_count': len(results),
                'results': results,
                'search_url': search_url,
                'keyword': keyword,
                'city_code': city_code,
                'page': page,
            }

        except Exception as e:
            return {
                'success': False,
                'total_count': 0,
                'results': [],
                'search_url': search_url,
                'error': str(e),
            }

    def _parse_job_card(self, card, keyword=''):
        """
        解析单个职位卡片

        参数:
            card: Selenium WebElement（职位卡片）
            keyword: 搜索关键词

        返回:
            dict: 职位数据
        """
        try:
            # 职位名称
            title = card.find_element(
                By.XPATH, ".//span[@class='job-name']"
            ).text

            # 薪资
            salary_text = card.find_element(
                By.XPATH, ".//span[@class='salary']"
            ).text

            # 解析薪资
            salary_parsed = self._parse_salary(salary_text)

            # 地址和区域
            try:
                area_text = card.find_element(
                    By.XPATH, ".//span[@class='job-area-wrapper']/span"
                ).text
                area_parts = area_text.split('·')
                address = area_parts[0].strip()
                dist = area_parts[1].strip() if len(area_parts) > 1 else ''
            except NoSuchElementException:
                address = ''
                dist = ''

            # 标签列表（学历、经验等）
            tag_elements = card.find_elements(
                By.XPATH, ".//ul[@class='tag-list']/li"
            )
            educational = ''
            work_experience = ''
            if len(tag_elements) >= 1:
                work_experience = tag_elements[0].text
            if len(tag_elements) >= 2:
                educational = tag_elements[1].text

            # 技能标签
            try:
                skill_tags = card.find_elements(
                    By.XPATH, "./div[contains(@class,'job-card-footer')]/ul[@class='tag-list']/li"
                )
                work_tag = [t.text for t in skill_tags]
            except NoSuchElementException:
                work_tag = []

            # 公司名称
            try:
                company_title = card.find_element(
                    By.XPATH, ".//div[@class='company-info']/h3/a"
                ).text
            except NoSuchElementException:
                company_title = ''

            # 公司Logo
            try:
                company_avatar = card.find_element(
                    By.XPATH, ".//div[@class='company-logo']/a/img"
                ).get_attribute('src')
            except NoSuchElementException:
                company_avatar = ''

            # 公司标签（性质、融资、规模）
            company_infos = card.find_elements(
                By.XPATH, ".//ul[@class='company-tag-list']/li"
            )
            company_nature = ''
            company_status = ''
            company_people = ''
            if len(company_infos) >= 3:
                company_nature = company_infos[0].text
                company_status = company_infos[1].text
                company_people = company_infos[2].text
            elif len(company_infos) == 2:
                company_nature = company_infos[0].text
                company_status = '未融资'
                company_people = company_infos[1].text
            elif len(company_infos) == 1:
                company_nature = company_infos[0].text
                company_status = '未融资'

            # 福利标签
            try:
                company_tags_text = card.find_element(
                    By.XPATH, "./div[contains(@class,'job-card-footer')]/div[@class='info-desc']"
                ).text
                company_tags = company_tags_text.split(',') if company_tags_text else []
            except NoSuchElementException:
                company_tags = []

            # 岗位详情链接
            try:
                detail_url = card.find_element(
                    By.XPATH, ".//a[@class='job-card-left']"
                ).get_attribute('href')
            except NoSuchElementException:
                detail_url = ''

            # 公司详情链接
            try:
                company_url = card.find_element(
                    By.XPATH, ".//div[@class='company-info']/h3/a"
                ).get_attribute('href')
            except NoSuchElementException:
                company_url = ''

            # HR信息
            try:
                hr_name = card.find_element(
                    By.XPATH, ".//div[@class='info-public']"
                ).text
            except NoSuchElementException:
                hr_name = ''
            try:
                hr_work = card.find_element(
                    By.XPATH, ".//div[@class='info-public']/em"
                ).text
            except NoSuchElementException:
                hr_work = ''

            return {
                'title': title,
                'salary': salary_text,
                'salary_min': salary_parsed['min'],
                'salary_max': salary_parsed['max'],
                'is_pratice': salary_parsed['is_pratice'],
                'salary_month': salary_parsed['salary_month'],
                'address': address,
                'dist': dist,
                'educational': educational,
                'work_experience': work_experience,
                'work_tag': work_tag,
                'company_title': company_title,
                'company_avatar': company_avatar,
                'company_nature': company_nature,
                'company_status': company_status,
                'company_people': company_people,
                'company_tags': company_tags,
                'detail_url': detail_url,
                'company_url': company_url,
                'hr_name': hr_name,
                'hr_work': hr_work,
                'keyword': keyword,
            }
        except Exception:
            return None

    def _parse_salary(self, salary_text):
        """
        解析薪资格式

        参数:
            salary_text: 如 "15-30K·14薪" 或 "100-150元/天"

        返回:
            dict: {'min': int, 'max': int, 'is_pratice': bool, 'salary_month': str}
        """
        result = {
            'min': 0,
            'max': 0,
            'is_pratice': False,
            'salary_month': '0',
        }

        if not salary_text:
            return result

        if 'K' in salary_text:
            # 正式岗位：15-30K·14薪
            parts = salary_text.split('·')
            salary_part = parts[0].replace('K', '')
            if '-' in salary_part:
                nums = salary_part.split('-')
                result['min'] = int(float(nums[0]) * 1000)
                result['max'] = int(float(nums[1]) * 1000)
            if len(parts) > 1:
                result['salary_month'] = parts[1].replace('薪', '')
        elif '元/天' in salary_text:
            # 实习岗位：100-150元/天
            salary_part = salary_text.replace('元/天', '')
            if '-' in salary_part:
                nums = salary_part.split('-')
                result['min'] = int(nums[0])
                result['max'] = int(nums[1])
            result['is_pratice'] = True
        else:
            # 面议或其他格式
            result['min'] = 0
            result['max'] = 0

        return result

    def close(self):
        """关闭浏览器实例"""
        if self.browser:
            try:
                self.browser.quit()
            except Exception:
                pass
            self.browser = None

    def __del__(self):
        """析构时自动关闭浏览器"""
        self.close()


# ===== 便捷函数 =====

def quick_search(keyword, city_name='全国', page=1, headless=True):
    """
    快速搜索BOSS直聘（无需手动管理浏览器生命周期）

    参数:
        keyword: 搜索关键词
        city_name: 城市名称（中文，如"北京"）
        page: 页码
        headless: 是否无头模式

    返回:
        dict: 搜索结果
    """
    # 导入城市映射
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from myApp.utils.boss_utils import get_city_code

    city_code = get_city_code(city_name)
    searcher = BossLiveSearch(headless=headless)
    try:
        return searcher.search(keyword, city_code=city_code, page=page)
    finally:
        searcher.close()


# ===== 测试入口 =====

if __name__ == '__main__':
    # 设置Django环境
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '数据可视化分析.settings')
    django.setup()

    # 测试搜索
    searcher = BossLiveSearch(headless=False)
    try:
        print("正在搜索BOSS直聘: Python 北京...")
        result = searcher.search('Python', city_code='101010100', max_results=5)

        print(f"\n搜索URL: {result['search_url']}")
        print(f"成功: {result['success']}")
        print(f"结果数: {result['total_count']}")
        print()

        for job in result['results']:
            print(f"  [{job['index']}] {job['title']}")
            print(f"      薪资: {job['salary']} | 公司: {job['company_title']}")
            print(f"      经验: {job['work_experience']} | 学历: {job['educational']}")
            print(f"      城市: {job['address']} | 标签: {', '.join(job['work_tag'][:3])}")
            print()
    finally:
        searcher.close()
