from flask import Flask, render_template
from flask import Response
import serial
import cv2
app=Flask(__name__,template_folder='template',static_folder='static')

arduino = serial.Serial('COM3', 9600)

led_state = False

def toggle_led():
  global led_state
  if led_state:
    arduino.write(b'0')
  else:
    arduino.write(b'1')
  led_state = not led_state

def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
  app.run(host='0.0.0.0')
