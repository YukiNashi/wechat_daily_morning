from datetime import date, datetime
import math

from wechatpy import WeChatClient

from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import urllib3
import json

from apscheduler.schedulers.blocking import BlockingScheduler

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

sched = BlockingScheduler()

def cron(event):
    '''
    周一至周日14：20执行任务
    '''
    sched = BlockingScheduler()
    sched.add_job(event, 'cron',  day_of_week='1-7', hour=14, minute=20)
    sched.start()

def get_weather():
  url = "https://api.map.baidu.com/weather_abroad/v1/?data_type=all&ak=4TqFCTbN37fk0AXA5g2i4Suao9rODaAC&district_id=" + city
  res = requests.get(url).json()
  weather = res['result']['now']
  location = res['result']['location']
  return weather['text'], math.floor(weather['temp']), location['city']

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days



def get_words():
    '''
    通过API获取json格式诗词、并解析出对应的 标题、作者、内容
    title:  诗词名
    author: 作者
    origin: 内容
    '''
  http = urllib3.PoolManager()
  result = http.request('GET','https://v2.jinrishici.com/sentence', headers={'X-User-Token': 'lbPaXqfSpHR9/XRM46asGkOYCshAxO5I'})
  s = json.loads(result.data)
  title = s['data']['origin']['title']
  author = s['data']['origin']['dynasty'] + '--' + s['data']['origin']['author']
  origin = json.loads(result.data)['data']['origin']['content']
  return get_words()
  return title, author, origin

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
weather, temperature, city = get_weather()
title, author, origin = get_words()
data = {
	"city": {
		"value": city,
		"color": get_random_color()
	},
	"weather": {
		"value": weather,
		"color": get_random_color()
	},
	"temperature": {
		"value": temperature,
		"color": get_random_color()
	},
	"love_days": {
		"value": get_count(),
		"color": get_random_color()
	},
	"birthday_left": {
		"value": get_birthday(),
		"color": get_random_color()
	},
	"title": {
		"value": title,
		"color": get_random_color()
	},
	"author": {
		"value": author,
		"color": get_random_color()
	},
	"origin": {
		"value": origin,
		"color": get_random_color()
	}
}
res = wm.send_template(user_id, template_id, data)
print(res)
