#!/usr/bin/env python
# coding: utf-8

import random
import urllib

import requests
from chalice import Chalice
from linebot import LineBotApi
from linebot import WebhookHandler
from linebot.models import CarouselColumn
from linebot.models import CarouselTemplate
from linebot.models import LocationMessage
from linebot.models import MessageEvent
from linebot.models import TemplateSendMessage
from linebot.models import URITemplateAction


LINE_CHANNEL_ACCESS_TOKEN = ''
LINE_CHANNEL_SECRET = ''
RECRUIT_API_KEY = ''
GOOGLE_MAP_API_KEY = ''

app = Chalice(app_name='todaylunch')
app.debug = True
line_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/callback', methods=['POST'])
def callback():
    request = app.current_request

    signature = request.headers['X-Line-Signature']
    body = request.raw_body.decode('utf-8')
    handler.handle(body, signature)

    return 'HELLO'


GOURMET_ENDPOINT = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'

MAP_URL = 'https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=16&size=320x200&key={}&markers={}'


def build_static_map_url(lat, lng):
    return MAP_URL.format(lat, lng, GOOGLE_MAP_API_KEY, urllib.quote(lat + ',' + lng))


@handler.add(MessageEvent, message=LocationMessage)
def handle_locationmessage(event):
    lat = event.message.latitude
    lng = event.message.longitude

    querystring = {'key': RECRUIT_API_KEY,
                   'lat': lat,
                   'lng': lng,
                   'range': 3,
                   'lunch': 1,
                   'type': 'lite',
                   'count': 20,
                   'format': 'json'}

    url = '{}?{}'.format(GOURMET_ENDPOINT,
                         urllib.urlencode(querystring))

    r = requests.get(url)

    content = r.json()
    shops = content['results']['shop']
    random.shuffle(shops)

    columns = []

    # 5件分まわす
    for shop in shops[:5]:

        columns.append(CarouselColumn(thumbnail_image_url=build_static_map_url(shop['lat'], shop['lng']),
                                      title=shop['name'],
                                      text=shop['genre']['catch'] + '\n' + shop['catch'],
                                      actions=[URITemplateAction(label='Open', uri=shop['urls']['pc'])],))

    line_api.reply_message(event.reply_token,
                           messages=TemplateSendMessage(alt_text="お店リスト",
                                                        template=CarouselTemplate(columns=columns)))

