import threading
import server
import bot


def run_flask():
    server.run()


def run_discord():
    bot.bot.run(bot.TOKEN)


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_discord()

# MADE BY DAI VIET
