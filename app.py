from flask import Flask
import threading
from client import Bot

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Bharat'

def run_bot():
    print("Bot Started 👍 Powered By @unicornguardian")
    Bot().run()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=8000)
