from flask import Flask
from threading import Thread

app = Flask('C++Bot')

@app.route('/')
def main():
  return "The cake is a lie, there is no spoon and the meaning of life is 42."

def run():
  app.run(host="0.0.0.0", port=8080)

def server_run():
  server = Thread(target=run)
  server.start()