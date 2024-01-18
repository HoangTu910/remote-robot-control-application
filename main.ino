#define MAX_SPEED 255
#include <SoftwareSerial.h>

int speed = 125;
String cmd;
String prev_cmd;
String mode;

SoftwareSerial bluetooth(0, 1);  // RX, TX

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
}

void forward(int speed){
  analogWrite(2, speed);
  analogWrite(7, MAX_SPEED);

  analogWrite(3, speed);
  analogWrite(4, 0);
  analogWrite(5, speed);
  analogWrite(6, 0);
}

void stop(int speed){
  analogWrite(2, 0);
  analogWrite(7, 0);

  analogWrite(3, 0);
  analogWrite(4, 0);
  analogWrite(5, 0);
  analogWrite(6, 0);
}


void left(int speed){
  analogWrite(2, speed);
  analogWrite(7, MAX_SPEED);

  analogWrite(3, 0);
  analogWrite(4, speed);
  analogWrite(5, speed);
  analogWrite(6, 0);
}


void right(int speed){
  analogWrite(2, MAX_SPEED);
  analogWrite(7, speed);

  analogWrite(3, speed);
  analogWrite(4, 0);
  analogWrite(5, 0);
  analogWrite(6, speed);
}
void loop() {
  while(Serial.available() == 0);
  cmd = Serial.readStringUntil('\r');
  Serial.println(cmd);
  // if(cmd == prev_cmd){
  //   return;
  // }

  // prev_cmd = cmd;
  if(cmd == "4"){
    mode = "4";
  }

  else if(cmd == "5"){
    mode = "5";
  }

  else if(cmd == "6"){
    mode = "6";
  }

  if(mode == "4"){
    if(cmd == "0"){
      forward(speed);
    }
    if(cmd == "1"){
      stop(speed);
    }
    if(cmd == "2"){
      left(speed);
    }
    if(cmd == "3"){ 
      right(speed);
    }
  }

  else if(mode == "5"){
    left(speed);
  }

  else if(mode == "6"){
    stop(speed);
  }

}
  

  // if(cmd == "5"){
  //   while(cmd != "4" || cmd != "6"){
  //     left(speed);
  //     delay(500);
  //     right(speed);
  //     delay(500);
  //   }
  // }

  // if(cmd == "6"){
  //   while(cmd != "4" || cmd != "5"){
  //     stop(speed);
  //   }
  // }
  
