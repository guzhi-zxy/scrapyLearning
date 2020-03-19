# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: main.py
@time: 2019-12-30 20:35:45
@projectExplain: 
"""


from flask import Response, Flask, request

app = Flask(__name__)

@app.route("/image", methods=['post', 'get'])
def index():
    path = request.args.get('path')
    print(path)
    path = "/Users/yundongjiutian/mywork/projects/picBed/images/%s" % path

    resp = Response(open(path, 'rb'), mimetype="image/jpeg")
    return resp

app.run(host='0.0.0.0',port=5050, debug=True)

