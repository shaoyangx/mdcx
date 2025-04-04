#!/usr/bin/env python3

import json
import re
import time

from models.crawlers import getchu, hanime1 , iqqtv

def main(number, appoint_url="", log_info="", req_web="", language="jp"):
    start_time = time.time()
    website_name = "hanimation"    
    req_web += "-> %s" % website_name
    #名称预处理
    seanumber = re.sub(r'^(OVA)\s*|\s*(＃|#)*(\d)\s*',
                    lambda m: f'{m.group(1) or ""} 'if m.group(1)
                    else f' {m.group(3)}', number)
    # 调用爬虫getchu
    json_data_getchu = json.loads(getchu.main(seanumber, appoint_url, log_info, req_web, "jp"))
    json_getchu_new = json_data_getchu["getchu"]["jp"] # 获取getchu中的JP数据
    # 调用爬虫iqqtv
    json_data_iqqtv_new = json.loads(iqqtv.main(seanumber, appoint_url, log_info, req_web, "zh_cn"))
    json_iqqtv_new = json_data_iqqtv_new["iqqtv"]["zh_cn"] # 获取iqqtv中的数据
    # 调用爬虫hanimel
    json_data_hanime1 = json.loads(hanime1.main(seanumber, appoint_url, log_info, req_web, "zh_cn"))
    json_hanime1 = json_data_hanime1["hanime1"]["zh_cn"] # 获取getchu中的数据
    # 日志
    log_info = (
        json_hanime1.get("log_info", "") + 
        json_getchu_new.get("log_info", "") + 
        json_iqqtv_new.get("log_info", "")
    )

    try: # 捕获主动抛出的异常
        dic = {
            "number": json_getchu_new.get("number") or "",
            "title": json_hanime1.get("title") or json_iqqtv_new.get("title") or json_getchu_new.get("title") or "",
            "originaltitle": json_getchu_new.get("originaltitle") or json_iqqtv_new.get("originaltitle") or json_hanime1.get("originaltitle", "") or "",
            "actor": "",
            "outline": json_hanime1.get("outline") or json_iqqtv_new.get("outline") or json_getchu_new.get("outline", "") or "",
            "originalplot": json_getchu_new.get("originalplot") or json_iqqtv_new.get("originalplot") or json_hanime1.get("originalplot", "") or "",
            "tag": json_hanime1.get("tag") or json_getchu_new.get("tag") or json_iqqtv_new.get("tag", "") or "",
            "release": json_getchu_new.get("release") or json_iqqtv_new.get("release") or "",
            "year": json_getchu_new.get("year") or json_iqqtv_new.get("year")  or "",
            "runtime": json_getchu_new.get("runtime") or json_iqqtv_new.get("runtime")  or "",
            "score": json_getchu_new.get("score") or json_iqqtv_new.get("score")  or "",
            "series": json_getchu_new.get("series") or json_iqqtv_new.get("series")  or "",
            "director": json_getchu_new.get("director") or json_iqqtv_new.get("director")  or "",
            "studio": json_getchu_new.get("studio") or json_iqqtv_new.get("studio")  or "",
            "publisher": json_getchu_new.get("publisher") or json_iqqtv_new.get("publisher")  or "",
            "source": json_getchu_new.get("source") or json_iqqtv_new.get("source") or json_hanime1.get("source", "") or "",
            "actor_photo": json_getchu_new.get("actor_photo") or json_iqqtv_new.get("actor_photo") or "",
            "cover": json_getchu_new.get("cover") or json_iqqtv_new.get("cover")  or "",
            "poster": json_getchu_new.get("poster") or json_iqqtv_new.get("poster")  or "",
            "extrafanart": json_getchu_new.get("extrafanart") or json_iqqtv_new.get("extrafanart")  or "",
            "trailer": json_getchu_new.get("trailer") or json_iqqtv_new.get("trailer") or "",
            "image_download": json_getchu_new.get("image_download") or json_iqqtv_new.get("image_download") or "",
            "image_cut": json_getchu_new.get("image_cut") or json_iqqtv_new.get("image_cut") or "",
            "log_info": log_info,
            "error_info": "",
            "req_web": req_web + f"({round((time.time() - start_time), )}s) ",
            "mosaic": "",
            "website": json_getchu_new.get("website") or json_iqqtv_new.get("website") or json_hanime1.get("website", "") or "",
            "wanted": "",
        }

        debug_info = "数据获取成功！"
        log_info += debug_info
        dic["log_info"] = log_info
    except Exception as e:
        debug_info = f"数据生成出错: {str(e)}"
        log_info += debug_info
        raise Exception(debug_info)
    dic = {"hanimation": {"zh_cn": dic, "zh_tw": dic, "jp": dic}}
    js = json.dumps(
        dic,
        ensure_ascii=False,
        sort_keys=False,
        indent=4,
        separators=(",", ": "),
    )  # .encode('UTF-8')
    return js


if __name__ == "__main__":
    # yapf: disable
    # print(main('コンビニ○○Z 第三話 あなた、ヤンクレママですよね。旦那に万引きがバレていいんですか？'))
    # print(main('[PoRO]エロコンビニ店長 泣きべそ蓮っ葉・栞～お仕置きじぇらしぃナマ逸機～'))
    # print(main('ACHDL-1159'))
    # print(main('好きにしやがれ GOTcomics'))    # 書籍，没有番号 # dmm 没有
    # print(main('ACMDP-1005')) # 有时间、导演，上下集ACMDP-1005B
    # print(main('ISTU-5391'))    # dmm 没有
    # print(main('INH-392'))
    # print(main('OVA催眠性指導 ＃4宮島椿の場合')) # 都没有
    # print(main('OVA催眠性指導 ＃5宮島椿の場合')) # 都没有
    # print(main('GLOD-148')) # getchu 没有
    # print(main('(18禁アニメ) (無修正) 紅蓮 第1幕 「鬼」 (spursengine 960x720 h.264 aac)'))
    print(main('OVAスケベエルフ探訪記 ＃2'))  # print(main('ISTU-5391', appoint_url='http://www.getchu.com/soft.phtml?id=1180483'))  # print(main('SPY×FAMILY Vol.1 Blu-ray Disc＜初回生産限定版＞'))    # dmm 没有
