# Bill of Materials — V4

Everything needed to build **V4**. V4 is a new vehicle: new frame, new drivetrain, new motors, new
power system. The only things carried over are the compute and sensing stack (Jetson, RTK GPS,
compass, camera, modem, lights), which are listed in section 3.

Quantities for the frame and drivetrain are read straight out of the V4b CAD
(`/CAD/V4/ships/V4b/V4b.step`), so the cut lists and fastener counts are exact.

**Price key:** `~` means estimated. McMaster-Carr doesn't publish prices to search engines, so every
McMaster line is an estimate until I place the order. Prices are USD, no shipping or tax.

Wiring is in [WIRING.md](./WIRING.md).

---

## 1. Frame

All extrusion is **30 mm** T-slot (confirmed by the bracket the CAD uses — McMaster 3136N923 is the
"Flush 90 Degree Angle Bracket for 30mm High Rail"). Cut list from the CAD:

| Item | Qty | Price | Source |
| ---- | --- | ----- | ------ |
| 30 mm T-slot extrusion — 700 mm | 2 | — | McMaster-Carr |
| 30 mm T-slot extrusion — 343 mm | 2 | — | McMaster-Carr |
| 30 mm T-slot extrusion — 240 mm | 6 | — | McMaster-Carr |
| 30 mm T-slot extrusion — 141 mm | 4 | — | McMaster-Carr |
| 30 mm T-slot extrusion — 100 mm | 4 | — | McMaster-Carr |
| 30 mm T-slot extrusion — 40 mm | 4 | — | McMaster-Carr |
| ↳ **4.65 m of extrusion**, bought as stock lengths and cut down | — | ~$150 | McMaster-Carr |
| 3-way 90° corner joint | 8 | ~$12 ea = ~$96 | McMaster [5537T864](https://www.mcmaster.com/5537T864/) |
| 45° structural bracket (sloped nose + tail) | 8 | ~$10 ea = ~$80 | McMaster [4844N18](https://www.mcmaster.com/4844N18/) |
| Flush 90° angle bracket, 30 mm rail | 4 | ~$8 ea = ~$32 | McMaster [3136N923](https://www.mcmaster.com/3136N923/) |
| T-slot nuts, screws and washers for all joints | ~120 | ~$50 | McMaster-Carr |
| Aluminum composite sheet, 24" × 60" × 1/8" black | 1 | $71.78 | [Home Depot — Falken ACM-BK-1/8-2460](https://www.homedepot.com/p/Falken-Design-24-in-x-60-in-x-1-8-in-Thick-Aluminum-Composite-ACM-Black-Sheet-Falken-Design-ACM-BK-1-8-2460/308670306) |
| ↳ cut by me into: left side, right side, front short, rear short, bottom | 5 panels | — | from sheet above |
| Front + rear bent panels — laser cut and bent | 2 | ~$90 | SendCutSend |
| Gasket / weatherstrip for the panel seams | 1 | ~$15 | Amazon |
| **Subtotal** | | **~$585** | |

The sheet is 9,120 cm² and the panels need ~3,280 cm², so one sheet covers it with room for mistakes.
Only the two bent panels go to SendCutSend — a plain rectangle was $36 there vs ~$5 of sheet cut at home.

## 2. Drivetrain

Beam axle. One motor per axle, belt down to an idler, second belt to a differential, then U-jointed
rods out to the wheels.

**The V4b CAD contains the front axle only.** The quantities below are for that one axle as modeled.
The full vehicle is 4WD, so double everything (the journal prices 2 diffs, not 1) — that's the
"×2 axles" column.

| Item | Qty / axle | ×2 axles | Price (both axles) | Source |
| ---- | ---------- | -------- | ------------------ | ------ |
| Flipsky 6384 190 KV sensored BLDC motor | 1 | 2 | ~$119 ea = ~$238 | [Flipsky](https://flipsky.net/collections/hobby-motors-for-esk8-ebike-efoil) |
| Flipsky VESC (motor controller) | 1 | 2 | ~$80 ea = ~$160 | Flipsky |
| Differential — gears, cross pins, 10×0.2 shims | 1 | 2 | <$100 total | AliExpress, built to [this GrabCAD diff](https://grabcad.com/library/differential-for-rc-quarterscale-cars) scaled up |
| 3D printed diff housing + mounts (PETG) | 1 set | 2 | ~$10 filament | Self-printed |
| HTD 3M 24-tooth pulley, 6 mm bore | 2 | 4 | ~$8 ea = ~$32 | AliExpress |
| HTD 3M belt, 174 mm (motor → idler) | 1 | 2 | ~$6 ea = ~$12 | AliExpress |
| HTD 3M belt (idler → diff) | 1 | 2 | ~$6 ea = ~$12 | AliExpress |
| 440C stainless ball bearing (idler) | 2 | 4 | ~$6 ea = ~$24 | McMaster [4668K235](https://www.mcmaster.com/4668K235/) |
| Idler pulley bearing, p/n 17021800 | 2 | 4 | ~$5 ea = ~$20 | AliExpress |
| 6 mm jack rod (idler shaft) | 1 | 2 | ~$5 ea = ~$10 | McMaster-Carr |
| 8 mm U-joint | 2 | 4 | ~$12 ea = ~$48 | AliExpress |
| 8 mm steel rod — 25 / 34 / 34 / 41 mm cuts | 4 | 8 | ~$15 total | McMaster-Carr |
| 8 mm rod → 12 mm hex wheel adapter | 2 | 4 | ~$10 ea = ~$40 | AliExpress |
| Wheel + tire, 1/5 scale | 2 | 4 | ~$25 ea = ~$100 | AliExpress |
| Mounting plate, motor mount, 2× idler bearing mount — 1/8" (3.2 mm) bent sheet | 1 set | 2 | ~$45 ea = ~$90 | SendCutSend |
| M5 socket head screw, motor to mount | 4 | 8 | ~$10 | McMaster [91292A116](https://www.mcmaster.com/91292A116/) |
| M5 socket head screw, motor mount + idler bolts | 7 | 14 | ~$14 | McMaster [91292A117](https://www.mcmaster.com/91292A117/) |
| Steel hex nut, motor mount | 4 | 8 | ~$5 | McMaster [90592A011](https://www.mcmaster.com/90592A011/) |
| Steel hex nut, idler bolts | 3 | 6 | ~$4 | McMaster [90592A090](https://www.mcmaster.com/90592A090/) |
| Black coated steel washer, motor mount | 4 | 8 | ~$5 | McMaster [93413A211](https://www.mcmaster.com/93413A211/) |
| **Subtotal (both axles)** | | | **~$944** | |

## 3. Power and electronics

The Jetson, GPS, compass, camera, modem and lights move over from V3 unchanged — everything below
the double line is new for V4.

| Item | Qty | Price | Source |
| ---- | --- | ----- | ------ |
| 6S LiPo pack — 2 in series gives 12S / 44.4 V | 2 | ~$130 ea = ~$260 | Hobby shop |
| Anti-spark switch + inline fuse (12S) | 1 | ~$25 | Amazon |
| Buck converter, 44.4 V → 5 V | 1 | ~$15 | Amazon |
| XT90 connectors, 10 AWG silicone wire, heat shrink | lot | ~$30 | Amazon |
| — *carried over from V3* — | | | |
| NVIDIA Jetson Orin Nano Super Dev Kit | 1 | $249 paid (now $399) | [NVIDIA](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/) |
| 512 GB NVMe SSD (boot drive) | 1 | ~$40 | Amazon |
| SparkFun GPS-RTK2 — ZED-F9P (Qwiic) | 1 | $259.95 | [SparkFun GPS-15136](https://www.sparkfun.com/sparkfun-gps-rtk2-board-zed-f9p-qwiic-gps-15136.html) |
| GNSS L1/L2 antenna + SMA cable | 1 | ~$70 | SparkFun |
| Waveshare SIM7600G-H 4G USB dongle + antenna | 1 | ~$70 | [Waveshare](https://www.waveshare.com/sim7600g-h-4g-dongle.htm) |
| LTE SIM + data plan | 1 | ~$10/mo | Carrier |
| Adafruit QMC5883P magnetometer (compass) | 1 | ~$5 | Adafruit |
| USB webcam (driving camera) | 1 | ~$30 | Amazon |
| Powered USB hub | 1 | ~$20 | Amazon |
| WS2812B NeoPixel strip, 30 px | 1 | ~$10 | Amazon |
| **Subtotal** | | **~$1,084** | |

## Totals

| Section | Cost |
| ------- | ---- |
| Frame | ~$585 |
| Drivetrain (both axles) | ~$944 |
| Power and electronics | ~$1,084 |
| **Total** | **~$2,613** |

## Not in the V4 build

V1–V3 drove on two hoverboard hub motors and the two GD32 ESC boards out of a salvaged hoverboard,
running [RoboDurden's firmware](https://github.com/RoboDurden/Hoverboard-Firmware-Hack-Gen2.x-GD32).
All of that is replaced in V4 by the Flipsky motors, VESCs and the belt-and-diff drivetrain above.

Tools used but not consumed: 3D printer + PETG, soldering iron, hand tools, drill, calipers, logic
analyzer, ST-Link V2, and Fusion 360 (free hobbyist licence).
