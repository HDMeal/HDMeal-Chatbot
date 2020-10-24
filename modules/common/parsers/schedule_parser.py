# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# schedule_parser.py - NEIS 서버에 접속하여 학사일정을 파싱해오는 스크립트입니다.

import json
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from modules.common import conf, log

# 설정 불러오기
school_code = conf.configs['School']['NEIS']['Code']
school_kind = conf.configs['School']['NEIS']['Kind']
neis_baseurl = conf.configs['School']['NEIS']['BaseURL']

def parse(year, month, req_id, debugging):

    log.info("[#%s] parse@schedule_parser.py: Started Parsing Schedule(%s-%s)" % (req_id, year, month))

    # 학년도 기준, 다음해 2월까지 전년도로 조회
    if month < 3:
        school_year = year - 1
    else:
        school_year = year

    try:
        url = (neis_baseurl+"sts_sci_sf01_001.do?"
               "schulCode=%s"
               "&schulCrseScCode=%d"
               "&schulKndScCode=%02d"
               "&ay=%04d&mm=%02d"
               % (school_code, school_kind, school_kind, school_year, month))
        req = urllib.request.urlopen(url, timeout=2)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err("[#%s] parse@schedule_parser.py: Failed to Parse Schedule(%s-%s) because %s" % (
            req_id, year, month, e))
        raise ConnectionError

    if debugging:
        print(url)

    data = BeautifulSoup(req, 'html.parser')
    data = data.find_all('div', class_='textL')

    calendar = dict()

    # 일정 후처리(잡정보들 삭제)
    def pstpr(cal):
        return cal.replace("토요휴업일", "").strip().replace('\n\n\n', '\n')

    for i in range(len(data)):
        string = data[i].get_text().strip()
        if string[2:].replace('\n', '') and pstpr(string[2:]):
            calendar[int(string[:2])] = pstpr(string[2:])

    if debugging:
        print(calendar)

    if calendar:
        with open('data/cache/Cal-%s-%s.json' % (year, month), 'w',
                  encoding="utf-8") as make_file:
            json.dump(calendar, make_file, ensure_ascii=False)
            print("File Created")

    log.info("[#%s] parse@schedule_parser.py: Succeeded(%s-%s)" % (req_id, year, month))

    return 0

# 디버그
if __name__ == "__main__":
    log.init()
    parse(2019, 8, "****DEBUG****", True)