#!/bin/bash

API = "o.V6LChFjuMwBnctjCgBDCPQaSm67dJxTc"
MSG="$1"

curl -u $API: https://api.pushbullet.com/v2/pushes -d type=note -d title="New Job" -d body="$MSG"