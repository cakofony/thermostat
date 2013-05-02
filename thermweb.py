"""
Copyright (C) 2013 Carter Kozak c4kofony@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from flask import Flask
from flask import render_template
from flask import request
import json
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import threading

lock = threading.Lock()
websockets = set([])
conf = None #settings object gets put here
current_values = {'temp':0, 'active':'off'}

def broadcast(data):
    toremove = []
    source = None
    if "source" in data:
        source = data["source"]
        del data["source"]
    lock.acquire()
    try:
        for ws in websockets:
            try:
                if ws != source: #stops infinite loops
                    ws.send(json.dumps(data))
            except:
                toremove.append(ws)
        websockets.difference_update(toremove)
    finally:
        lock.release()

def settings_changed(new_conf):
    conf = new_conf
    broadcast(conf.to_dict())

def update_active(new_active, heat, cool, fan):
    current_values['active'] = new_active
    broadcast({'active':new_active})

def update_temperature(temp):
    current_values['temp'] = temp
    broadcast({'temp': '%.1f&deg; F' % temp})

def handle_websocket(ws):
    while True:
        message = ws.receive()
        if message is None:
            break
            print 'none message'
        else:
            message = json.loads(message)
            print 'message: '+str(message)
            if "min" in message:
                conf.set_min(float(message["min"]), ws)
            if "max" in message:
                conf.set_max(float(message["max"]), ws)
            if "fan" in message:
                conf.set_fan(message["fan"] == "on", ws)
            if "system" in message:
                conf.set_system(message["system"] == "on", ws)
                
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

def therm_app(environ, start_response):  
    path = environ["PATH_INFO"]  
    if path == "/":
        return app(environ, start_response)  
    elif path == "/websocket":
        ws = environ["wsgi.websocket"]
        if not ws in websockets:
            websockets.add(ws)
            tmpdict = conf.to_dict()
            tmpdict['active'] = current_values['active']
            tmpdict['temp'] = '%.1f&deg; F' % current_values['temp']
            if "source" in tmpdict:
                del tmpdict["source"]
            ws.send(json.dumps(tmpdict))
        handle_websocket(environ["wsgi.websocket"])
    else:  
        return app(environ, start_response)

@app.route('/')
def index():
    return render_template('index.html')
