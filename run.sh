#!/bin/sh

cd ~/UnoBot

if ! ps -p `cat ~/UnoBot/UnoBot.pid` > /dev/null
then
   echo "Starting UnoBot"
   screen -d -m python2 ~/UnoBot/DeeBot.py
fi

