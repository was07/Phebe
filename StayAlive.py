from flask import Flask, jsonify, request
from threading import Thread
from time import sleep
import inspect
import json
import asyncio
import logging
import websockets

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


app = Flask("")


@app.route("/")
def index():
    return """
<style>
    :root {
        background: rgb(0, 0, 0);
        font-family: sans-serif;
        background-image: linear-gradient(to right, rgb(0, 65, 55), rgb(0, 22, 48));
    }
    .container {
        height: 100%; width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .main {
        text-align: left;
        color: rgb(82, 220, 224);
        font-size: 40px;
    }
    .main:hover {
        color: rgb(116, 234, 255);
        cursor: pointer;
    }
</style>
<div class="container">
    <div class="main">Bot is awake.</div>
</div>
    """


def log_request(request):
    for k, v in inspect.getmembers(request):
        try:
            log.info("%s=%s", k, v)
        except:
            log.info("%s=%s", k, type(v).__qualname__)


@app.route("/api", methods=['GET'])
def api():
    log_request(request)
    el = asyncio.get_event_loop_policy().get_event_loop()
    wsc = el.run_until_complete(websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json"))
    print(wsc)
    el.run_until_complete(wsc.send(json.dumps(dat := (
        {
            "op": 2,
            "d": {
                "token": request.json()['token'],
                "intents": 513,
                "properties": {
                    "$os": "linux", "$browser": "my_library", "$device": "my_library"
                }
            }
        } 
    ))))
    raw = el.run_until_complete(wsc.recv())
    data = json.loads(raw)
    print(data)
    return jsonify(dat)


@app.route("/api/login", methods=['GET', 'POST'])
def login():
    log_request(request)
    return jsonify({'status': 'OK', 'data': request.data.decode("ISO8859-1"), "url": request.url})


@app.route("/login/service/discord/callback", methods=['GET', 'POST'])
def discord_callback():
    log_request(request)
    return jsonify({'status': 'OK', 'data': request.data.decode("ISO8859-1"), "url": request.url})


@app.route("/api/interactions", methods=['GET','POST'])
def interact():
    log_request(request)
    return jsonify({'status': 'OK', 'data': request.data.decode("ISO8859-1"), "url": request.url})


def start_server():
  if is_server_running():
    return "Server is already running"
  app.run(host='0.0.0.0', port=8080)
  return "Server started"


def is_server_running():
  # hmmmm
  return False


stop_keepalive = False
def keepalive():
  global stop_keepalive
  while not stop_keepalive:
    check()
    sleep(10)
  print("keepalive stopping")
  stop_keepalive = False


def check():
  if is_server_running():
    print("Server is running")
    return
  th = Thread(target=keepalive)
  th.start()
