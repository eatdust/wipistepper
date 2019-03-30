# Wipistepper: high level controls for serious steppers

---

### Summary

Wipistepper provides two python modules, **wipidrive** and
**wipimotor** encoding high level functions built on top of **wiringpi**
to control stepper motors and their drivers by using a Raspberry Pi.

Please ensure that you have a working installation of
[wiringpi](http://wiringpi.com/) as well as its python wrappers [WiringPi-Python](https://github.com/WiringPi/WiringPi-Python)

---

### Driver initialization

High currents stepper motors are usually connected to a *driving*
electronic board, which itself can be controled from the Raspberry
Pi.

Wiring between the driver board and the RPI are up to you, but should
be specified during the initialization of a *driver* object within the
**wipidrive** class. The default initialization assumes 3 cables, one
for the driver power state (enable), one for triggering pulses
(clock), and one for setting the direction (direction).

```python
defWiring = {'enable':0,'clock':1,'direction':2}
```

defines a dictionary, *defWiring*, that says that the power cable is
connected to the pin 0 of the RPI, the clock to the pin 1 and
direction to pin 2. This numbering is the ('wiringPi'
numbering)[http://wiringpi.com/pins], but this can be changed (see
wipidrive.py).

-
NB: If you want to be able to reach high clock frequencies using the
    RPI pulse width modulator, you must connect the clock on pin 1 (BCM_GPIO 18)
-

```python
defStates = {'enable':wp.LOW,'clock':wp.LOW,'direction':wp.LOW}
```

defines a dictionary, *defStates*, encoding the initial voltages sent
to the 'enable', 'clock' and 'direction' wires.

Various other hardware settings can be changed during the
initialization of a driver object:

```python
def __init__(self,name='',wiring=defWiring,states=defStates,
                 stepmode=defStepMode,pulsewidth=defPulseWidth,
		                  clockwidth=defClockWidth,range=defRange):
```				  

Notice that *pulsewidth* refers to software generated clock signals
and *clockwidth* and *range* are for the Pulse Width Modulator (PWM).


### Motor initialization
