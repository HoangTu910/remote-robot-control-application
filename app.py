from flask import Flask, render_template, request, flash, jsonify
from flask import Response
from serial.tools import list_ports
import serial
# import cv2
import cv2
# from cvzone.HandTrackingModule import HandDetector
# from cvzone.ClassificationModule import Classifier
# import numpy as np
# import math

app=Flask(__name__,template_folder='template',static_folder='static')
app.secret_key = 'your_secret_key'
led_state = False
camera = cv2.VideoCapture(0)
com_port = 'init'
baud_rate = 0

def toggle_led():
  global led_state
  if led_state:
    arduino.write(b'0')
  else:
    arduino.write(b'1')
  led_state = not led_state

def generate_frames():
    while True:
        success, frame = camera.read()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
  return render_template('index.html')

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

@app.route('/pair', methods=['GET', 'POST'])
def pair():

  com_port = request.form.get('comPort')
  baud_rate = request.form.get('baudRate')

  if not com_port:
    flash("COM PORT is required")
    return render_template('index.html')

  if not baud_rate:
    flash("BAUD RATE is required")
    return render_template('index.html')

  # Convert baud rate to int
  baud_rate = int(baud_rate)
  available_ports = [port.device for port in list_ports.comports()]
  arduino_connected = False
  if com_port not in available_ports:
    flash("Undefined COM PORT")
    return render_template('index.html')
  try:
    arduino = serial.Serial(com_port, baud_rate)
    arduino_connected = True
    flash("Connect Successful !")
    return render_template('index.html', com_port=com_port, baud_rate=baud_rate)
  except serial.SerialException:
    flash("Invalid COM PORT or BAUD RATE")

if __name__ == '__main__':
  app.run(host='0.0.0.0')


