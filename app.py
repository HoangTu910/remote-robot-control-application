from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, session
from flask import Response
from serial.tools import list_ports
import serial
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import arduino as arduino
# import cv2
import cv2
import pyfirmata
import time
import threading

app = Flask(__name__,template_folder='template',static_folder='static')
app.secret_key = 'your_secret_key'
cap = cv2.VideoCapture(0)
com_port = 'init'
baud_rate = 0
speed = 0
speed_get = 0
index = 10
control_mode = 'ai'
board = ''
start = 0
arduino_data = None

def toggle_led():
  global led_state
  if led_state:
    arduino.write(b'0')
  else:
    arduino.write(b'1')
  led_state = not led_state


def generate_frames():
    detector = HandDetector(maxHands=1)
    classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
    offset = 20
    imgSize = 300
    global index
    global board
    global start
    global arduino_data
    while True:
        success, frame = cap.read()
        success2, img = cap.read()
        hands, img = detector.findHands(img)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)*255
            try:
                imgCrop = img[y-offset:y+h+offset, x-offset:x+w+offset]
                try:
                    aspect_ratio = h/w
                    if aspect_ratio > 1:
                        prev_aspect = h/w
                        new_witdh = math.ceil(imgSize / prev_aspect)
                        imgResize = cv2.resize(imgCrop, (new_witdh, imgSize))
                        y_remain = math.ceil((imgWhite.shape[1] - imgResize.shape[1])/2)
                        imgWhite[0:imgResize.shape[0], y_remain:imgResize.shape[1]+y_remain] = imgResize
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    else:
                        prev_aspect = h / w
                        new_height = math.ceil(imgSize * prev_aspect)
                        imgResize = cv2.resize(imgCrop, (imgSize, new_height))
                        x_remain = math.ceil((imgWhite.shape[0] - imgResize.shape[0]) / 2)
                        imgWhite[x_remain:imgResize.shape[0]+x_remain, 0:imgResize.shape[1]] = imgResize
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    print(index)
                    if start == 1:
                        arduino_data.write(str(index).encode())
                        Received = arduino_data.readline()
                        print(Received)
                except:
                    print("Out of imgWhite")
            except:
                print("Out of imgCrop")
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def arduino_run():
    global index
    global board
    global speed_get
    pin_2 = board.get_pin('d:2:p')
    pin_3 = board.get_pin('d:3:p')
    pin_4 = board.get_pin('d:4:p')
    pin_5 = board.get_pin('d:5:p')
    pin_6 = board.get_pin('d:6:p')
    pin_7 = board.get_pin('d:7:p')
    while True:
        if index == 0:
            pin_2.write(speed_get)
            pin_7.write(1)

            pin_3.write(speed_get)
            pin_4.write(0)

            pin_5.write(speed_get)
            pin_6.write(0)

        elif index == 1:
            pin_2.write(0)
            pin_7.write(0)

            pin_3.write(0)
            pin_4.write(0)
            pin_5.write(0)
            pin_6.write(0)

        elif index == 2:
            pin_2.write(speed_get)
            pin_7.write(1)

            pin_3.write(0)
            pin_4.write(speed_get)
            pin_5.write(speed_get)
            pin_6.write(0)

        elif index == 3:
            pin_2.write(1)
            pin_7.write(speed_get)

            pin_3.write(speed_get)
            pin_4.write(0)
            pin_5.write(0)
            pin_6.write(speed_get)

        else:
            print("None")

def thread_run():
    global start
    if start == 1:
        thread = threading.Thread(target=arduino_run)
        thread.daemon = True
        thread.start()

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/index_baud')
def index_baud():
  return render_template('index.html', com_port=com_port, baud_rate=baud_rate)


@app.route('/on')
def led_on():
  toggle_led()
  return "LED turned on!"


@app.route('/off')
def led_off():
  toggle_led()
  return "LED turned off!"


@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/lock_click')
def get_lock_click():
    global control_mode
    control_mode = 'lock'
    return '', 204


@app.route('/ai_click')
def get_ai_click():
    global control_mode
    control_mode = 'ai'

    return '', 204


@app.route('/spin_click')
def get_spin_click():
    global control_mode
    control_mode = 'spin'
    return '', 204


@app.route('/get_image_source')
def get_image_source():
    global index
    if index == 0:
        image_src = "/static/Image/forward.png"
    elif index == 1:
        image_src = "/static/Image/stop.png"
    elif index == 2:
        image_src = "/static/Image/right.png"
    else:
        image_src = "/static/Image/left.png"
    return image_src


@app.route('/get_data')
def get_data():
    global index
    if index == 0:
        data = "Robot nhận tín hiệu 'forward'"
    elif index == 1:
        data = "Robot nhận tín hiệu 'stop'"
    elif index == 2:
        data = "Robot nhận tín hiệu 'right'"
    elif index == 3:
        data = "Robot nhận tín hiệu 'left'"
    else:
        data = "Chờ tín hiệu từ người dùng !"
    return data


@app.route('/start', methods=['GET', 'POST'])
def handle_setup():
    global index
    global control_mode
    global board
    global start
    global speed_get
    start_click = 'start';
    start = 1
    session['slider'] = (request.form.get('slider'))
    speed = session.get('slider')
    speed = int(speed)
    print(type(speed))
    speed_get = speed/255
    com_port = session.get('com_port')
    baud_rate = session.get('baud_rate')
    arduino.get_speed(speed)
    modes = {
        'ai': 'AI',
        'lock': 'LOCK',
        'spin': 'SPIN'
    }
    mode_text = modes.get(control_mode, 'MODE')
    # thread_run()
    return render_template('index.html', slider=speed, com_port=com_port, baud_rate=baud_rate, control_mode=mode_text)


@app.route('/pair', methods=['GET', 'POST'])
def pair():
  global board
  global arduino_data
  session['com_port'] = request.form.get('comPort')
  session['baud_rate'] = request.form.get('baudRate')
  com_port = session.get('com_port')
  baud_rate = session.get('baud_rate')
  if not com_port:
    flash("COM PORT is required")
    return render_template('index.html')

  if not baud_rate:
    flash("BAUD RATE is required")
    return render_template('index.html')

  baud_rate = int(baud_rate)
  available_ports = [port.device for port in list_ports.comports()]
  arduino_connected = False
  if com_port not in available_ports:
    flash("Undefined COM PORT")
    return render_template('index.html')
  try:
    arduino_data = serial.Serial(com_port, baud_rate)
    flash("Connect Successful !")
    return render_template('index.html', com_port=com_port, baud_rate=baud_rate)
  except serial.SerialException:
    flash("Invalid COM PORT or BAUD RATE")


if __name__ == '__main__':

  app.run(host='0.0.0.0')
