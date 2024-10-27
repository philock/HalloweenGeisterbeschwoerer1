#include <Arduino.h>
#include <Servo.h>

#define PIN_SERVO 21
#define PIN_TRIGGER 27
#define PIN_RELAIS 5

Servo myservo;  // create servo object to control a servo
const int up_pos = 80;
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

  digitalWrite(PIN_RELAIS, LOW);
  move_up();
}

void loop() {


  delay(50);

  if(!digitalRead(PIN_TRIGGER)){
    digitalWrite(LED_BUILTIN, HIGH);

    //digitalWrite(PIN_RELAIS, HIGH);
    
    // Start video
    Serial.print(6);

    release();

    //wait for second flicker sound, turn lights back on and move shutter up
    delay(15000);
    move_up();
    //digitalWrite(PIN_RELAIS, LOW);
     
    digitalWrite(LED_BUILTIN, LOW);
  }
}