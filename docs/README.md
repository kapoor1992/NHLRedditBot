# NHLJetsBot
Reddit bot that extracts and posts information about the Winnipeg Jets.

First, generate oAuth credits by logging into your bots account, preferences, apps, "create another app". Select script, add a fun name, and make the redirect_uri http://127.0.0.1:65010/authorize_callback

To run this script while logged into your bot's account

`python video_bot.py --bot-name <reddit-username> --dad <creator reddit username> --client-id <oAuth client ID> --client-secret <client secret>`

It will open your favourite browser with a reddit webpage requesting permissions to your account. click yes. Your URL will now look something like 'http://127.0.0.1:65010/authorize_callback?state=K3YYY&code=jRG69j-sh5sEPcrWq3L415V3yGA' the webcode is the string after 'code=''

`--web-code <web code>`

Testing is generally easier when we don't set "Read" flag on messages. if you want to read messages, you need the -r parameter.

Currently, the software doesn't automatically refresh the key on an hourly scheudle. you need to generate a new key every time you test the software (unless I'm doing something wrong).

Also, would be usefully to store these credentials in a file that we don't push to github so that we don't need to pass command line arguments all the time.

To have this process run without dieing when your terminal connection ends (on a pi or other computer), use `nohup <process> &` and it won't die on disconnection.