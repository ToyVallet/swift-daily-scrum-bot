from threading import Thread
import daily_scrum_bot
import flask_app


def keep_alive():
    t = Thread(target=flask_app.run)
    t.start()


keep_alive()
daily_scrum_bot.main()
