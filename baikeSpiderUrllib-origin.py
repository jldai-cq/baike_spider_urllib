import json
import urllib.request
import urllib.parse
from lxml import etree
from urllib.parse import quote
import time
import random
from tqdm import tqdm

"""配置日志"""
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""获取关键字"""
import crops
crops_name = crops.food_crops + crops.cash_crops + crops.fruits + crops.vegetables + crops.edible_fungi

"""获取代理IP池"""
with open('./proxies.json', 'r', encoding='utf-8') as f:
    PROXY_POOL = json.load(f)

def get_proxy():
    """智能随机获取一个代理IP"""
    proxy_item = random.choice(PROXY_POOL)
    # http://ip:port
    proxy_ip = proxy_item['ip']
    proxy_port = proxy_item['port']
    proxy = f"http://{proxy_ip}:{proxy_port}"
    return proxy

"""执行请求、解析html、返回解析数据"""
def start_requests(url, headers, method='GET'):

    # 设置代理
    if PROXY_POOL:
        # 使用代理进行请求
        proxy_handler = urllib.request.ProxyHandler({'http': get_proxy()})
        # 创建一个 OpenerDirector 对象
        opener = urllib.request.build_opener(proxy_handler)
        # 安装全局的 opener
        urllib.request.install_opener(opener)

    # 利用请求地址和请求头部构造请求对象
    req = urllib.request.Request(url=url, headers=headers, method=method)
    # 发送请求，获得响应
    response = urllib.request.urlopen(req)

    # 读取响应，获得文本
    text = response.read().decode('utf-8')
    # 构造 _Element 对象
    html = etree.HTML(text)
    # 使用 xpath 匹配数据，得到匹配字符串列表
    briefly = html.xpath("//div[@class='lemmaSummary_s9vD3 J-summary']//text()")
    crop_name = html.xpath("//h1[@class='lemmaTitle_WMFeg J-lemma-title']//text()")
    detail = html.xpath("//div[@class='J-lemma-content']//text()")

    # 过滤数据，去掉空白
    briefly_after_filter = [item.strip('\n') for item in briefly]
    crop_name_after_filter = [item.strip('\n') for item in crop_name]
    detail_after_filter = [item.strip('\n') for item in detail]

    # 拼接数据
    briefly_after_filter = ''.join(briefly_after_filter)
    crop_name_after_filter = ''.join(crop_name_after_filter)
    detail_after_filter = ''.join(detail_after_filter)

    item = {
        "url": url,
        "crop_name": crop_name_after_filter,
        "briefly": briefly_after_filter,
        "detail": detail_after_filter
    }

    return item

"""爬取逻辑"""
def main():
    # 请求地址
    url = 'https://baike.baidu.com/item/'

    # 循环爬取关键字（作物名称库）
    for crop_name in tqdm(crops_name, desc="爬取进度："):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
            'Referer': 'https://www.baidu.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive'
        }
        # 对关键字 crop_name 进行编码
        response = start_requests(f'{url}{quote(crop_name)}', headers, 'GET')

        # 追写模式、存储于jsonl文件中
        with open('scrapy_data/data.jsonl', 'a', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False)
            f.write('\n')

        # 随机延迟 2-3 秒，避免被反爬虫
        time.sleep(random.uniform(2, 3))

if __name__ == '__main__':
    main()
