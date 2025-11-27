#define _DEBUG

#include <Arduino.h>
#include "util.h"
#include "hoverserial.h"

// ------------------- Config -------------------
#define BAUDRATE 19200
#define SEND_MILLIS 100
#define LED_PIN 2

// Optional manual motor pins (only used if MANUAL_CONTROL is true)
#define MOTOR_LEFT_PIN 5
#define MOTOR_RIGHT_PIN 4

#define MANUAL_CONTROL false  // set true to drive motors via pins instead of hoverboard serial

// ------------------- Globals -------------------
SerialHover2Server oHoverFeedback;

uint8_t iSendId = 0;
int iMax = 500;
int iPeriod = 3;
unsigned long iNext = 0;

// ------------------- Helpers -------------------
inline int CLAMP(int val, int minVal, int maxVal) {
  if (val < minVal) return minVal;
  if (val > maxVal) return maxVal;
  return val;
}

// ------------------- Setup -------------------
void setup() {
  Serial.begin(115200);
  Serial.println("ESP8266 Hoverboard Demo");

  pinMode(LED_PIN, OUTPUT);

  if (!MANUAL_CONTROL) {
    Serial1.begin(BAUDRATE);  // Hoverboard serial
  } else {
    pinMode(MOTOR_LEFT_PIN, OUTPUT);
    pinMode(MOTOR_RIGHT_PIN, OUTPUT);
  }
}

// ------------------- Main Loop -------------------
void loop() {
  unsigned long iNow = millis();

  // Blink LED as heartbeat
  digitalWrite(LED_PIN, (iNow % 1000) < 200);

  // Calculate speed and steering
  int iSpeed = CLAMP(
    (int)((1.6f * (float)iMax / 100.0f) * (abs((long)((iNow / iPeriod + 250) % 1000 - 500)) - 250)),
    -iMax, iMax
  );

  int iSteer = (int)(abs((long)((iNow / 400 + 100) % 400 - 200)) - 100);

  // Receive hoverboard feedback
  if (!MANUAL_CONTROL) {
    while (Receive(Serial1, oHoverFeedback)) {
      DEBUGT("iSpeed", iSpeed);
      HoverLog(oHoverFeedback);
    }
  }

  // Send commands at intervals
  if (iNow > iNext) {
    iNext = iNow + SEND_MILLIS;

    if (!MANUAL_CONTROL) {
      switch(iSendId++) {
        case 0:
          HoverSend(Serial1, 0, CLAMP(iSpeed + iSteer, -iMax, iMax), 1);
          break;
        case 1:
          HoverSend(Serial1, 1, -CLAMP(iSpeed - iSteer, -iMax, iMax), 1);
          iSendId = 0;
          break;
      }
    } else {
      // Manual pin-based motor control (example: PWM)
      int leftMotor = CLAMP(iSpeed + iSteer, -iMax, iMax);
      int rightMotor = CLAMP(iSpeed - iSteer, -iMax, iMax);

      // Map from -iMax..iMax to 0..255 for analogWrite
      analogWrite(MOTOR_LEFT_PIN, map(leftMotor, -iMax, iMax, 0, 255));
      analogWrite(MOTOR_RIGHT_PIN, map(rightMotor, -iMax, iMax, 0, 255));
    }
  }
}
