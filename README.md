## Info

I'm thinking of starting the project again and adding self driving. If I do, here is a list of things I need to do to get it working again:

* New sim card; unlimited
* Need to set up whatever server I needed for video. Might try to do this with port forwarding at home instead of paying for a vps
* Clean up this readme; might reverse the journal so you don't need to scroll as much
* Add a summary of what I added to V3 (Paint, WebRTC, think I hosted the website?)

Then, once it's all working nicely again:

* Get everything working on coral dev board
* Better headlights
* Start on self driving

Then once self driving is working:

* See how it can go faster
* Nicer frame?


This is version 2 of my RC-Tank. It is no longer a tank but whatever. I created both versions for Hack Club [Moonshot](https://moonshot.hackclub.com).

The idea of this project was simple, I had a normal rc car with camera, but it coulden't even go around the block, so I wanted something that would have much better range. Thats where using a cell modem comes in. The main (and big) disadvantage with this is latency, you need < 1.5s or else it becomes very hard to drive. I learned a lot doing this project (not done though!), I spent a lot of time learning about motor contollers and reverse engineering some hoverboard ECS's so I could use the motors I had. The main thing I want to keep working on, is the latency over cell, hopefully I can get webRTC working also. After I have a working human controled rover, then I will use it as the testbed for many more projects such as AI vision control, and GPS waypoints.

![Top view of new frame](/photos/chassis_top.jpg)

## Setup

### Install Tailscale

Go to [login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines) and follow instructions for new linux device.

### Turn off wifi power saving

```shell
sudo nano /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf
```

```ini
[connection]
wifi.powersave = 2
```

```shell
sudo systemctl restart NetworkManager
```

### Add networks and set wifi priority

```shell
sudo nmtui
```

```shell
sudo nmcli c mod "mypreferred" conn.autoconnect-priority 10
```

to set priority; higher number is higher priority.

## Turn off auto for neopixels

```shell
sudo nano /boot/firmware/config.txt

dtparam=audio=on -> dtparam=audio=off
```

then reboot

### Cmd to temp use wifi

```shell
sudo ip route del default via 192.168.1.1 dev wlan0
sudo ip route add default via 192.168.1.1 dev wlan0 metric 50
```

## Cmd to dissconnect from WiFi

```shell
sudo ip link set wlan0 down

sudo ip link set wlan0 up

```

## Journal

I did not count the time building the chassis kit.

### Thursday, October 16th | 30 minutes

Spent 30 minutes designing a simple riser so that I can fit more stuff on the tank. There is not enough room otherwise. This is mainly so I can start installing everything tmrw, once I have an idea of where things fit, I'll make a better version.
![Fusion](photos/riser_fusion.jpg)
![Wayyy too much stuff on the tank](photos/tank_with_junk.jpg)
![Profile of tank](photos/tank_profile.jpg)

### Friday, October 17th | 4 hours

#### 07:00 | 30 minutes

Tested V1 of the riser. It covered the tracks fine, but I made the screw holes too small and mismeasured where the holes in the chassis are. I spent 30 making V2 with the following improvements.

- Fix size of screw holes
- Fix chassis mountiung hole locations
- Add holes for mounting RPI Zero
- Add holes to ziptie batterys on the edge
  ![V2 of the riser in fusion](photos/riser_v2_fusion.jpg)
  ![Tank with V1 of riser](photos/tank_with_riser_v1.jpg)

#### 16:00 | 30 minutes

Took apart the car and tracks to test V2 of the riser. The mounting holes distance to edge rn is good but apparently I misread the design sheet and made them to far apart. So I made a quick edit and started V3 on the printer.
![V3 of riser in fusion](photos/riser_v3_fusion.jpg)

#### 18:30 | 1 hour

Soldered a bunch of cables to the motor controllers and did first boot of pi from the tank battery. V3 of the riser is almost done printing. Going to start researching and writing code to make the motors spin!
![Tank with pi on it](photos/tank_with_pi.jpg)

#### 20:00 | 2 hours

Got the car to drive. But one of the free wheels is locking up, v3 of the riser but finished printing so I'll fix the wheel as I put the new version on. Put V3 of riser on tank. ALL SCREWS LINE UP!!

### Saturday, October 18th | 3.25 hours

#### 10:00 | 1 hour

Added a lcd screen that displays the IP because it kept changing ip. Also wrote code so that it auto displays on boot. Right now its seprate from main.py but at some point I will find a way to intigrate once I feel safe having it auto run main.py.
![Tank with screen showing the IP](photos/tank_with_ip_screen.jpg)

#### 14:30 | 15 minutes

Seeing how quickly I'm running out of room, I designed a cover for the pi, modem and camera so that I could mount more stuff like the screen, antennas, lights, and other goodies.
![Cover in fusion](photos/cover_in_fusion.jpg)

#### 20:25 | 30 minutes

Tested the cover and made some changes and printed v2. Still going to use hot glue to mount until I redo the riser.
Changes:

- Make total width 75mm instead of 3+75+3
- Add hole for power switches
- Add hole for SMA connector
- Add hole for LCD cables
- Add notch for camera
  ![Cover V2 in fusion](photos/cover_v2_fusion.jpg)

#### 21:40 | Not logging this time

Just spent 20 minutes figuring out why code was not working, but it was because I was never pulling changes to the tank... Also forgot that a vertical cam makes a vertical stream so going to put it back into original positon and remove the notch in the cover for it. Not a big deal so not printing V3 of cover yet.

#### 22:00 | 1.5 hours

Worked on the website and debugged the twitches. I want to make the website look nicer but I'm going to get some more features working first.
Website changes:

- Embed video stream
- Add connection status
- Add var to enable or disable cam (Added, but did not add a ui switch yet)
- Add ping
- Redo layout

### Sunday, October 19th | 2 hours

#### 08:00 | 30 minutes

Installed the modem and V2 of the cover.
![Cover V2 on tank](photos/tank_with_cover_v2.jpg)
![Cover V2 on tank side view](photos/tank_with_cover_v2_side.jpg)

#### 11:00 | 30 minutes

Wrote some quick code that will set the motors to 0 if it has not gotten a cmd in the last 1000ms. To be tested.

#### 20:30 | 30 minutes

Used `sudo nmtui` to set up multiple wifi networks. Then used `nmcli c mod "mypreferred" conn.autoconnect-priority 10` to set priority; higher number is higher priority. The modem has not been set up yet but thats the idea. I'll set up the modem once I have the tank working better on wifi.
| Network Name | Priority |
| ------------ | -------- |
| home1 | 10 |
| home2 | 10 |
| phone | 20 |
| cell modem | 30 |

#### 21:00 | 30 minutes

Spend a bit trying to debug why it is sending tiny bit of power to the motors whenever we read from camera. Seems to be either power related or USB interferince. Tmrw I'll look at the pwm signals to check how they look, as well as calculate the total power everything is drawing and the total the motor contolers can supply from the 5v rail. I think I'm pulling too much so might need a seprate buck converter.

### Monday, October 20th | 30 minutes

#### 07:20 | 30 minutes

Did some research on how much power everything draws. (Everything @ 5v). Each BEC provides 1A so 2A total. A lot of the items did not have stright answers so I'll measure myself at some point. The Pi claims it uses 2.5A but thats crazy so I'll say 1A. Next I'm going to look at the pwm signals to see if there is anything weird about them.
| Device | Power |
| ------ | ----- |
| RPI | 1A |
| Modem | 2A |
| Camera | 200mA?|
| LCD | 22mA? |
| Total | 3.2A |

I think all the weird issues are becasue we are drawing too much power from the ESC BEC's. So I'm going to find a better buck comverter to use. In the mean time I'm going to work on the website or something that is not broken.

### Tuesday, October 21st | 1 hour

#### 20:00 | 1 hour

Worked on the website.
Changes:

- Add background
- Fix setting div's
- Add switch for cam on / off (Still working on looks)

### Wendesday, October 22nd | 1 hour

#### 20:00 | 1 hour

Found a buck converter and did some testing to get it ready to be used in the tank. Also started thinking and calculating the correct size fuse to add to the battery.

### Friday, October 24th | 2 hours

#### 17:40 | 30 minutes

Designed V4 of riser. Made the whole thing widers and added holes for the cover to screw into.
![Riser V4 in fusion](/photos/riser_v4_fusion.jpg)

### 20:00 | 1.5 hours

Designed V3 of the cover. Main change were the screw holes so I don't need to use hot glue each time I want to mount it. Tmrw morning I'm going to finish some tests on the new buck converter and mount it, along with a fuse and main power switch into the tank. Then mount new cover and see if it fixed anything.
Changes:

- Add hole for GPS SMA connector.
- Add new walls
- Add hole for batt cord
- New hole for new power switch
- GPS and CELL labels
- Screw mounts

### Saturday, October 25th | 1.5 hours

#### 10:00 | 1 hour

Assembled and attached the new riser. I made the holes for the M3 screws a bit too big (3.4mm from 3mm), so that was a mess. Right now you have to take the whole tank apart to replace the riser, not the best, so I might fix that in a new version.

#### 12:00 | 30 minutes

Kept testing the buck converter (forshadowing, it was broken), it was not making sense why the voltage would colapse as soon as a load was added (24 Ohm power resistors).

### Sunday, October 26th | 2 hours

#### 10:00 | 1 hour

Found out that the buck converter I was trying to use was damaged. After I found that out and got some new ones, everything was making much more sense. The converter was able to buck a 6v input to 5v out. That is better than the specs but thats good. It was also able to power some 24 Ohm power resistors. I=V/R 5/24=0.204 ish Amps.

#### 22:00 | 1 hour

Soldered the new buck converter, fuse, and power switch into the tank. Now I need to fit this mess into the new cover I printed... After being powered on for a few secs, something starts making a weird noise, I'll look into it in the morning.

### Wendsday, October 29th | 1.30 hours

#### 20:00 | 1.30 hours

Finished making the main page look nice. Also made the IP picker screen, so when you open the site, you can just type the current ip instead of editing code. Now have to figure out why the camera is not streaming.

### Thursday, October 30th | 2.5 hours

#### 06:40 | 1 hour

Finaly put the cover on the tank, it involved a lot of pushing hard, so I'll make the next version of the cover much taller. I also need to make all the m3 screw holes smaller. And need to space the cell and GPS connectors apart more. It looks likes it's powering on but never connects to tailscale so I'll fix all of this after school.
![Tank with cover V3](/photos/tank_with_cover_v3.jpg)

#### 21:00 | 0.3 hours

Figured out why the tank is not working... I may have snaped the SD card. Just reflashed a card an now am going to set everything up again.
![Snapped SD card](/photos/snapped_sd_card.jpg)

#### 21:30 | 1 hour

Set everything up on the pi. Also wrote some instructions for setup to help me and or others next time. Debugged some issues with the website, need to make it only try to run any of the functions that use ip once the ip is set. It's also really laggy, but I'll fix that in the morning.

#### 22:30 | 0.2 hours

~~Site seems to not work when hosted on vercel, only works on localhost. This is probably due to the fact that its trying to call the API requests from the backend, not the client.~~ I think that was just becasue the site was not working in general... Anyways, fixed the site, so now you can enter the IP and it actually tries to connect.

### Saturday, November 1st | 3.5 Hours

#### 12:00 | 1.5 hours

Did some debugging. Got the timeout feature working. Also changed the amount the website sends motor cmds from every 10ms to every 100ms. That helped with the lag a lot. Added a thing on website to change that value.

#### 15:00 | 2 hours

Wrote code to let you control the tank like a car, also added switch to turn that on and off. Refactored the whole python file to use classes. Got a bit of help from AI to reduce video bandwidth. It now looks rlly bad, and feels the same on latency, but the bandwidth is down by A LOT.

### Sunday, November 2nd | 3 hours

#### 10:00 | 2 hours

Spent forever trying to get ppp (network over serial) working on the modem. The modem itself will get an IP from the cell towers, but once I start asking for a ppp address, I get ghosted. I had the same issue with this modem on my last project, and I was naive to think it would work better this time. The solution is to use usb, but I'm already using the one usb port for the camera, so I'll have to wire up a hub.

#### 15:00 | 1 hour

Tested the car on it's first long range test. It uhh worked. But the latency was annoying, a lot of the time it was usable, but with color off I coulden't tell the difference between the road and dirt, so I turned on color, that broke everything. I hope it works better once I'm back in Boston, but I don't want to get my hopes up too much. Another issue is not a bug, but once your on the road, it feels SUPER slow. It's fine in a house but once you are on the street its wayyy too slow. So I'm going to start designing a new chassis made out of aluminum extrutions, with a higher speed and more room for goodies.

New things for v2:

- Bigger chassis
- Switch to electon so we can use the hosts serial ports for radios and such
- Faster top speed

### Monday, November 3rd | .5 hours

#### 17:30 | 0.5 hours

Tested the tank in Boston (hopefully has faster cell). It worked, but has a lot to be wanted... It was night so I could bearly see what I was doing. [filz.cc/f/UVyD.mp4](https://filz.cc/f/UVyD.mp4) [filz.cc/f/diph.mp4](https://filz.cc/f/diph.mp4)
![Driving in Boston](/photos/driving_in_boston.jpg)

### Tuesday, November 4th | 1.5 hours

#### 17:00 | 1 hour

Started by checking btop (better htop) to see cpu usage while running the script. THe cpu is around 10% when running, so we don't need a faster pi. Then I took apart a hover board to get to the brushless motors, this is going to be the main motors for V2 until I feel I need better ones. ![Wayyyy too many screws](/photos/screws_from_hoverboard.jpg) ![Taken apart hoverboard](/photos/taken_apart_hoverboard.jpg)

#### 20:00 | 0.5 hours

Started thinking about how to design the robot and doing the cad. Right now I'm stuck on the suspension because I rally have to build around it. CAD is hard :/

### Wednesday, November 5th | 1.5 hours

#### 07:30 | 0.5 hours

Started reading about WebRTC and how to use it, seems helpful due too variable bitrate among other features. Just built out more in general. To use this libary I found, it looks like I need to switch to FastAPI so I started doing that. Later today I'm going to build the frame for the bigger chassis. It's going to be really simple to start, just a rectangle, but it will be much bigger and allow me to start getting the motors working.

#### 21:00 | 1 hour

Found this repo that looks good, it will let me use the motor contolers already in the hoverboard mobo. I might make the robot in to a hoverboard for now so I don't need to get more parts, depends on if the repo will do the balance, if not, I'll jsut use the motors and mobo. I'll look into a bit more in the morning and figure out my next steps for hardware. [Repo Link](https://github.com/RoboDurden/Hoverboard-Firmware-Hack-Gen2.x-GD32)

### Thursday, November 6th | 2.5 hours

#### 07:00 | 0.5 hours

Wired up this ESP8266 to flash the new firmware to the hoverboard boards. Also got headers ready for the boards. Now i just need to solder the headers and flash it, but the pins for flashing are a weird size so the headers don't want to solder.

#### 17:00 | 1 hour

Soldered headers to the hoverboard PCB's to flash. Now I'm trying to follow the **not very helpful** guide in the repo on how to set up the flasher and all that. I have about 20 programs open rn and bearly know what half of them do... ![ESP8266 I'm using to flash the hoverboard](/photos/esp_8266_flasher.jpg) ![Hoverboard PCB with nice headers I added](/photos/hoverboard_pcb_with_headers_and_wires.jpg)

#### 21:30 | 1 hour

Set up Keil and some other apps to try and program it. I'm making no progress though. I think I'm going to try and use a rpi pico instead of ESP8266 and start over tmrw.

### Friday, November 7th | 2 hours

#### 20:30 | 1 hour

Started by flashing (WHY FLASH SOO MANY THINGS TODAY :/ ) a rpi pico with picoprobe, a SWD flasher that runs on a pi pico. Then I spent a while figuring out what program I use to flash the new firmware to the hoverboard. After a while of it not working, I found out that I was trying to wipe the wrong type of chip. Once I started using the correct chip, I just had to use shorter wires and IT WIPED THE CHIP. :yayayayay: Now I'm going to try to flash the new firmware and see if it does anything... ![Hoverboard connected to picoprobe](/photos/hoverboard_board_with_pi_pico.jpg)

#### 22:00 | 1 hour

Got stuck with [this](https://github.com/pyocd/pyOCD/issues/1396) error, will try again in morning. I tried grounding the reset pin as it says to, but that doesn't do anythign about the error, it just pops up as soon as I let go (therefore starting the mcu). ![Pcb in question](/photos/hoverboard_pcb_held.jpg)

### Sunday, November 9th | 2 hours

#### 16:30 | 2 hours

Susfually compiled firmware from scratch, and tried to flash, no diffrence. Tried pulling boot0 high and low on boot. Tried external 36v power. Tried on other PCB that has not been messed with. Went back to ESP8266 with Keil and flashed with same error. STLink app does not work with ESP8266 or rpi pico.

Fet is `110n8f6` according to google is 80v 80a?

Next steps:

- Try STLink programmer
- Find other repos doing same thing
- Look into price of other motor contollers and or motors

### Thursday, November 13th | 1 hour

#### 20:45 | 1 hour

I GOT IT TO PROGRAM!!! Using the ST-Link flasher was the fix!! I have been stuck on this part for almost 2 weeks (of not everyday work) so this is good. To tired rn, but next time I'm home I'm going to test the motors with the boards. ![Programing working](/photos/PROGRAM_WORKING.jpg) ![ST-Link Versions](/photos/ST-Link_Version.jpg) ![Flasher](/photos/ST-Link_Flasher.jpg)

### Wendsday, November 19th | 1.5 hours

#### 20:00 | 1 hour

GOT THE THING FLASHING LIGHTS WHEN I SPIN MOTOR!!! This is mainly so I don't forget, but when programing, start with only 3v3 from programer, then after the programing disconnect 3v3 and use 36v mains (12v seems to work fine). Now I'm going to see if I can get it to spin the motor!

#### 21:00 | .5 hours

Can't get it to spin motors, when I give it power, the motors seems to stiffen though, so somethings happening. Next steps are to flash the pit detection firmware so I can make sure I'm using the right pins for the hall sensors or smt. I think thare should be 3 lights switching when I spin the wheel, not two. So tmrw I will wire an esp32 to see the output of the autodetect firmware! [Video!](https://filz.cc/f/YVN7.mp4)

### Thursday, November 20th | 3.25 hours

#### 07:30 | .5 hours

Made a cable to connect the ESP8266 for commands and debug info, but now when programing, I get this error: `STLink USB communication error`. No idea why because I have not changed anything. Tried diffrent cables with no sucess.

#### 16:45 | .25 hours

Got it programing again, here is the full process you have to do: first, connect all pins but make sure the 36v power is OFF. Power via programmer 3v3. Then in ST-Link, click connect, it should load some data. Then load your file and click download when it asks you to. Then disconnect the 3v3 from programmer, and turn on 36v power to test.

#### 17:00 | 1 hour

![ESP8266 Pinout](/photos/esp_8266_pinout.jpg)

| SWD   | Pico  | Pico Board | ESP    | ESP Board | Color  |
| ----- | ----- | ---------- | ------ | --------- | ------ |
| SWCLK | GPIO2 | 4          | GPIO14 | D5        | Blue   |
| SWDIO | GPIO3 | 5          | GPIO13 | D7        | Purple |
| VCC   | 3V3   | 3V3        | 3v3    | 3v3       | White  |
| GND   | GND   | GND        | GND    | GND       | Gray   |

**Keil installation folder:** `C:\Users\wev\AppData\Local\Keil_v5`

We have the `gd32f130c8`

Packs go here: `C:\Users\web\AppData\Local\cmsis-pack-manager\cmsis-pack-manager`

**Green = pink on original cable**

| Color  | Meaning | GPIO | Pin# |
| ------ | ------- | ---- | ---- |
| Green  | Ground  | GND  | GND  |
| Blue   | 5v      | 5v?  | 5v   |
| Orange | PA2?    | 14   | D5   |
| Yellow | PA3?    | 12   | D6   |

[This](http://www.hiletgo.com/ProductDetail/1906570.html) has some good info about how to set up the board.

So I got the firmware on the ESP32 so we can see the output from the pin autodetect firmware. I am seeing nothing but there are a lot of things to check. Rn it looks like it only draws current when holding the on button...

#### 18:00 | .5 hours

Compiled the firmware myself and in config selected the pins I'm using for output, now I get messages in the serial console. Still have to hold the button but tis not that bad.
Figured out that `#define LAYOUT_SUB 19	// Layout 19 means x.1.9`.
Anyways rn its still not spinning but I figured out how to get the autodetect firmware running and how to edit all the code. So hopefully it works tonight!

#### 21:00 | 1 hour

Can't tell if the dummy mode is actualy trying to spin the motor. Rn only 2/3 leds light up for the phases... Ideas for tmrw:

- Test with python UART
- Use STM Var viewer thing

### Sunday, November 23rd | 2.5 hours

#### 20:00 | 1.5 hours

Decided to try and use STM Studio to watch the vars like in the guide. After I got it installed, and then added some stuff to PATH, I got this error. I got it watching the vars, but nothing was happening. My next idea was try changing the hall sensor pins to ones I knew was wrong, this made no change, giving me the idea that its not compiling for the right board. I added a debug message to 2-1-9 and it never ran so I messed with the options a figured out how to select the correct one: `#define LAYOUT 9 // means 2.1.9`

#### 22:00 | 1 hour

When it uses the correct files with what I thought was correct hall pins, the leds dont light up at all, and I feel no resistance on the motor. I should see what the pins are on the file I was doing by mistake and use those.

Just tried the halls from the file I was wrongly using (2-1-2) and it did not work. This is good though, so it has to be something else in 2-1-2 but not halls so we can use new halls. Now I am using all settings from 2-1-2 BUT used proper led mappings are we can see all the halls. [Video](https://github.com/niiccoo2/RC-Tank/raw/refs/heads/main/photos/working_hall_with_led.mp4) Still don't know why its not trying to spin...

Switched the `Brushless Control DC (BLDC) defines` and it did nothing, so I think its just not trying to spin at all.

IT SPINSSSSS!!!!! All I did was switch out this bit from 2-1-9 and it started working!!!!!! [Video](https://github.com/niiccoo2/RC-Tank/raw/refs/heads/main/photos/IT_SPINS.mp4)

```
// GD32F130 USART0 TX/RX:	(PA9/PA10)AF1	, (PB6/PB7)AF0 , 	(PA2/PA3)AF1 , (PA14/PA15)AF1 GD32F130x4 only!
// GD32F130 USART1 GD32F130 TX/RX: (PA14/PA15)AF1 , (PA2,PA3)AF1	, (PA8/PB0)AlternateFunction4
#define USART1_TX		PA2
#define USART1_RX		PA3

#define VBATT	PA4		//maybe
#define CURRENT_DC	PA5		//maybe

#define SELF_HOLD	PB2		// rhody tested
#define BUTTON		PC14 	// rhody tested

#ifdef HAS_BUZZER
	// Buzzer defines
	#define BUZZER	PB9 // rhody tested
#endif
```

### Monday, November 24th | .33 hours

#### 07:40 | .33 hours

Figured out how to turn off the buzzer. It's really annoying. Next steps:

- Get UART control working
- Set up on other board
- Get UART bus working to control both boards with one ESP8266

### Wendsday, November 26th | 3 hours

#### 16:00 | 1.5 hours

Made some code to send the uart stuff from pi, still not working. Next steps:

- Flash and get known good code working on esp8266

#### 20:00 | 1.5 hours

Got it to kinda spin via uart. Rn it spins but at a really weird interval. Next steps are to go back to the rpi and see if I can get it to spin, then tune the code more. Then get it working via uart bus. Then start working on the frame (wood or metal) and figure out hte battery and steering I will use for the first test in NH this weekend.

### Thursday, November 27th | 4.5 hours

#### 11:40 | 1 hour

Did a good bit of debugging, so from the var viewer, it looks like every time it starts spinning it gets a speed set, then it times out so therefore the slow down. Now need to figure out why its timing out.

#### 14:00 | .5 hours

Still cant get python to work... This is the data of the semi working code... Also don't know why its timing out...
![Semi working data](/photos/semi_working_data_bytes.png)

#### 18:00 | 3 hours

Got it to follow cmds! I had to switch from 19200 to 4800 buad. Now for the time explanation: First spend a while understanding how the code worked. Code in question:

Old code:

```cpp
void RemoteCallback(void)
{
	uint8_t cRead = USART_REMOTE_BUFFER[0];
	//DEBUG_LedSet(SET,0)
	//DEBUG_LedSet((steerCounter%20) < 10,0)	//
	if (	(iReceivePos<0) && (cRead == '/'))	// Start character is captured, start record
	{
		iReceivePos++;
	}

	if (iReceivePos >= 0)		// data reading has begun
	{
		aReceiveBuffer[iReceivePos++] = cRead;
		if (iReceivePos == sizeof(SerialServer2Hover))
		{
			SerialServer2Hover* pData = (SerialServer2Hover*) aReceiveBuffer;
			//memcpy(aDebug,aReceiveBuffer,sizeof(SerialServer2Hover));
			//if (1)

			nicoRxCRC = pData->checksum;
			nicoCalcCRC = CalcCRC(aReceiveBuffer, sizeof(SerialServer2Hover) - 2);


			if (pData->checksum == CalcCRC(aReceiveBuffer, sizeof(SerialServer2Hover) - 2))	//  first bytes except crc
			{
				iTimeLastRx = millis();
				bRemoteTimeout = 0;
				speed = pData->iSpeed;
				steer = pData->iSteer;
				wState = pData->wStateMaster;
				wStateSlave = pData->wStateSlave;
				//if (speed > 300) speed = 300;	else if (speed < -300) speed = -300;		// for testing this function

				ResetTimeout();	// Reset the pwm timout to avoid stopping motors
				iReceivePos = -1;
			}
			else
				iReceivePos = -2;	// skip next start character in case there was another such char in message
		}
	}
}
```

New code:

```cpp
void RemoteCallback(void) {
    uint8_t cRead = USART_REMOTE_BUFFER[0]; // Read the incoming byte

    // Log raw data into nicoRawData for debugging purposes
    nicoRawData[nicoRawIndex] = cRead; // Save the raw byte
    nicoRawIndex = (nicoRawIndex + 1) % 128; // Move to the next index, wrap around if the buffer is full

    // If we are in idle state (waiting for start character) and receive the start character
    if ((iReceivePos < 0) && (cRead == '/')) {
        iReceivePos = 0; // Start recording data
        aReceiveBuffer[iReceivePos++] = cRead; // Save the start character
        return; // Wait for further data
    }

    // If data reading has begun
    if (iReceivePos >= 0) {
        aReceiveBuffer[iReceivePos++] = cRead; // Record the incoming byte to the buffer

        // If buffer is full, process the message
        if (iReceivePos == sizeof(SerialServer2Hover)) {
            SerialServer2Hover* pData = (SerialServer2Hover*)aReceiveBuffer;

            // Assign debug values for CRC
            nicoRxCRC = pData->checksum; // Store received CRC for debugging
            nicoCalcCRC = CalcCRC(aReceiveBuffer, sizeof(SerialServer2Hover) - 2); // Calculate local CRC for debugging

            // Check if CRC matches
            if (nicoRxCRC == nicoCalcCRC) {
                // Valid message
                iTimeLastRx = millis(); // Update timestamp of last valid message
                bRemoteTimeout = 0; // Clear timeout flag
                speed = pData->iSpeed; // Extract speed
                steer = pData->iSteer; // Extract steering
                wState = pData->wStateMaster; // Extract master state
                wStateSlave = pData->wStateSlave; // Extract slave state

                ResetTimeout(); // Reset PWM timeout to avoid stopping motors
                iReceivePos = -1; // Reset position to idle (ready for next message)
            } else {
                // CRC mismatch, invalid message
                // Set position to -2 (error state) and wait for the next valid start character
                iReceivePos = -2;
            }
        }
    }

    // Handle failed state (-2): Skip until the next start character
    if (iReceivePos == -2) {
        if (cRead == '/') {
            // Valid start character detected, reset and start recording new message
            iReceivePos = 0;
            aReceiveBuffer[iReceivePos++] = cRead;
        }
    }

    // Handle buffer overflow (unexpected condition)
    if (iReceivePos >= sizeof(aReceiveBuffer)) {
        iReceivePos = -1; // Reset to idle state to avoid overriding memory
    }
}
```

Make sure that both sides were calculating CRC (checksums) the same way, they were. Then added some global vars so I could see the values of CRCrx and CRCcalc. For some reason they are diffrent most of the time. Then spent a while looking at code to understand why they were not calculating the same.

Then hooked up my logic analyzer to look at the raw data. It was the same each time... (Thats good) ![Picture of data](/photos/data_from_logic.png) (This is not the final, or correct data). Also hooked up normal scope to make sure it looked clean and not noisy. It was fine.

At this point, I was almost about to restart with another set of code for the hoverboard. But then I decided to do one last thing and change the baud rate from 19200 to 4800 and it worked!!

Right now there are still a few issues with the wheel, other than needing to get it working from a pi (not a esp8266) and needing to use UART Bus:

- Seems to have a very conservative breaking / slow down. Like VERY slow, if you stop giving it cmds, it takes almost 10 secs to stop from speed 400.
- Seems to make a loud noise when running at high speeds, idk if this is because it is hitting my power limits (set on PS) or if its because its floating rn, and not on the ground, hopefully this fixes itself.

Things to do tmrw:

- Fix conservative breaking
- Make sure second wheel and contoller work alone
- UART Bus
- Frame
- Wire the new python code into the old stuff
- Might need to finish getting webRTC working, might just skip that though
- Set up modem with usb ub
- Figure out what >= 14v battery to use for it
- ^ Might need to make harness for two 2s batts

### Friday, November 28th | 6.5 hours

#### 08:00 | 1 hour

Seems to get stuck when going over speed 500... Using BLDC_BC instead of BLDC_SINE fixed it! Now going to test the other motor and contoller alone, then work on uart bus!

Tested the other PCB and motor and they are working the same as first!! Now going to get uart working from the pi.

#### 09:00 | .5 hours

Got UART working from pi, now working on UART bus. Got uart bus working. Now need to test it with two salves and start on the frame. ![Working UART Bus bytes](/photos/working_uart_bytes.png)

#### 10:00 | 2 hours

Did a bunch of wiring. Made a harness to go from 2 2s batts to 1 4s batt. Now working on a 4 way connnector with fuse so we can power everything. Then working on frame. ![Battery adapter](/photos/battery_adapter.jpg)

#### 12:30 | 1 hour

Took forever but made the wiring harness for the data stuff. Now testing both motors at once. Need to find out how to bypass on button... Just crashed my laptop bc I hooked up power wrone :/ Found pins to bridge so it turns on on power. Got both motors working at once.

#### 15:00 | 2 hours

Made this really nice frame. It looks a bit weird but it works. Then put everything onto the tank and tested that the motors still spin, they do! Tmrw morning I will turn the motor code into a class then integrate. ![Top view of new frame](/photos/chassis_top.jpg) ![Side view of new frame](/photos/chassis_side.jpg)

### Satuday, November 29th | 2.5 hours

#### 09:00 | 1 hour

Now working on rewriting the motor control into a class that I can then use in the api thing. Was not too hard, just copied a bunch of code from the test file into the old class. One thing you have to remember is that slave 1 is left and slave 0 is right.

#### 11:00 | 1 hour

When I made the wiring harness for the esc data comms, I made it on perf board, but it was really bad. Thats why sometimes it woul just not listen to the cmds I was sending. So I decided to just solder the wires directly because perf board was a bit too much for the task. After I soldered the wires directly I realized that I still messed up the wiring. This is because from the factory, they switch the data tx and rx in the cable so that the two boards can talk to each other, so I took apart hte connector so I could switch them back. Now the esc wiring should be better.

#### 12:00 | .5 hours

Finally I got to test it, this test was a bit flawed though, because I found out that the usb hub I was using was really old, so it was unable to stream camera data over it. For camera I had someone follow on google meet so I could see what I was doing. Other than me getting car sick from the shaky camera, the test was pretty good, the latency was not amazing, but it was semi drivable. So hopefully once I get a new usb hub, the built in camera will be better! (Video will be from second test)

### Sunday, November 30th | 2.33 hours

#### 10:00 | 2 hours

Spent a while trying to set up WebRTC. It should have much better latency but I was unable to get it working. I just wanted to drive the car so I reverted to using MJPEG.

#### 14:00 | .33 hours

DROVE THE CAR. There are a lot of things to add BUT ITS USABLE!!! Things that happend (so I remember):

- Latency is not horible, but WebRTC is still a good thing to add
- You tend to sverve a lot because of the (even if small) latency...
- Need to figure out how to read bettery voltage. This could be from ESC's or make my own thing.
- I think I broke the webcam because there are PCB trace looking things in my view. It's still driveable but should fix it.

[Video](https://hc-cdn.hel1.your-objectstorage.com/s/v3/c245bbe98e534a92a19db2d41ba9c841da88784e_2025-11-30_13-42-12.mp4)

This is the first part of this project that I am submitting to [Moonshot](https://moonshot.hackclub.com). As of here I am at **65.46** hours!

## CAD designs

### Riser

#### V3

- Holes to mount to chasis
- Holes for RPI
- Holes for battery zipties

#### V4

- Screw holes to mount to chasis
- Screw holes for RPI
- Holes for battery zipties
- Screw holes for cover

#### V5

- Screw holes to mount to chasis
- Screw holes for RPI
- Holes for battery zipties
- Screw holes for cover
- MAKE ALL M3 HOLES SMALLER

### Cover

#### V1

- Indents for zipties

#### V2

- Indents for zipties
- Hole for switches
- Indent for camera mount
- Hole for cell SMA
- Hole for LCD cables

#### V3

- Indents for zipties
- Hole for switches + holes for switch screws
- Hole for cell SMA
- Hole for GPS SMA
- Hole for LCD cables
- Mounting holes to mount to riser

#### V4

- Indents for zipties
- Hole for switches + holes for switch screws
- Hole for cell SMA
- Hole for GPS SMA
- Hole for LCD cables
- Mounting holes to mount to riser
- MAKE ALL M3 HOLES SMALLER
