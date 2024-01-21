from threading import Thread
import daily_scrum_bot
import flask_app


def keep_alive():
    t = Thread(target=flask_app.run)
    t.start()


def run_bot():
    t = Thread(target=daily_scrum_bot.main)
    t.start()


run_bot()
keep_alive()
