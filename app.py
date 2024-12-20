from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
import os, io, sys
import numpy as np
import cv2
import base64
import pickle

from train_model import CurrencyNotesDetection
from englisttohindi.englisttohindi import EngtoHindi
sys.path.insert(0, './yolov5')

app = Flask(__name__)


############################################## THE REAL DEAL STARTS HERE ###############################################
@app.route('/detectObject', methods=['POST'])
def mask_image():
    #################################################
    file = request.files['image'].read() ## byte file
    # npimg = np.fromstring(file, np.uint8)
    npimg = np.frombuffer(file,np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)[:, :, ::-1]

    img,text = detect_image(img)
    if(text.lower() == "image contains"):
        text = ""

    if(len(text) == 0):
        text = "Reload the page and try with another better image"
    
    englishtext = text
    hinditext = EngtoHindi(text).convert
    
    # below encodes the detected image as it sent to server back
    """
    rawBytes = io.BytesIO()
    img = Image.fromarray(img.astype("uint8"))
    img.save(rawBytes,"JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())
    return jsonify({'status':str(img_base64)})
    """
    bufferedBytes = io.BytesIO()
    img_base64 = Image.fromarray(img)
    img_base64.save(bufferedBytes, format="JPEG")
    img_base64 = base64.b64encode(bufferedBytes.getvalue())
    return jsonify({'status':str(img_base64),'englishmessage':englishtext, 'hindimessage':hinditext})

################################## THE MAIN PART IS DONE ABOVE #########################################################


@app.route('/')
def home():
    return render_template('index.html')

@app.after_request
def after_request(response):
    print("log: setting cors", file=sys.stderr)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


model=pickle.load(open("model.pkl", 'rb'))
def detect_image(img):
    detected_labels_text = ""
    detected_img,detected_labels_text = model.get_detected_image(img)
    return detected_img, detected_labels_text

if __name__ == '__main__':
	# app.run(debug=True) 
    # when run using above command change localhost/5000 default port in index.js file
    # In order to work for any device connected to wifi/LAN same network, use below
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=False)
    # make threaded=True for concurrent users
    # ip = "0.0.0.0" matches all ip address, and server listens to all ip address requests
    # below method is for devices connected to Wifi/ LAN
    # using ifconfig/ipconfig cmd in terminal find ip
    # app.run(debug=False, host="xxx.xxx.xxx.xxx",port=8080)
    # change the route path in index.js with http://host_ip:port/