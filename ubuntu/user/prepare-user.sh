#!/bin/bash

# restore dconf settings like hot cornets; week days, etc
cat "$(dirname $0)/user/dconf" | dconf load /

mv "${HOME}/.bashrc" "${HOME}/.bashrc-$(date +%s)"
cp "$(dirname $0)/user/bashrc" "${HOME}/.bashrc"
