#!/usr/bin/env bash
git pull
source ../sklenv/bin/activate
pip3 install -r requirements.txt
python manage.py migrate