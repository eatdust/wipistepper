import wiringpi as wp
import wipidrive as wd
import math as m
import sys as sys

#Motor driven by a driver inherits all driver methods. However, a
#motor has its own properties, such as a stepangle per pulse
#(in full step mode), etc... to be specified

defStepAngle = 1.8

#some constants used everywhere
mnPerUs = 60*1e6
mnsInUs2 = 1e-13/6
degPerRpmPerUs = 360/mnPerUs
usInfty = 1000000
usNull = 1

class motor(wd.driver):

    def __init__(self,drivername='', motorname='',
                 wiring=wd.defWiring, states=wd.defStates,
                 stepmode=wd.defStepMode, pulsewidth=wd.defPulseWidth,
                 clockwidth=wd.defClockWidth, range=wd.defRange,
                 stepangle=defStepAngle):

        wd.driver.__init__(self,name=drivername,wiring=wiring,states=states,
                           stepmode=stepmode,pulsewidth=pulsewidth,
                           clockwidth=clockwidth,range=range)
        self.set_motorname(motorname)
        self.set_stepangle(stepangle)
        self.set_tickangle()
        self.set_tickrotfrac()

        
    def set_motorname(self,name):
        self.motorname = name
        
    def get_motorname(self):
        return self.motorname

    
#motor step angle (in full step mode)
    def set_stepangle(self,angle):
        self.stepangle = angle
        
    def get_stepangle(self):
        return self.stepangle
    
#motor pulse and clock angle (in any step mode)
    def set_tickangle(self):
        self.tickangle = self.stepangle/self.stepmode

#returns the angle the motor rotates under one pulse or clock impulsion
    def get_tickangle(self):
        return self.tickangle
    
#motor rotation per pulse or clock
    def set_tickrotfrac(self):
        self.tickrotfrac = self.tickangle/360

#return the fraction of turn made by one pulse        
    def get_tickrotfrac(self):
        return self.tickrotfrac

#how much ticks are needed to rotate by this amount of degrees    
    def get_ticknumber(self,degrees):
        ntick = round(degrees/self.tickangle)
        rest = degrees - ntick*self.tickangle
        if rest != 0.0:
            print('get_ticknumber: remaining angle =',rest)
        return ntick
    
#get the mean time between ticks corresponding to a given rpm    
    def get_ticktime(self,rpm):
        if rpm <=0:
            return float('inf')
        return self.tickangle/(rpm*degPerRpmPerUs)
    
#get the rpm corresponding to a given tick time
    def get_rpm(self,us):
        return self.tickangle/(degPerRpmPerUs*us)
    

    
#switch state of a given wire    
    def switch(self,wirename=''):
        pin = self.wiring[wirename]
        antistate = anti_state(self.states[wirename])
        self.states[wirename] = antistate
        self.set_pinstate(pin,antistate)
    
#create and send a pulse of width given by self.pulsewidth in the
#middle of us microseconds
    def pulse(self,wirename='',us=1e6):
        quietime = round((us-self.pulsewidth)/2)
        wp.delayMicroseconds(quietime)
        self.set_pinstate(self.wiring[wirename],anti_state(self.states[wirename]))
        wp.delayMicroseconds(self.pulsewidth)
        self.set_pinstate(self.wiring[wirename],self.states[wirename])
        wp.delayMicroseconds(quietime)
               
    
    
#software generated pulsetimes with an initial acceleration
#of "rpmps" rotation per minute per seconds, for ramping up to the
#given pulserpm (pulsetime associated with rpm).
    def get_pulsetime_accel(self,rpus2,pulsetime,pulserpm):

#example of acceleration profile
#        invmu2 = 1.0/pulsetime/pulsetime
#        invrpm2 = 1.1/pulserpm/pulserpm
#        friction = abs(invrpm2-invmu2)/(invrpm2 + invmu2)
#        accel = rpus2  * friction
        
#2*accel is anow + aprev for leap frog, let's spare instruction
        invmu2 = 1.0/pulsetime/pulsetime + (2*rpus2)/self.tickrotfrac
        
        if invmu2 > 0:
            return pow(invmu2,-0.5)
        else:
            return usInfty

    
    
#software driven run of the motor during "msrun" milliseconds at a
#given rpm. In doing so, ramp to, and from the nominal rpm with an
#initial acceleration of rpmps. Notice that the ramping time depends
#on the acceleration profile for non-constant acceleration
    def softrun_while(self,wirename='',msrun=1000,rpm=1,rpmps=0.5):
        
        rpus2 = rpmps * mnsInUs2
        pulserun = self.get_ticktime(rpm)
        pulseramp = usInfty

        while pulseramp > pulserun:
            pulseramp = self.get_pulsetime_accel(rpus2,pulseramp,pulserun)
            self.pulse(wirename,pulseramp)
            
        inirun = wp.millis()        
        
        while wp.millis()-inirun < msrun:
            self.pulse(wirename,pulserun)

        pulseramp = pulserun
        
        while pulseramp < usInfty:
            self.pulse(wirename,pulseramp)
            pulseramp = self.get_pulsetime_accel(-rpus2,pulseramp,usInfty)

    

