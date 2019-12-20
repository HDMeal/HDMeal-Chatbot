# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/getData.py - 급식, 시간표, 캐시정보를 가져오는 스크립트입니다.

import datetime
import json
import os
import urllib.request
from collections import OrderedDict
from modules import mealParser, scheduleParser, WTempParser, TTParser, weatherParser, log


# 급식정보 가져오기
def meal(year, month, date, req_id, debugging):
    # 자료형 변환
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    date = str(date).zfill(2)

    log.info("[#%s] meal@modules/getData.py: Started Fetching Meal Data(%s-%s-%s)" % (req_id, year, month, date))

    if not os.path.isfile('data/cache/' + year + '-' + month + '-' + date + '.json'):
        parser = mealParser.parse(year, month, date, req_id, debugging)
        if parser == "NoData" or parser == "":
            log.info("[#%s] meal@modules/getData.py: No Meal Data(%s-%s-%s)" % (req_id, year, month, date))
            return {"message": "등록된 데이터가 없습니다."}

    try:
        with open('data/cache/' + year + '-' + month + '-' + date + '.json',
                  encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
            json_data = data
    except FileNotFoundError:  # 파일 없을때
        if debugging:
            print("FileNotFound")
        log.info("[#%s] meal@modules/getData.py: No Meal Data(%s-%s-%s)" % (req_id, year, month, date))
        return {"message": "등록된 데이터가 없습니다."}
    log.info("[#%s] meal@modules/getData.py: Succeeded(%s-%s-%s)" % (req_id, year, month, date))
    return json_data


# 시간표정보 가져오기
def tt(tt_grade, tt_class, year, month, date, req_id, debugging):
    tt_weekday = datetime.date(year, month, date).weekday()

    log.info("[#%s] tt@modules/getData.py: Started Fetching Timetable Data(%s-%s, %s-%s-%s)"
             % (req_id, tt_grade, tt_class, year, month, date))

    if tt_weekday >= 5:  # 토요일, 일요일 제외
        log.info("[#%s] tt@modules/getData.py: No Timetable Data(%s-%s, %s-%s-%s)"
                 % (req_id, tt_grade, tt_class, year, month, date))
        return "등록된 데이터가 없습니다."

    data = TTParser.parse(tt_grade, tt_class, year, month, date, req_id, debugging)

    if not data:
        log.info("[#%s] tt@modules/getData.py: No Timetable Data(%s-%s, %s-%s-%s)"
                 % (req_id, tt_grade, tt_class, year, month, date))
        return "등록된 데이터가 없습니다."

    def wday(tt_weekday):
        if tt_weekday == 0:
            return "월"
        elif tt_weekday == 1:
            return "화"
        elif tt_weekday == 2:
            return "수"
        elif tt_weekday == 3:
            return "목"
        elif tt_weekday == 4:
            return "금"
        elif tt_weekday == 5:
            return "토"
        elif tt_weekday == 6:
            return "일"
        else:
            return "오류"

    # 헤더 작성. n학년 n반, yyyy-mm-dd(요일): 형식
    header = ("%s학년 %s반,\n%s(%s):\n" % (
        tt_grade, tt_class, datetime.date(year, month, date), wday(tt_weekday)))
    if debugging:
        print(header)

    # 본문 작성
    body = str()
    for i in range(len(data)):
        if "[MSG]" in data[i]:  # 파서 메세지에는 아무것도 붙이지 않음
            body = body + "\n%s" % data[i].replace("[MSG]", "")
        else:
            body = body + "\n%s교시: %s" % (i+1, data[i])

    log.info("[#%s] tt@modules/getData.py: Succeeded(%s-%s, %s-%s-%s)"
             % (req_id, tt_grade, tt_class, year, month, date))

    return header + body


# 학사일정 가져오기
def schdl(year, month, date, req_id, debugging):
    # 자료형 변환
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    date = str(date).zfill(2)

    log.info("[#%s] schdl@modules/getData.py: Started Fetching Schedule Data(%s-%s-%s)" % (req_id, year, month, date))

    # 파일 없으면 생성
    if not os.path.isfile('data/cache/Cal-%s-%s.json' % (year, month)):
        scheduleParser.parse(year, month, req_id, debugging)

    try:
        with open('data/cache/Cal-%s-%s.json' % (year, month),
                  encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
    except FileNotFoundError:  # 파일 없을때
        if debugging:
            print("FileNotFound")
        log.info("[#%s] schdl@modules/getData.py: No Schedule Data(%s-%s-%s)" % (req_id, year, month, date))
        return "일정이 없습니다."

    # 일정 있는지 확인
    if date in data:
        log.info("[#%s] schdl@modules/getData.py: Succeeded(%s-%s-%s)" % (req_id, year, month, date))
        return data[date]
    log.info("[#%s] schdl@modules/getData.py: No Schedule Data(%s-%s-%s)" % (req_id, year, month, date))
    return "일정이 없습니다."


# 학사일정 가져오기 (다중)
def schdl_mass(start, end, req_id, debugging):
    between_month = list()
    between_date = list()
    schdl = list()

    log.info("[#%s] schdl_mass@modules/getData.py: Started Fetching Mass Schedule Data(%s ~ %s)" % (req_id, start, end))

    delta = (end - start).days  # 시작일과 종료일 사이의 일수를 구함

    for i in range(delta + 1):  # 리스트에 시작일과 종료일 사이의 모든 달과 날짜를 담음
        date = start + datetime.timedelta(days=i)
        between_month.append((str(date.year).zfill(4), str(date.month).zfill(2)))
        between_date.append((str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))

    between_month = sorted(list(set(between_month)))  # List의 중복을 제거하고 정렬

    for i in between_month:  # 대상월의 캐시가 있는지 확인, 없으면 만들기
        if not os.path.isfile('data/cache/Cal-%s-%s.json' % (i[0], i[1])):
            scheduleParser.parse(i[0], i[1], req_id, debugging)

    for i in between_date:
        try:  # 파일 열기, JSON 데이터를 딕셔너리형으로 변환
            with open('data/cache/Cal-%s-%s.json' % (i[0], i[1]),
                      encoding="utf-8") as data_file:
                data = json.load(data_file, object_pairs_hook=OrderedDict)
        except FileNotFoundError:  # 파일 없을때
            if debugging:
                print("FileNotFound")
            body = "일정이 없습니다."
            schdl.append((i[0], i[1], i[2], body))  # 년, 월, 일, 일정
            continue  # 이후 구문 실행 않음

        if i[2] in data:  # 일정이 있는지 확인
            body = data[i[2]]
        else:  # 없으면
            body = "일정이 없습니다."

        schdl.append((i[0], i[1], i[2], body))  # 년, 월, 일, 일정

    log.info("[#%s] schdl_mass@modules/getData.py: Succeeded(%s ~ %s)" % (req_id, start, end))

    return schdl


# 한강 수온 가져오기
def wtemp(req_id, debugging):
    log.info("[#%s] wtemp@modules/getData.py: Started Fetching Water Temperature Data" % req_id)
    global date, temp

    def parse():
        log.info("[#%s] wtemp@modules/getData.py: Started Parsing Water Temperature Data" % req_id)
        try:
            global date, temp
            parser = WTempParser.get(req_id, debugging)
            date = parser[0]
            temp = parser[1]
        except Exception:
            log.err("[#%s] wtemp@modules/getData.py: Failed to Fetch Water Temperature Data" % req_id)
            return "측정소 또는 서버 오류입니다."
        if not temp.isalpha():  # 무효값 걸러냄(값이 유효할 경우에만 캐싱)
            with open('data/cache/wtemp.json', 'w',
                      encoding="utf-8") as make_file:  # 캐시 만들기
                json.dump({"timestamp": int(date.timestamp()), "temp": temp}, make_file, ensure_ascii=False, indent="\t")
                print("File Created")
                temp = temp + "°C"
        log.info("[#%s] wtemp@modules/getData.py: Succeeded" % req_id)

    if os.path.isfile('data/cache/wtemp.json'):  # 캐시 있으면
        try:
            log.info("[#%s] wtemp@modules/getData.py: Read Data in Cache" % req_id)
            with open('data/cache/wtemp.json', encoding="utf-8") as data_file:  # 캐시 읽기
                data = json.load(data_file, object_pairs_hook=OrderedDict)
        except Exception:  # 캐시 읽을 수 없으면
            try:
                os.remove('data/cache/wtemp.json')  # 캐시 삭제
            except Exception:
                log.err("[#%s] wtemp@modules/getData.py: Failed to Delete Cache" % req_id)
                return "측정소 또는 서버 오류입니다."
            parse()  # 파싱
        # 캐시 유효하면
        if (datetime.datetime.now() - datetime.datetime.fromtimestamp(data["timestamp"])
                < datetime.timedelta(minutes=76)):  # 실시간수질정보시스템상 자료처리 시간 고려, 유효기간 76분으로 설정
            log.info("[#%s] wtemp@modules/getData.py: Use Data in Cache" % req_id)
            date = datetime.datetime.fromtimestamp(data["timestamp"])
            temp = data["temp"] + "°C"
        else:  # 캐시 무효하면
            log.info("[#%s] wtemp@modules/getData.py: Cache Expired" % req_id)
            parse()  # 파싱
    else:  # 캐시 없으면
        log.info("[#%s] temp@modules/getData.py: No Cache" % req_id)
        parse()  # 파싱

    time = date.hour
    # 24시간제 -> 12시간제 변환
    if time == 0 or time == 24:  # 자정
        time = "오전 12시"
    elif time < 12:  # 오전
        time = "오전 %s시" % time
    elif time == 12:  # 정오
        time = "오후 12시"
    else:  # 오후
        time = "오후 %s시" % (time - 12)

    body = "%s %s 측정자료:\n한강 수온은 %s 입니다." % (date.date(), time, temp)
    log.info("[#%s] wtemp@modules/getData.py: Succeeded" % req_id)

    return body


# 날씨 가져오기
def weather(date_ko, req_id, debugging):
    global weather_data
    now = datetime.datetime.now()
    log.info("[#%s] weather@modules/getData.py: Started Fetching Weather Data" % req_id)

    # 날씨 파싱 후 캐싱
    def parse():
        global weather_data

        log.info("[#%s] weather@modules/getData.py: Started Parsing Weather Data" % req_id)

        weather_data = weatherParser.parse(req_id, debugging)

        # 지금의 날짜와 시간까지만 취함
        weather_data["Timestamp"] = int(datetime.datetime(now.year, now.month, now.day, now.hour).timestamp())

        with open('data/cache/weather.json', 'w',
                  encoding="utf-8") as make_file:  # 캐시 만들기
            json.dump(weather_data, make_file, ensure_ascii=False, indent="\t")
            print("File Created")

        log.info("[#%s] weather@modules/getData.py: Succeeded" % req_id)

    if os.path.isfile('data/cache/weather.json'):  # 캐시 있으면
        try:
            log.info("[#%s] weather@modules/getData.py: Read Data in Cache" % req_id)
            with open('data/cache/weather.json', encoding="utf-8") as data_file:  # 캐시 읽기
                data = json.load(data_file, object_pairs_hook=OrderedDict)
        except Exception:  # 캐시 읽을 수 없으면
            try:
                os.remove('data/cache/weather.json')  # 캐시 삭제
            except Exception:
                log.err("[#%s] weather@modules/getData.py: Failed to Delete Cache" % req_id)
                return "측정소 또는 서버 오류입니다."
            parse()  # 파싱
        # 캐시 유효하면
        if now - datetime.datetime.fromtimestamp(data["Timestamp"]) < datetime.timedelta(hours=1):
            global weather_data
            log.info("[#%s] weather@modules/getData.py: Use Data in Cache" % req_id)
            weather_data = data
        else:  # 캐시 무효하면
            log.info("[#%s] weather@modules/getData.py: Cache Expired" % req_id)
            parse()  # 파싱
    else:  # 캐시 없으면
        log.info("[#%s] weather@modules/getData.py: No Cache" % req_id)
        parse()  # 파싱

    return_data = ("🌡️ %s 최소/최대 기온: %s℃/%s℃\n\n"
                   "등굣길 예상 날씨: %s\n"
                   "🌡️ 기온: %s℃\n"
                   "🌦️ 강수 형태: %s\n"
                   "❔ 강수 확률: %s%%\n"
                   "💧 습도: %s%%"
                   % (date_ko, weather_data['temp_min'], weather_data['temp_max'], weather_data['sky'],
                      weather_data['temp'], weather_data['pty'], weather_data['pop'], weather_data['reh'])
                   )

    log.info("[#%s] weather@modules/getData.py: Succeeded" % req_id)

    return return_data


# 커밋 가져오기
def commits(req_id, debugging):
    # GitHub API 사용
    # API 사양은 https://developer.github.com/v3/repos/commits/#list-commits-on-a-repository 참조
    try:
        response = (
            urllib.request.urlopen(url="https://api.github.com/repos/hgyoseo/hdmeal/commits").read().decode('utf-8')
        )
        data = json.loads(response)
    except Exception as error:
        if debugging:
            print(error)
        log.err("[#%s] commits@modules/getData.py: Failed to Parse Commits" % req_id)
        return error

    # 마지막 커밋이 일어난 시간를 파싱함
    # 시간은 UTC 기준, datetime에서 인식할 수 있게 하기 위해 Z를 떼고 9시간을 더해 한국 표준시로 변환
    updated_at_datetime = (datetime.datetime.fromisoformat(data[0]["commit"]["committer"]["date"].replace("Z", ""))
                           + datetime.timedelta(hours=9))
    updated_at = "%s년 %s월 %s일 %s시 %s분" % (
        updated_at_datetime.year, updated_at_datetime.month, updated_at_datetime.day,
        updated_at_datetime.hour, updated_at_datetime.minute
    )
    # 최근 5개 커밋의 메시지 가져오기
    messages = list(map(lambda loc: data[loc]["commit"]["message"], range(5)))
    # 리스트의 0번에 마지막 커밋 시간 삽입
    messages.insert(0, updated_at)
    log.info("[#%s] commits@modules/getData.py: Succeeded" % req_id)
    return messages


# 디버그
if __name__ == "__main__":
    log.init()
    # print(cal_mass(datetime.datetime(2019, 12, 1), datetime.datetime(2020, 2, 29), True))
    # print(tt(3, 11, 2019, 10, 25, "****DEBUG****", True))
    # print(weather(None, "****DEBUG****", True))
    print(commits("****DEBUG****", True))