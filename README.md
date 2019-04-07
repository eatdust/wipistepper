# Wipistepper: high level controls for serious steppers

---

### Summary

Wipistepper provides two python modules, **wipidrive** and
**wipimotor** encoding high level functions built on top of **wiringpi**
to control stepper motors and their drivers by using a Raspberry Pi.

Please ensure that you have a working installation of
[wiringpi](http://wiringpi.com/) as well as its python wrappers
[WiringPi-Python](https://github.com/WiringPi/WiringPi-Python).

---

### Driver initialization

High currents stepper motors are usually connected to a **driving**
electronic board, which itself can be controled from the Raspberry
Pi.

Wiring between the driver board and the RPI are up to you, but should
be specified during the initialization of a *driver* object within the
**wipidrive** class. The default initialization assumes 3 cables, one
for the power state (enable), one for triggering pulses
(clock), and one for setting the direction (direction).

```python
defWiring = {'enable':0,'clock':1,'direction':2}
```

defines a dictionary, *defWiring*, that says that the power cable is
connected to the pin 0 of the RPI, the clock to the pin 1 and
direction to pin 2. This numbering is the ['wiringPi'
numbering](http://wiringpi.com/pins), but this can be changed (see
wipidrive.py).

NB: If you want to be able to reach high clock frequencies using the
RPI pulse width modulator, you must connect the clock on pin 1 (BCM_GPIO 18)

```python
defStates = {'enable':wp.LOW,'clock':wp.LOW,'direction':wp.LOW}
```

defines a dictionary, *defStates*, encoding the initial voltages sent
to the 'enable', 'clock' and 'direction' gates of the driving board.

Various other hardware settings can be set during the initialization
of a driver object:

```python
def __init__(self,name='',wiring=defWiring,states=defStates,
                 stepmode=defStepMode,pulsewidth=defPulseWidth,
		                  clockwidth=defClockWidth,range=defRange):
```				  

Notice that *pulsewidth* refers to software generated clock signals
while *clockwidth* and *range* are for the Pulse Width Modulator
(PWM). The *stepmode* in which the driver board is running should be
properly set, it obviously encodes by how much a connected stepper
motor will be running for a given number of pulses.

---

### Motor initialization

The *motor* class is derived from the *driver* class and all the above
settings can be provided during the initialization of a motor object.

```python

import wipidrive as wd

def __init__(self,drivername='', motorname='',
                 wiring=wd.defWiring, states=wd.defStates,
                 stepmode=wd.defStepMode,
		 pulsewidth=wd.defPulseWidth,
	         clockwidth=wd.defClockWidth,
		 range=wd.defRange,
		 stepangle=defStepAngle):
```

In addition, a *motor* object comes with its own properties. Don't
forget to check the value of the step angle, the angle by which the stepper
tilts when receiving  one pulse in stepmode=1. The default is:

```python
defStepAngle = 1.8 #in degrees
```

---

### Working example

Let's analyze the example provided, "steppertest.py"

```python
#!/usr/bin/python
import wipidrive as wd
import wipimotor as wm
import time as time

connections={'en':0,'clk':1,'cw':2}
defaultvalues={'en':1,'clk':0,'cw':0}

motor = wm.motor(drivername='TB65603A',motorname='QSH6018-65-28-210',
                 wiring=connections, states=defaultvalues,
		 stepmode=8, pulsewidth=10,
		 clockwidth=8,
                 range=4096,
		 stepangle=1.8)

```

We specify that we have connected the "en", "clk" and "cw" driver
gates to the RPI pins 0, 1 and 2, respectively. Their name are
yours, here "en" for "enable", "clk" for "clock", "cw" for "clockwise"
rotation. Voltage states for these wires are initially set to 1,
0, 0 (my board wiring switches the motor off for en=1).

The driver board is in stepmode=8, the motor has a step angle of 1.8
degrees and we want to generate software pulses of 10 milliseconds
width (these should be set to what the driving board is capable of).
For the PWM, a pulse width of 8 milliseconds is set over a range of
4096.


```python

motor.switch('en')

rpm = 360
rpmps = 180
motor.softrun_while('clk',msrun=5000,rpm=rpm,rpmps=rpmps)
motor.pwmrun_while('clk',msrun=5000,rpm=rpm,rpmps=rpmps)

```

The first instruction energizes the motor (flip state on gate 'en'). Then
we want to reach an angular speed of *rpm=360* rotations per minute with an
acceleration of *rpmps=180* rpm per second. Therefore, cruising speed
will be reached after 2 seconds.

The method *motor.softrun_while()* generates clock pulses sent to the
driver, through the 'clk' gate, to accelerate the motor to *rpm*
angular speed with a *rpmps* acceleration. The motor will stay at
maximum speed during *msrun=5000* milliseconds. Then it decelerates
and stop. Pulses are software generated, they are not very accurate
and some can be skipped depending on what the operating system is
prioritizing. You won't be able to reach high speed with software
generated pulses.

The method *motor.pwmrun_while()* does exactly the same using the
PWM of the RPI, clock frequency can go up to a few MHz and you can
easily reach more than 1000 rpm, provided your stepper keeps it
torque at high speed. To understand the RPI's PWM, have a look to the [wiringpi
doc](http://wiringpi.com/reference/raspberry-pi-specifics/).


```python

rpmps=180
nframe = 10
motor.softrun_to('clk',degrun=(2*nframe-1)*180.0,degramp=90.0,rpmps=rpmps)

motor.reset()

```

The method *motor.softun_to()* allows to move the motor by a given
angle (degrun) with a given acceleration (rpmps) that applies only during
some ramp angle (degramp).

---

### Real world example

I have been developping these modules to control an old 16mm film
projector that has been transformed into a HDR film scanner. That
thing requires some more than 3A stepper motor for getting enough
torque. All the public codes I was able to find were software
controlling toy steppers that did not need to move at 1440 rpm.

The stepper is used to move the film frame per frame, precisely, to
allow for the digital camera to take and dump pictures. It is also
used at very high speeds, up to 24 frames/second (1440 rpm), to
actually allow for dumping the sound track and projecting the movie.

Here a picture of the stepper motor, the driver board and the RPI:

---
![stepper](/docs/stepdriverpi.jpg?raw=true)
---

It takes some time and attention to localize the correct GPIO pins,
but nothing more is required. A zoom on the wiring used (caution: your
driving board may require a completely different one)

---
![wiring](/docs/wiring.jpg?raw=true)
---

For the film scanner code, see [fbfscan](https://github.com/eatdust/fbfscan).
