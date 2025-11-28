#include <Arduino.h>
#include "util.h"
#include "hoverserial.h"

// ------------------- Config -------------------
#define BAUDRATE 4800  // Baud rate for hoverboard communication
#define SEND_MILLIS 100  // Command send interval
#define ABS(x) ((x) < 0 ? -(x) : (x))  // Macro for absolute value calculation

// ------------------- Globals -------------------
unsigned long iNext = 0;              // Timing for next command
unsigned long iTimeNextState = 3000;  // Timing for next state change
uint8_t wState = 1;                   // Motor state
int iMax = 500;                       // Maximum speed amplitude for zigzag
int iPeriod = 3;                      // Zigzag period (in seconds)
HardwareSerial& oSerialHover = Serial1;  // Reference to Serial1 (UART)
unsigned long iNow;                   // Current time in milliseconds

// ------------------- Helpers -------------------
inline int CLAMP(int val, int minVal, int maxVal) {
  if (val < minVal) return minVal;
  if (val > maxVal) return maxVal;
  return val;
}

// ------------------- Setup -------------------
void setup() {
  Serial.begin(115200);  // Debugging communication
  Serial.println("Hoverboard Test Starting...");
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize UART for hoverboard
  oSerialHover.begin(BAUDRATE, SERIAL_8N1, SERIAL_FULL, 1, false);
  Serial.println("Hoverboard UART initialized.");
}

// ------------------- Loop -------------------
void loop() {
  iNow = millis();  // Current time in milliseconds

  // LED heartbeat (blinks every 1 second)
  digitalWrite(LED_BUILTIN, (iNow % 1000) < 200);

  // // Calculate dynamic speed (zigzag behavior)
  // float fScaleMax = 1.6 * (CLAMP(iPeriod, 3, 9) / 9.0);  // Flatten sine curve
  // int iSpeed = CLAMP((fScaleMax * iMax / 100) *
  //                    (ABS((int)((iNow / iPeriod + 250) % 1000) - 500) - 250),
  //                    -iMax, iMax);
  // int iSteer = 1 * (ABS((int)((iNow / 400 + 100) % 400) - 200) - 100);

  //Update state every 3 seconds
  // if (iNow > iTimeNextState) {
  //   iTimeNextState = iNow + 3000;
  //   wState = wState << 1;
  //   if (wState >= 64) wState = 1;  // Cycle states
  // }

  // Send motor commands at defined intervals
  // if (iNow > iNext) {
  //   iNext = iNow + SEND_MILLIS;

  //   // Left motor: dynamic speed + steer
  //   HoverSend(oSerialHover, 0, CLAMP(iSpeed + iSteer, -iMax, iMax), wState);

  //   // Right motor: negative dynamic speed + steer
  //   HoverSend(oSerialHover, 1, CLAMP(-iSpeed + iSteer, -iMax, iMax), wState);

  //   // Debugging
  //   Serial.print("Sent Motor Commands: iSpeed=");
  //   Serial.print(iSpeed);
  //   Serial.print(", iSteer=");
  //   Serial.println(iSteer);
  // }

  if (iNow > iNext) {
    iNext = iNow + SEND_MILLIS;

    HoverSend(oSerialHover, 0, 1000, 0, 0);
    Serial.print("Sent Motor Commands: ");
    Serial.println(iNow);
    
  }


}