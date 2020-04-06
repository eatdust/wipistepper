import wiringpi as wp

#how the driver is connected to the board: "name":pinnumber
#if not specified at initialization, the first three pins are
defWiring = {'enable':0,'clock':1,'direction':2}

#driver's default states at initialization: "name": value
#if not specified at initialization, let's put 0V everywhere
defStates = {'enable':wp.LOW,'clock':wp.LOW,'direction':wp.LOW}

#driver's excitation mode, an integer which is the inverse of the
#excitation step. if not specified at initialization, full step per
#default
defStepMode = 1

#software generated pulse width (in microsecs)
defPulseWidth = 60

#hardware clock frequency for PWM
ClockFreqMHz = 19.2

#hardware generated pulse width on the PWM channel (in microsecs)
defClockWidth = 8

#default range for PWM (from 2 to a lot)
defRange = 4096

#set priority
defPriority = 99

class driver(object):
    
    def __init__(self,name='',wiring=defWiring,states=defStates,
                 stepmode=defStepMode,pulsewidth=defPulseWidth,
                 clockwidth=defClockWidth,range=defRange):

        wp.wiringPiSetup()
        success = wp.piHiPri(defPriority)
        if success != 0:
            print('init driver: setting priority failed',success)

        self.numbering = 'wiringPi'
        
        self.set_drivername(name)

        self.set_initial_states(states)
        self.set_stepmode(stepmode)
        self.set_pulsewidth(pulsewidth)
        
        self.set_wiring(wiring)
        self.set_states(states)
        for wire,pin in wiring.items():
            state = states[wire]
            self.set_pinmode_output(pin)
            self.set_pinstate(pin,state)

#set the variables only because we are not in PWM mode
        self.set_clockwidth(clockwidth)
        self.set_range(range)

    def get_numbering(self):
        return self.numbering
    
            
    def set_drivername(self,name):
        self.drivername = name

    def get_drivername(self):
        return self.drivername



    def set_wiring(self,wiring):
        self.wiring = wiring
    
    def get_wiring(self):
        return self.wiring

    
    def set_initial_states(self,states):
        self.inistates = states.copy()

    def get_initial_states(self):
        return self.inistates

    
    def set_pinmode_output(self,pin):
        wp.pinMode(pin,wp.OUTPUT)

#in balance mode        
    def set_pinmode_pwm(self,pin):
        wp.pwmSetMode(wp.PWM_MODE_BAL)
        wp.pinMode(pin,wp.PWM_OUTPUT)
        
        
    def set_pinstate(self,pin=0,state=wp.LOW):
        wp.digitalWrite(pin,state)

    def get_pinstate(self,pin):
        return wp.digitalRead(pin)

#should be called in PWM mode
    def set_pindata(self,pin=1,data=0):
        wp.pwmWrite(pin,data)


                
    def set_states(self,states):
        self.states = states
    
    def get_states(self):
        return self.states

                                 
    def set_stepmode(self,invstep):
        self.stepmode = invstep

    def get_stepmode(self):
        return self.stepmode

                                 
    def set_pulsewidth(self,us):
        self.pulsewidth = us

    def get_pulsewidth(self):
        return self.pulsewidth

#the hardware clock is actually updated only if a pin is set to PWM
#mode, take care to call them after having switched to pwm mode
    def set_range(self,nrange=defRange):
        wp.pwmSetRange(nrange)
        self.range = nrange

    def get_range(self):
        return self.range
    
    def set_clockwidth(self,us):
        clockDivider = round(us*ClockFreqMHz)
        wp.pwmSetClock(clockDivider)
        self.clockwidth = us
        self.clockdivider = clockDivider
        self.clockshift = clockDivider/ClockFredMHz - us

    def set_clockdivider(self,divider):
        wp.pwmSetClock(divider)
        self.clockdivider = divider
        self.clockwidth = divider/ClockFreqMHz
        self.clockshift = 0
        
    def get_clockwidth(self):
        return self.clockwidth

    def get_clockdivider(self):
        return self.clockdivider

    def get_clockshift(self):
        return self.clockshift

#another way to set the range, for data=1 (min non-vanishing duty
#cycle), this is the longest possible clocktime between two ticks
    def set_clockmaxtime(self,us):
        nrange = round(us/self.clockwidth)
        self.set_range(nrange)
    
    def get_clockmaxtime(self):
        return self.clockwidth*self.range
    
    
    def reset(self):
        for wire,pin in self.wiring.items():
            self.set_pinmode_output(pin)
            self.set_pinstate(pin,self.inistates[wire])



#convenience wrapper for test

    def set_wiremode_output(self,wirename):
        self.set_pinmode_output(self.wiring[wirename])
        
    def set_wiremode_pwm(self,wirename):
        self.set_pinmode_pwm(self.wiring[wirename])
        
    def set_wirestate(self,wirename,state=wp.LOW):
        self.set_pinstate(self.wiring[wirename],state)

    def get_wirestate(self,wirename):
        return self.get_pinstate(self.wiring[wirename])

    def set_wiredata(self,wirename,data):
        self.set_pindata(self.wiring[wirename],data)



