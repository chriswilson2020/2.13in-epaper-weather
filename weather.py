#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import epd2in13bc
import requests, json
import time
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
import traceback
import threading

logging.basicConfig(level=logging.DEBUG)

REFRESH_INTERVAL = 1 # in minutes

#Prepare display
epd = epd2in13bc.EPD()
logging.info("Init and clear")
epd.init()
epd.Clear()

font12 = ImageFont.truetype('Font.ttc', 12)
font16 = ImageFont.truetype('Font.ttc', 16)

def load_api_key():
    with open("config.json") as config_json:
        config_data = json.load(config_json)
        return config_data["api_key"]

def draw_weather(locale, desc, temp, humid, feel, speed, next_rain):
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)

    margin_left = 4
    margin_top = 4
    datetime_str = time.strftime("%H:%M on %m/%d", time.localtime())

    drawblack.text((margin_left, margin_top + 0), f"Weather {locale} @ {datetime_str}", font = font12, fill = 0)
    drawblack.text((margin_left, margin_top + 16), f"Current Weather: {desc}", font = font12, fill = 0)
    drawblack.text((margin_left, margin_top + 36), f"Temp: {temp}, Humidity: {humid}%", font = font16, fill = 0)
    drawry.text((margin_left, margin_top + 54), f"Feels Like: {feel}, With Wind@ {speed}m/s", font = font12, fill = 0)
    if next_rain:
        drawry.text((margin_left, margin_top + 72), f"Rain @ {next_rain.hour}:00 on {next_rain.month}/{next_rain.day}", font = font16, fill = 0)
    else:
        drawblack.text((4, margin_top + 72), f"No rain predicted for 48 hrs", font = font16, fill = 0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))

def fetch_weather(zip_code="outside"):
    #threading.Timer(60.0 * REFRESH_INTERVAL, fetch_weather).start()
    base_url = "http://api.openweathermap.org/data/2.5/onecall"
    req_url = f"{base_url}?appid={api_key}&exclude=minutely&lat=51.833&lon=5.850&units=metric"
    response = requests.get(req_url) 
    raw_data = response.json()
    temp_F = raw_data["current"]["temp"]
    humid_pc = raw_data["current"]["humidity"]
    feels_like = raw_data["current"]["feels_like"]
    feel = round(feels_like, 0)
    wind_speed = raw_data["current"]["wind_speed"]
    rounded_temp = round(temp_F, 0)
    weather = raw_data["current"]["weather"][0]["description"]
    hourly_data = raw_data["hourly"]
    hourly_will_rain = [x["dt"] for x in hourly_data if "rain" in x["weather"][0]["main"].lower()]
    next_rain = datetime.fromtimestamp(min(hourly_will_rain)) if len(hourly_will_rain) > 0 else None
    draw_weather(zip_code, weather, rounded_temp, humid_pc, feel, wind_speed, next_rain)

api_key = load_api_key()
fetch_weather()
epd2in13bc.epdconfig.module_exit()
exit()
