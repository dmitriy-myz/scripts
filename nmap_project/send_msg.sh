#!/bin/bash

msg="$1"

curl -s 'https://hooks.slack.com/services/XXX/XXX/XX' \
  -d "payload={\"text\": \"hosts scanner alert $msg.\", \"icon_emoji\": \":omgcat:\", \"username\": \"hosts scanner\"}"
