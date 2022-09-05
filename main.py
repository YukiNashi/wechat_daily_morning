from datetime import date, datetime
import math

from wechatpy import WeChatClient

from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

def get_weather():
# 调用百度天气API，获取天气、温度、地点
  url = "https://api.map.baidu.com/weather_abroad/v1/?data_type=all&district_id=FRA10017001001&ak=" + city
  res = requests.get(url).json()
  weather = res['result']['now']
  location = res['result']['location']
  return weather['text'], math.floor(weather['temp']), location['city']

def get_count():
# 计算累计日期
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday_total():
# 计算累计生日天数
  cumulative = today - datetime.strptime(birthday, "%Y-%m-%d")
  return cumulative.days

def get_birthday():
# 计算生日倒数日
  birthday1 = datetime.strptime(birthday, "%m-%d")
  next = datetime.strptime(str(date.today().year) + "-" + birthday1, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
# 调用今日诗词API，获取一句诗词
  words = requests.get("https://v1.jinrishici.com/tianqi/xingxing")
  if words.status_code != 200:
    return get_words()
  return words.json()['content']

def get_random_color():
# 随机颜色
  return "#%06x" % random.randint(0, 0xFFFFFF)

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
weather, temperature, city = get_weather()
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
	"birthday_total": {
		"value": get_birthday_total(),
		"color": get_random_color()
	},
	"birthday_left": {
		"value": get_birthday(),
		"color": get_random_color()
	},
	"words": {
		"value": get_words(),
		"color": get_random_color()
	}
}
res = wm.send_template(user_id, template_id, data)
print(res)
