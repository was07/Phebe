from flask import Flask
from threading import Thread
from time import sleep
app = Flask("")

@app.route("/")
def index():
  #bot = sys.modules["__main__"].bot
  #bot.run(os.getenv('Token'))
  return '<div style="color: green; font-size: 40px">Bot is awake.</div>'


def start_server():
  if is_server_running():
    return "Server is already running"
  app.run(host='0.0.0.0', port=8080)
  return "Server started"

def is_server_running():
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
