<a name="readme-top"></a>

<!-- GETTING STARTED -->

## Getting Started

This repository is a telegram-bot that can be used to send scheduled messages to telegram users at defined times. All kinds of messages can be sent (text, image, video, audio, file, with/without caption). In order to configure messages, you have to run the bot and open a chat - then register as an administrator by using the passphrase (see below - installation 4.).
Users can register via /start command or by being added to a telegram-group with the bot already in it. When added to the group, the bot will automatically send a welcome message and the new user can click on a button Yes/No to register for auto messages. An administrator can then add or delete auto-messages for all registeres users. Auto-messages can also be deactivated or activated without deleting them.

This Telegram-Bot is configured to be run on Heroku in combination with a MongoDB database, but it can be modified to run on any other server or database as well.

The bot consists of two main files:
Main.py: main program logic, register new users, register admin, handle messages and conversations
Clock.py: scheduler to send auto-messages at defined times, using blocking scheduler

caffeine.py: can be triggered by a third party Heroku scheduler in order to prevent idle mode (usually after 30 minutes of inactivity, depending on plan)

### Installation

1. Pull repository from GitHub and set up a Heroku server.
2. Create .env file in main folder for the environment variables
   ```sh
   BOT_TOKEN=xyz
   APP_NAME=xyz
   HEROKU_API_TOKEN=xyz
   MONGO_URI=xyz
   ```
3. Check "Procfile" to fit your dyno configuration on Heroku
   ```sh
   web: python3 main.py
   clock: python3 clock.py
   ```
4. Change the admin "passphrase" in main.py (line 413)
5. Change scheduler timezone in clock.py according to your needs
6. Push repository to Heroku, all requirements will be installed from "requirements.txt"

<p align="right">(<a href="#readme-top">back to top</a>)</p>
