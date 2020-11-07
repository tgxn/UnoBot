UnoBot
======

Use it like this in docker-compose:
```yaml
    unobot:
        container_name: "server_irc_unobot"
        image: frolvlad/alpine-python2:latest
        environment:
            IRC_SERVER: "irc.connct.online"
            IRC_CHANNEL: "#Uno"
            IRC_ADMINS: "tgxn,gamerx"
            IRC_NS_PW: "nickserv id pw"
        command: python /data/bot/DeeBot.py
        volumes:
            - "./UnoBot:/data/bot/"
```
