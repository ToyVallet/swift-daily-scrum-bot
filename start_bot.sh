# !/bin/sh

CURRENT_PATH=$(pwd)

CONFIG_FILE=${CURRENT_PATH}/config.ini

DISCORD_TOKEN=$(awk '/^DISCORD_TOKEN/{print $3}' ${CONFIG_FILE})

# echo ${DISCORD_TOKEN}
export DISCORD_TOKEN=${DISCORD_TOKEN}
python daily_scrum_bot.py 
