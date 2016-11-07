#!/usr/bin/env python
# coding: utf-8
import json

from google.appengine.api import urlfetch

from linebot import HttpClient
from linebot import HttpResponse


class RequestsHttpClient(HttpClient):

    def __init__(self, timeout=HttpClient.DEFAULT_TIMEOUT):
        super(RequestsHttpClient, self).__init__(timeout)

    def get(self, url, headers=None, params=None, stream=False, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = urlfetch.fetch(url,
                                  payload=params,
                                  method=urlfetch.GET,
                                  headers=headers,
                                  deadline=timeout)

        return RequestsHttpResponse(response)

    def post(self, url, headers=None, data=None, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = urlfetch.fetch(url,
                                  payload=data,
                                  method=urlfetch.POST,
                                  headers=headers,
                                  deadline=timeout)

        return RequestsHttpResponse(response)


class RequestsHttpResponse(HttpResponse):

    def __init__(self, response):
        self.response = response

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def text(self):
        return unicode(self.content, 'UTF-8', errors='replace')
    @property
    def content(self):
        return self.response.content

    @property
    def json(self):
        # return self.response.json()
        return json.loads(self.content)

    def iter_content(self, chunk_size=1024, decode_unicode=False):
        """Get request body as iterator content (stream).

        :param int chunk_size:
        :param bool decode_unicode:
        """
        # return self.response.iter_content(chunk_size=chunk_size, decode_unicode=decode_unicode)
        return self.content
