#ifndef UTIL_H
#define UTIL_H

#include <Arduino.h> // For String, isDigit, etc.

// --- String utilities ---
inline String ShiftValue(String &sLine, const char* c)
{
  int i = sLine.indexOf(c);
  if (i == -1) return "";  // safety check
  String s = sLine.substring(0, i);
  sLine.remove(0, i + 1);
  return s;
}

inline bool isUInt(const String &str)
{
  for (size_t i = 0; i < str.length(); i++)
    if (!isDigit(str.charAt(i)))
      return false;
  return true;
}

// --- Safe math utilities ---
template <typename T>
inline T Abs(T val) { return (val < 0) ? -val : val; }

template <typename T>
inline T Clamp(T val, T low, T high) { 
  if (val < low) return low;
  if (val > high) return high;
  return val;
}

template <typename T>
inline T MapVal(T x, T xMin, T xMax, T yMin, T yMax) {
  return (x - xMin) * (yMax - yMin) / (xMax - xMin) + yMin;
}

// --- Debug macros ---
#ifdef _DEBUG
  #define DEBUG(txt, val) {Serial.print(F(txt)); Serial.print(F(": ")); Serial.print(val);}
  #define DEBUGT(txt, val) {Serial.print(F(txt)); Serial.print(F(": ")); Serial.print(val); Serial.print(F("\t"));}
  #define DEBUGTX(txt, val) {Serial.print(F(txt)); Serial.print(F(": ")); Serial.print(val, HEX); Serial.print(F("\t"));}
  #define DEBUGTB(txt, val) {Serial.print(F(txt)); Serial.print(F(": ")); Serial.print(val, BIN); Serial.print(F("\t"));}
  #define DEBUGN(txt, val) {Serial.print(F(txt)); Serial.print(F(": ")); Serial.println(val);}
#else
  #define DEBUG(txt, val)
  #define DEBUGT(txt, val)
  #define DEBUGTX(txt, val)
  #define DEBUGTB(txt, val)
  #define DEBUGN(txt, val)
#endif

#endif // UTIL_H
