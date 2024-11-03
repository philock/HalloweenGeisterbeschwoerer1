#include <Arduino.h>
#include <Servo.h>

#define PIN_SERVO 21
#define PIN_TRIGGER 27
#define PIN_RELAIS 5

Servo myservo;  // create servo object to control a servo
const int up_pos = 100;
const int rel_pos = 70;
const int catch_pos = 155;
const int slow = 10;
const int fast = 0;
int s_pos = 0;

void move(int p, int t_stp){
  if(p - s_pos >= 0){
    for(int i = s_pos; i <= p; i++){
      myservo.write(i);
      delay(t_stp);
    }
  }
  else{
    for(int i = s_pos; i >= p; i--){
      myservo.write(i);
      delay(t_stp);
    }
  }

  s_pos = p;
}

void move_up(){
  move(catch_pos, slow);
  move(up_pos, slow);
}

void release(){
  move(rel_pos, fast);
}

void setup() {
  Serial.begin(9600);

  myservo.write(180);
  myservo.attach(PIN_SERVO);  // attaches the servo on pin 16 to the servo object
  myservo.write(180);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(PIN_RELAIS, OUTPUT);
  pinMode(PIN_TRIGGER, INPUT_PULLUP);

  digitalWrite(PIN_RELAIS, HIGH);
  move_up();
}

void rumbleMotor(int duration){
  digitalWrite(PIN_RELAIS, LOW);
  delay(duration);
  digitalWrite(PIN_RELAIS, HIGH);
}

void videoDemons(){ 
  Serial.print(6);
  release();

  rumbleMotor(1000);
  delay(3000);
  rumbleMotor(1500);
  delay(3000);
  rumbleMotor(1000);
  delay(4000);
  rumbleMotor(1000);
  delay(2000);
  
  move_up();
}

void videoFire(){
  Serial.print(7);
  release();
  delay(36000);
  move_up();
}

void loop() {

  delay(50);

  if(!digitalRead(PIN_TRIGGER)){

    if(random(2))videoDemons();
    else videoFire();
    
  }
  //delay(10000);
}