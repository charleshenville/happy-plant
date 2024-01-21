#include <Adafruit_MotorShield.h>
// #include <hp_BH1750.h>

#define MOTOR_A_TERMINAL 1
#define MOTOR_B_TERMINAL 2
#define MOTOR_C_TERMINAL 3
#define MOTOR_D_TERMINAL 4

// #define IR_PIN_1 A0
// #define IR_PIN_2 A1
// #define IR_PIN_3 A2
// #define IR_PIN_4 A4

Adafruit_MotorShield AFMS = Adafruit_MotorShield();

Adafruit_DCMotor *MOTOR_A = AFMS.getMotor(MOTOR_A_TERMINAL);
Adafruit_DCMotor *MOTOR_B = AFMS.getMotor(MOTOR_B_TERMINAL);
Adafruit_DCMotor *MOTOR_C = AFMS.getMotor(MOTOR_C_TERMINAL);
Adafruit_DCMotor *MOTOR_D = AFMS.getMotor(MOTOR_D_TERMINAL);

const int sig1pin = 12;
const int sig2pin = 13;
const int readypin = 11;
const int delaytime = 30000;
const int mvtime = 10000;

// int run;
// int buttonPin;
int whichPlant;
int go1, go2;

void setup()
{
  // run = 0; //starts stopped
  // buttonPin = A5; //whatever pin your button is plugged into

  // pinMode(buttonPin, INPUT_PULLUP);
  // // put your setup code here, to run once:
  AFMS.begin();

  Serial.begin(9600);      // Initialize serial communication
  pinMode(sig1pin, INPUT); // Set D12 as an input pin
  pinMode(sig2pin, INPUT); // Set D13 as an input pin
  pinMode(readypin, OUTPUT); // 

  // Serial.begin(9600);

  // pinMode(IR_PIN_1, INPUT);
  // pinMode(IR_PIN_2, INPUT);
  // pinMode(IR_PIN_3, INPUT);
  // pinMode(IR_PIN_4, INPUT);

  MOTOR_A->setSpeed(0);
  MOTOR_A->run(RELEASE);

  MOTOR_B->setSpeed(0);
  MOTOR_B->run(RELEASE);

  MOTOR_C->setSpeed(0);
  MOTOR_C->run(RELEASE);

  MOTOR_D->setSpeed(0);
  MOTOR_D->run(RELEASE);
}

void loop()
{

  // int SEN_1 = digitalRead(IR_PIN_1);
  // int SEN_2 = digitalRead(IR_PIN_2);
  // int SEN_3 = digitalRead(IR_PIN_3);
  // int SEN_4 = digitalRead(IR_PIN_4);

  // //Serial.print(SEN_1);

  // // Read the vale from the light sensor

  // if (SEN_1 == 1 && SEN_2 == 0 && SEN_3 == 1 && SEN_4 == 0) {
  //   moveForward();
  // }

  // if (SEN_1 == SEN_2 == SEN_3 == SEN_4){
  //   stop();
  // }

  int go1 = digitalRead(sig1pin);
  int go2 = digitalRead(sig2pin);

  whichPlant = go1 + 2*go2;
  Serial.println(whichPlant);

  switch (whichPlant)
  {
  case 0: // 00 - Stop
    stop();
    delay(delaytime); // Pause for 15 seconds
    break;

  case 1: // 01 - Move forward for 5 seconds
    moveForward();
    delay(mvtime); // Move for 5 seconds
    stop();

    digitalWrite(readypin, HIGH);
    delay(delaytime); // Pause for 15 seconds
    digitalWrite(readypin, LOW);

    moveBackward();
    delay(mvtime);
    stop();
    break;

  case 2: // 10 - Move forward for 10 seconds
    moveForward();
    delay(mvtime); // Move for 10 seconds
    stop();

    digitalWrite(readypin, HIGH);
    delay(delaytime); // Pause for 15 seconds
    digitalWrite(readypin, LOW);

    moveBackward();
    delay(2*mvtime);
    stop();
    break;
  case 3:
    moveForward();
    delay(mvtime); // Move for 10 seconds
    stop();

    digitalWrite(readypin, HIGH);
    delay(delaytime); // Pause for 15 seconds
    digitalWrite(readypin, LOW);

    moveForward();
    delay(mvtime); // Move for 10 seconds
    stop();

    digitalWrite(readypin, HIGH);
    delay(delaytime); // Pause for 15 seconds
    digitalWrite(readypin, LOW);

    moveBackward();
    delay(2*mvtime);
    stop();
    break;
  }
}

void moveForward()
{
  MOTOR_A->setSpeed(45);
  MOTOR_A->run(FORWARD);

  MOTOR_B->setSpeed(45);
  MOTOR_B->run(FORWARD);

  MOTOR_C->setSpeed(45);
  MOTOR_C->run(FORWARD);

  MOTOR_D->setSpeed(45);
  MOTOR_D->run(FORWARD);
}
void moveBackward(){
  MOTOR_A->setSpeed(45);
  MOTOR_A->run(BACKWARD);

  MOTOR_B->setSpeed(45);
  MOTOR_B->run(BACKWARD);

  MOTOR_C->setSpeed(45);
  MOTOR_C->run(BACKWARD);

  MOTOR_D->setSpeed(45);
  MOTOR_D->run(BACKWARD);
}

void stop()
{
  MOTOR_A->setSpeed(0);
  MOTOR_B->setSpeed(0);
  MOTOR_C->setSpeed(0);
  MOTOR_D->setSpeed(0);
  // MOTOR_A->run(FORWARD);
  // MOTOR_B->run(FORWARD);
  // MOTOR_C->run(FORWARD);
  // MOTOR_D->run(FORWARD);
}

// 00 car stop
// if signal 01 - stop at the first point
// if signal 10 - stop at the second point
// if signal 11 - go to both

// void rotateMotorsClockwise() {
//   MOTOR_A->setSpeed(30);
//   MOTOR_D->setSpeed(20);
//   MOTOR_A->run(BACKWARD);
//   MOTOR_D->run(BACKWARD);

//   MOTOR_B->setSpeed(250);
//   MOTOR_C->setSpeed(250);
//   MOTOR_B->run(FORWARD);
//   MOTOR_C->run(FORWARD);
// }

// void rotateMotorsCounterClockwise() {
//   MOTOR_B->setSpeed(30);
//   MOTOR_C->setSpeed(20);
//   MOTOR_B->run(BACKWARD);
//   MOTOR_C->run(BACKWARD);

//   MOTOR_A->setSpeed(250);
//   MOTOR_D->setSpeed(250);
//   MOTOR_A->run(FORWARD);
//   MOTOR_D->run(FORWARD);
// }
