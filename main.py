#!/usr/bin/env python
# coding: utf-8
import json
import random
import urllib

import webapp2
from google.appengine.api import urlfetch

import config
from gae_http_client import RequestsHttpClient
from linebot import LineBotApi
from linebot import WebhookHandler
from linebot.models import CarouselColumn
from linebot.models import CarouselTemplate
from linebot.models import LocationMessage
from linebot.models import MessageEvent
from linebot.models import TemplateSendMessage
from linebot.models import URITemplateAction

GOURMET_ENDPOINT = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'

MAP_URL = 'https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=16&size=320x200&key={}&markers={}'


line_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN, http_client=RequestsHttpClient)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)


def build_static_map_url(lat, lng):
    return MAP_URL.format(lat, lng, config.GOOGLE_MAP_API_KEY, urllib.quote(lat + ',' + lng))


@handler.add(MessageEvent, message=LocationMessage)
def handle_locationmessage(event):
    lat = event.message.latitude
    lng = event.message.longitude

    querystring = {'key': config.RECRUIT_API_KEY,
                   'lat': lat,
                   'lng': lng,
                   'range': 3,
                   'lunch': 1,
                   'type': 'lite',
                   'count': 20,
                   'format': 'json'}

    url = '{}?{}'.format(GOURMET_ENDPOINT,
                         urllib.urlencode(querystring))

    r = urlfetch.fetch(url)

    content = json.loads(r.content)
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


class CallbackHandler(webapp2.RequestHandler):
    def post(self):
        request_body = self.request.body.decode('utf-8')
        signature = self.request.headers.get('X-Line-Signature')

        handler.handle(request_body, signature)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("I'm Recommend Lunch Bot")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/callback', CallbackHandler)
], debug=True)