#software driven run of the motor at a given rpm to sweep the angle
#degrun. In doing so, ramp to and from over the angle degramp. The
#total swept angle is degrun + 2*degramp
    def softrun_to(self,wirename='',degrun=360.0,degramp=90.0,rpmps=10):
        rpus2 = rpmps * mnsInUs2
        nrun = self.get_ticknumber(degrun)
        nramp = self.get_ticknumber(degramp)
        
        pulseramp = usInfty
        for istep in range(0,nramp):
            pulseramp = self.get_pulsetime_accel(rpus2,pulseramp,usNull)
            self.pulse(wirename,pulseramp)

            
        pulserun = pulseramp
        for istep in range(0,nrun):
            self.pulse(wirename,pulserun)

            
        pulseramp = pulserun
        for istep in range(0,nramp):
            self.pulse(wirename,pulseramp)
            pulseramp = self.get_pulsetime_accel(-rpus2,pulseramp,usInfty)





#get the value of data/range corresponding to a given rpm
    def get_dataoverrange(self,rpm):
        return self.clockwidth/self.get_ticktime(rpm)

    def get_clockminrpm(self):
        return self.get_rpm(self.get_clockmaxtime())

#assuming data does not exceed 50% duty
    def get_clockmaxrpm(self):
        return self.get_rpm(2*self.clockwidth)
            
#hardware PWM driven run of the motor during "msrun" milliseconds at a
#given rpm. In doing so, ramp to, and from the nominal rpm with an
#acceleration of rpmps.
    def pwmrun_while(self,wirename='',msrun=1000,rpm=1,rpmps=0.5):

        if rpm < self.get_clockminrpm():
            print('pwmrun_while: rpm < rpmmin= ',self.get_clockminrpm())
            return
        if rpm > self.get_clockmaxrpm():
            print('pwmrun_while: rpm < rpmmin= ',self.get_clockmaxrpm())
            return
                  
        print('switching to PWM mode...   ')
        self.set_pinmode_pwm(self.wiring[wirename])
        self.set_clockwidth(self.clockwidth)
        self.set_range(self.range)

        print('ramping up...              ')                  
        data = self.pwmramp(wirename,rpm,rpmps)

        print ('running at data =',data)
        wp.delay(msrun)
            
        print('ramping down...')
        data = self.pwmramp(wirename,rpm,-rpmps)
                  
        print('switching to output mode...')
        print('                           ')
        self.set_pinmode_output(self.wiring[wirename])



#start an hardware PWM driven run of the motor forever. In doing so,
#ramp to the nominal rpm with an acceleration of rpmps.
    def pwmrun_start(self,wirename='',rpm=1,rpmps=0.5):

        if rpm < self.get_clockminrpm():
            print('pwmrun_while: rpm < rpmmin= ',self.get_clockminrpm())
            return
        if rpm > self.get_clockmaxrpm():
            print('pwmrun_while: rpm < rpmmin= ',self.get_clockmaxrpm())
            return
                  
        print('switching to PWM mode...   ')
        self.set_pinmode_pwm(self.wiring[wirename])
        self.set_clockwidth(self.clockwidth)
        self.set_range(self.range)

        print('ramping up...              ')                  
        data = self.pwmramp(wirename,rpm,rpmps)

        print ('running at data =',data,'      ')
        return rpm


#stop an hardware PWM driven run. In doing so,
#ramp from the nominal rpm to zero with an acceleration of rpmps.
    def pwmrun_stop(self,wirename='',rpm=1,rpmps=-0.5):

        if rpmps > 0:
            print('pwnrun_stop: rpmps > 0!')
            rpmps = -rpmps
            
        print('ramping down...            ')
        data = self.pwmramp(wirename,rpm,rpmps)
                  
        print('switching to output mode...')
        print('                           ')
        self.set_pinmode_output(self.wiring[wirename])
        

        
        
    def pwmramp(self,wirename,rpm,rpmps):
        rpmpms = rpmps * 1e-3
        if rpmpms >= 0:
            data = self.pwm_accelerate_to(wirename,rpm,rpmpms)
        else:
            data = self.pwm_deccelerate_from(wirename,rpm,rpmpms)
            
        return data
        

    def pwm_accelerate_to(self,wirename,rpm,rpmpms):
        if rpmpms <= 0:
            print('pwm_accelerate_to: rpmps <= 0!')
            return
        
        rpmramp = 0        
        
        data = -1
        dataprev = -1
        friction = 1
        while rpmramp < rpm:
#friction could be set to one or any other functions
            friction = abs(1.1*rpm-rpmramp)/(1.1*rpm+1 + rpmramp)
            rpmramp = min(rpmramp + rpmpms*friction,rpm)
            data = round(self.get_dataoverrange(rpmramp)*self.get_range())
            if data != dataprev:
                print('data =',data)
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                self.set_pindata(self.wiring[wirename],data)
                dataprev = data
            wp.delay(1)

        return data


    def pwm_deccelerate_from(self,wirename,rpm,rpmpms):
        if rpmpms >= 0:
            print('pwm_deccelerate_from: rpmps >= 0!')
        
        rpmramp = rpm

        data = 1
        dataprev = 1
        friction = 1
        while data > 0:
#friction could be set to one or any other functions
#            friction = abs(1.1*rpm-rpmramp)/(1.1*rpm+1 + rpmramp)
            rpmramp = max(rpmramp + friction*rpmpms,0)
            data = round(self.get_dataoverrange(rpmramp)*self.get_range())
            if data != dataprev:
                print('data =',data)
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                self.set_pindata(self.wiring[wirename],data)
                dataprev = data
            wp.delay(1)

        return data
   

            

def anti_state(state):
    if state == wp.LOW:
        anti_state = wp.HIGH
    else:
        anti_state = wp.LOW

    return anti_state
