#!/usr/bin/env python3
import json
import re
import time
import urllib.parse

import urllib3
from lxml import etree

from models.base.web import curl_html
from models.config import config
from models.signals import signal


urllib3.disable_warnings()  # yapf: disable

def get_title(html):
    result = html.xpath('//div[@class="video-description-panel video-description-panel-hover no-select"]/div[2]/text()')[0].strip()
    # 使用正则表达式去掉中括号及其内容
    return result

def get_outline(html):
    result = html.xpath('//div[@class="video-description-panel video-description-panel-hover no-select"]/div[3]/text()')[0].strip()
    result = str(result)
    return result

def get_tag(html):
    result = html.xpath('//div[@style="margin-bottom: 18px; font-weight: normal"]/a/text()')
    # 清理Tag中的标签
    result = [tag for tag in result if not re.match(r'^(1080(P)*)$', tag, re.IGNORECASE)] 
    return ",".join(result) if result else ""

def retry_request(html_info, log_info, web_info):
    title = get_title(html_info)  # 获取标题
    if not title:
        debug_info = "数据获取失败: 未获取到title！"
        log_info += web_info + debug_info
        raise Exception(debug_info)
    outline = get_outline(html_info)
    tag = get_tag(html_info)
    return title, outline, tag, log_info


def get_real_url(html, number):
    """
    从搜索结果页面中获取最匹配的详情页URL
    :param html: HTML解析后的元素树
    :param number: 要匹配的番号
    :return: 匹配结果状态、匹配的番号、标题和URL
    """
    item_list = html.xpath('//div[@class="col-xs-6 col-sm-4 col-md-2 search-doujin-videos hidden-xs hover-lighter multiple-link-wrapper"]')

    for item in item_list:
        detail_url = item.xpath("./a/@href")[0].strip()
        #获取搜索结果页
        if detail_url:
            result, html = curl_html(detail_url)
            if not result:
                debug_info = f"网络请求错误: {html} "
                log_info += debug_info
                raise Exception(debug_info)
            html = etree.fromstring(html, etree.HTMLParser())
        raw_title = html.xpath('//h3[@id="shareBtn-title"]/text()')[0].strip()
        title = re.sub(r"[\W_]", "", raw_title).upper()
        number = re.sub(r"[\W_]", "", number).upper()
        # 比较标题与番号是否匹配
        if number.upper() in title:
            return detail_url,html
    return ""



def main(number,appoint_url="",log_info="",req_web="",language="zh_cn"):
    """
    主函数，获取影片信息
    :param number: 番号
    :param appoint_url: 指定的URL
    :param log_info: 日志信息
    :param req_web: 请求网站信息
    :param language: 语言
    :return: JSON格式的影片信息
    """
    start_time = time.time()
    website_name = "hanime1"
    req_web += "-> %s" % website_name
    title = ""
    web_info = "\n       "
    log_info += " \n    🌐 hanime1"
    debug_info = ""
    real_url = appoint_url
    hanime1_url = "https://hanime1.me"
    number2 = re.sub('#', ' ', number)
    try: # 捕获主动抛出的异常
        if not real_url:
            # 通过搜索获取real_url
            url_search = hanime1_url + f"/search?query={number2}"
            debug_info = f"搜索地址: {url_search} "
            log_info += web_info + debug_info

            result, html_search = curl_html(url_search)
            if not result:
                debug_info = f"网络请求错误: {html_search} "
                log_info += web_info + debug_info
                raise Exception(debug_info)
            html = etree.fromstring(html_search, etree.HTMLParser())
            #捕获列表
            real_url = html.xpath('//div[@class="col-xs-6 col-sm-4 col-md-2 search-doujin-videos hidden-xs hover-lighter multiple-link-wrapper"]/a[@href]/@href')
            if not real_url:
                debug_info = "搜索结果: 未匹配到番号！"
                log_info += web_info + debug_info
                raise Exception(debug_info)

        if real_url:
            real_url,html_info = get_real_url(html, number)
            # 搜索结果页面有条目，但无法匹配到番号
            if not real_url:
                debug_info = "搜索结果: 未匹配到番号！2"
                log_info += web_info + debug_info
                raise Exception(debug_info)
            else:
                real_url = urllib.parse.urljoin(hanime1_url, real_url) if real_url.startswith("/") else real_url

            debug_info = f"番号地址: {real_url} "
            log_info += web_info + debug_info
            title, outline, tag, log_info = retry_request(
                html_info, log_info, web_info
            )
            try:
                dic = {
                    "number": number,
                    "title": title,
                    "originaltitle": title,
                    "actor": "",
                    "outline": outline,
                    "originalplot": outline,
                    "tag": tag,
                    "release": "",
                    "year": "",
                    "runtime": "",
                    "score": "",
                    "series": "",
                    "director": "",
                    "studio": "",
                    "publisher": "",
                    "source": "hanime1",
                    "actor_photo": "",
                    "cover": "",
                    "poster": "",
                    "extrafanart": "",
                    "trailer": "",
                    "image_download": "",
                    "image_cut": "",
                    "log_info": log_info,
                    "error_info": "",
                    "req_web": req_web + f"({round((time.time() - start_time), )}s) ",
                    "mosaic": "",
                    "website": real_url,
                    "wanted": "",
                }
                debug_info = "数据获取成功！"
                log_info += web_info + debug_info
                dic["log_info"] = log_info
            except Exception as e:
                debug_info = f"数据生成出错: {str(e)}"
                log_info += web_info + debug_info
                raise Exception(debug_info)
    except Exception as e:
        # print(traceback.format_exc())
        debug_info = str(e)
        dic = {
            "title": "",
            "website": "",
            "log_info": log_info,
            "error_info": debug_info,
            "req_web": req_web + f"({round((time.time() - start_time), )}s) ",
        }
    dic = {website_name: {"zh_cn": dic, "zh_tw": dic, "jp": dic}}
    js = json.dumps(
        dic,
        ensure_ascii=False,
        sort_keys=False,
        indent=4,
        separators=(",", ": "),
    )  # .encode('UTF-8')
    return js

if __name__ == "__main__":
    # 测试代码
    #print(main("OVAスケベエルフ探訪記"))
    print(main("OVAスケベエルフ探訪記 #2"))
    # 测试搜索功能
    # results = search("巨乳", 1)
    # print(f"搜索结果数量: {len(results)}")
    # if results:
    #     print(f"第一个结果: {results[0]}")
