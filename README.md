# QBitTorrent Bot

A bot that takes a magnet or xtravel link and automatically start to download it in qbittorrent web UI. The bot can also return the public IP of the device it is running, so that you can easily access your downloads (via a prior port-forwarding). <br>
For instance you can run the bot in an always-on Raspberry PI that also runs an emby server to easily download and get access to your films.

## Getting started

Clone the repository:
```
git clone https://github.com/puccj/qbittorrent-bot
```

Install the requirements:
```
pip install -r requirements.txt
```

Modify the `config.py` file with your information and start the bot:
```
python bot.py
```

And you are ready to go!

## Features
- Just send a magnet or xtravel link. The bot will ask you to choose a category (`film` or `TVseries`) and the download will start automatically with the right saving path
- `/ip` : Return the public IP of the device the bot is running on
- `status` : Return the status of the last 5 torrents, useful to see if they finish downloading.

## Notes
Keep in mind that:
- You can get your Telegram bot API from [BotFather](https://telegram.me/BotFather).
- Qbittorrent host should be `127.0.0.1` (localhost) if you are running the bot on the same machine where qbittorrent runs.
- Only authorized user can use the bot. This is done to prevent to expose your public IP or torrents to the public. To know your telegram user ID, you can use [userinfobot](https://t.me/userinfobot).
- You can easily get torrent links from a search using [1337x search bot](https://t.me/search_content_bot).

## Todo
- Make categories customizable
- Add superusers
- Add delete command