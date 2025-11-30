#!/bin/bash

# 设置环境变量
export FLASK_APP=main.py
export FLASK_ENV=development

# 启动Flask应用
flask run --host=0.0.0.0 --port=5000