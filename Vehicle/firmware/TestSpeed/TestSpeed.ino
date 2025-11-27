#include <Arduino.h>
#include <SoftwareSerial.h>  // Include Software Serial library for ESP8266
#include "util.h"
#include "hoverserial.h"

// ------------------- Config -------------------
#define RX_PIN 4  // GPIO4 (D2) - Connect ESP8266 RX to Hoverboard TX
#define TX_PIN 5  // GPIO5 (D1) - Connect ESP8266 TX to Hoverboard RX
#define BAUDRATE 19200  // Hoverboard communication baud rate
#define SEND_MILLIS 50  // Communication interval
#define ABS(x) ((x) < 0 ? -(x) : (x))  // Macro for absolute value calculation

// Software Serial instance for hoverboard communication
SoftwareSerial oSerialHover(RX_PIN, TX_PIN);

// ------------------- Globals -------------------
unsigned long iNext = 0;              // Timing for next command
unsigned long iTimeNextState = 3000;  // Timing for next state change
uint8_t wState = 1;                   // Motor state (1: enabled)
int iMax = 500;                       // Maximum speed amplitude for zigzag
int iPeriod = 3;                      // Zigzag period (in seconds)
unsigned long iNow;                   // Current time in milliseconds

// ------------------- Helpers -------------------
inline int CLAMP(int val, int minVal, int maxVal) {
  if (val < minVal) return minVal;
  if (val > maxVal) return maxVal;
  return val;
}

// ------------------- CRC Calculation -------------------
uint16_t CalculateCRC(uint8_t* data, uint8_t length) {
  uint16_t crc = 0xFFFF;

  for (int i = 0; i < length; i++) {
    crc ^= data[i];
    for (int j = 0; j < 8; j++) {
      if (crc & 1) {
        crc = (crc >> 1) ^ 0xA001;  // Polynomial 0xA001
      } else {
        crc >>= 1;
      }
    }
  }

  return crc;
}

// ------------------- Send Debug Function -------------------
void HoverSendDebug(SoftwareSerial& serial, uint8_t motorId, int16_t speed, uint8_t state) {
  uint8_t packet[8];

  // Build the packet
  packet[0] = 0xFF;                         // Header byte 1
  packet[1] = 0xFF;                         // Header byte 2
  packet[2] = motorId;                      // Motor ID
  packet[3] = speed & 0xFF;                 // Speed Low Byte
  packet[4] = (speed >> 8) & 0xFF;          // Speed High Byte
  packet[5] = state;                        // State (enabled)
  packet[6] = CalculateCRC(packet, 6) & 0xFF;      // CRC Low Byte
  packet[7] = (CalculateCRC(packet, 6) >> 8) & 0xFF;  // CRC High Byte

  Serial.print("Packet Sent: ");
  for (int i = 0; i < 8; i++) {
    Serial.print("0x");
    if (packet[i] < 0x10) Serial.print("0");
    Serial.print(packet[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  serial.write(packet, 8);
}

// ------------------- Setup -------------------
void setup() {
  Serial.begin(115200);
  Serial.println("Hoverboard Test Starting...");
  oSerialHover.begin(BAUDRATE);
  Serial.println("Hoverboard Software Serial initialized.");
  pinMode(LED_BUILTIN, OUTPUT);  // Onboard LED setup
}

// ------------------- Loop -------------------
void loop() {
  iNow = millis();

  // LED heartbeat
  digitalWrite(LED_BUILTIN, (iNow % 1000) < 200);

  // Calculate dynamic speed (zigzag behavior)
  float fScaleMax = 1.6 * (CLAMP(iPeriod, 3, 9) / 9.0);
  int iSpeed = CLAMP((fScaleMax * iMax / 100) *
                     (ABS((int)((iNow / iPeriod + 250) % 1000) - 500) - 250),
                     -iMax, iMax);
  int iSteer = 1 * (ABS((int)((iNow / 400 + 100) % 400) - 200) - 100);

  // Update motor state
  if (iNow > iTimeNextState) {
    iTimeNextState = iNow + 3000;
    wState = wState << 1;
    if (wState >= 64) wState = 1;
  }

  static uint8_t motorSendState = 0;
  if (iNow > iNext) {
    iNext = iNow + SEND_MILLIS;

    if (motorSendState == 0) {
      HoverSendDebug(oSerialHover, 0, CLAMP(iSpeed + iSteer, -iMax, iMax), wState);
    } else {
      HoverSendDebug(oSerialHover, 1, CLAMP(-iSpeed + iSteer, -iMax, iMax), wState);
    }

    motorSendState ^= 1;  // Toggle between left and right motor
  }

  // Optional feedback handling (debug logs)
  SerialHover2Server oHoverFeedback;
  if (Receive(oSerialHover, oHoverFeedback)) {
    Serial.print("Feedback Received: Speed L = ");
    Serial.print(oHoverFeedback.iSpeedL);
    Serial.print(" Speed R = ");
    Serial.println(oHoverFeedback.iSpeedR);
  } else {
    Serial.println("No feedback received.");
  }
}