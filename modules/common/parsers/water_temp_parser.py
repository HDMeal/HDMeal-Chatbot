# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# water_temp_parser.py - 실시간수질정보시스템 서버에 접속하여 수온정보를 파싱해오는 스크립트입니다.

import datetime
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from modules.common import log


def get(req_id, debugging):
    log.info("[#%s] get@water_temp_parser.py: Started Parsing Water Temperature" % req_id)
    try:
        url = urllib.request.urlopen("http://koreawqi.go.kr/wQSCHomeLayout_D.wq?action_type=T", timeout=2)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err("[#%s] get@water_temp_parser.py: Failed to Parse Water Temperature because %s" % (req_id, e))
        raise ConnectionError
    data = BeautifulSoup(url, 'html.parser')
    # 측정일시 파싱
    date = data.find('span', class_='data').get_text().split('"')[1]
    date = int(date[0:4]), int(date[4:6]), int(date[6:8])
    time = int(data.find('span', class_='data').get_text().split('"')[3])
    measurement_date = datetime.datetime(date[0], date[1], date[2], time)
    # 수온 파싱
    wtemp = data.find('tr', class_='site_S01004').get_text()  # 구리측정소 사용
    wtemp = wtemp.replace("구리", "").strip()
    log.info("[#%s] get@water_temp_parser.py: Succeeded" % req_id)
    return measurement_date, wtemp