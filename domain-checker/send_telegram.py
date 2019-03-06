#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os


import requests


token = os.getenv('BOT_TOKEN')
chat = os.getenv('CHAT')
def send(message):
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(token)
    r = requests.post(url, json = {'chat_id': chat, 'text': message})

