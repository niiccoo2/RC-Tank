# Wiring Diagram — V4

How everything in the [BOM](./BOM.md) wires together on **V4**. V4 runs a 12S pack into two VESCs
driving two Flipsky BLDC motors — one per beam axle, belted to a differential. The compute and
sensing side (Jetson, RTK GPS, compass, camera, modem, lights) carries over from V3 unchanged.

Arrows with a voltage are power. Arrows with a protocol are data.

```mermaid
flowchart LR
    subgraph PACK["12S pack"]
        B1["6S LiPo<br>22.2 V"]
        B2["6S LiPo<br>22.2 V"]
    end

    subgraph FRONT["Front axle"]
        VF["Flipsky VESC<br>front"]
        MF["Flipsky 6384<br>190 KV sensored"]
        DF["Belt to idler,<br>belt to diff,<br>U-joints to 2 wheels"]
    end

    subgraph REAR["Rear axle"]
        VR["Flipsky VESC<br>rear"]
        MR["Flipsky 6384<br>190 KV sensored"]
        DR["Belt to idler,<br>belt to diff,<br>U-joints to 2 wheels"]
    end

    B1 -->|series| B2
    B2 -->|44.4 V| FUSE["Fuse +<br>anti-spark switch"]
    FUSE --> BUS["Power bus"]
    BUS -->|44.4 V| VF
    BUS -->|44.4 V| VR
    BUS -->|44.4 V| BUCK["Buck converter<br>44.4 V to 5 V"]

    BUCK -->|5 V| JET
    BUCK -->|5 V| HUB
    BUCK -->|5 V| LED

    VF -->|"3-phase + hall sensor cable"| MF
    VR -->|"3-phase + hall sensor cable"| MR
    MF -->|belts and diff| DF
    MR -->|belts and diff| DR

    JET["Jetson Orin Nano<br>40-pin header"]

    JET -->|"UART1 - pin 8 TX / pin 10 RX / pin 6 GND"| VF
    VF -->|"CAN bus"| VR
    JET -->|"I2C1 - pin 3 SDA / pin 5 SCL<br>pin 2 = 5 V, pin 9 = GND"| CMP["QMC5883P compass"]
    JET -->|"SPI0 - pin 19, 6.4 MHz"| LED["30x WS2812B NeoPixels<br>head / tail / turn"]
    JET -->|USB| HUB["Powered USB hub"]

    HUB -->|USB| CAM["USB camera"]
    HUB -->|"USB - AT / PPP"| MDM["SIM7600G-H 4G modem"]
    HUB -->|"USB - /dev/ttyACM0, 38400"| GPS["SparkFun ZED-F9P<br>RTK GPS"]

    GPS -->|SMA| ANT["GNSS L1/L2 antenna"]
    MDM -->|SMA| LTE["LTE antenna"]

    MDM -->|"internet - RTCM3 in / WebRTC + WS out"| NET(["NTRIP caster<br>+ website"])
```

## Notes

- **The 5 V rail needs its own converter.** The stack pulls ~3.2 A at 5 V (Jetson ~1 A, modem ~2 A,
  camera ~200 mA). On V3 I tried to run it off the ESC BECs, which only gave 1 A each, and it caused
  a long run of bugs that all looked like software problems. Don't repeat that.
- **12S needs an anti-spark switch,** not a bare switch — 44.4 V into the VESC caps will weld a
  plain contact.
- **One VESC is the master.** The Jetson talks UART to the front VESC only; the front VESC forwards
  to the rear over CAN. Same idea as the V3 UART bus, one link from the host instead of two.
- **Motors are sensored,** so each one needs the hall sensor cable back to its VESC as well as the
  three phase wires. Without it low-speed torque is bad, which matters for a heavy rover.
- **SPI must be enabled first** or the lights silently do nothing: run
  `sudo /opt/nvidia/jetson-io/jetson-io.py` and enable SPI1 (yes, SPI1 — it shows up as
  `/dev/spidev0.0`).
- **The compass needs its ground.** It reads garbage rather than erroring if pin 9 is missing.
- **Antennas go outside the shell.** The frame is aluminium, so the GNSS and LTE antennas need SMA
  bulkheads through the top panel.

## Jetson pin assignments

Unchanged from V3, except pins 6/8/10 now go to the front VESC instead of the hoverboard ESC.

| Pin # | Purpose  | Item              | Wire Color |
| ----- | -------- | ----------------- | ---------- |
| 2     | 5V       | Compass Power     | Red        |
| 3     | I2C1_SDA | Compass Data      | Orange     |
| 5     | I2C1_SCL | Compass Data      | Brown      |
| 6     | GND      | VESC Serial Ground | Green     |
| 8     | UART1_TX | VESC UART RX      | Purple     |
| 9     | GND      | Compass Ground    | Black      |
| 10    | UART1_RX | VESC UART TX      | Yellow     |
| 19    | SPI_0    | Lights Control    | Orange     |
