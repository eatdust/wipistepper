#!/usr/bin/python
import wipidrive as wd
import wipimotor as wm
import time as time

connections={'en':0,'clk':1,'cw':2}
defaultvalues={'en':1,'clk':0,'cw':0}

motor = wm.motor(drivername='TB65603A',motorname='QSH6018-65-28-210',
                 wiring=connections, states=defaultvalues,
                 stepmode=8, pulsewidth=10,
                 clockwidth=8, range=4096,
                 stepangle=1.8)

print(motor.get_drivername())
print(motor.get_motorname())

print('wiring is:  =  ',motor.get_wiring())
print('inistates   =  ',motor.get_initial_states())
print('stepmode    =  ',motor.get_stepmode())
print('angle/tick  =  ',motor.get_tickangle())
print('tick/rot    =  ',motor.get_ticknumber(360))
print('pulse width =  ',motor.get_pulsewidth())
print('clock width =  ',motor.get_clockwidth())
print('clock maxrpm=  ',motor.get_clockmaxrpm())
print('clock minrpm=  ',motor.get_clockminrpm())
print()
time.sleep(2)



motor.switch('en')
#motor.switch('cw')
#motor.switch('clk')

rpm = 360
rpmps = 180
motor.softrun_while('clk',msrun=5000,rpm=rpm,rpmps=rpmps)
motor.pwmrun_while('clk',msrun=5000,rpm=rpm,rpmps=rpmps)

rpm=720
rpmps=180
nframe = 10
motor.softrun_to('clk',degrun=(2*nframe-1)*180.0,degramp=90.0,rpmps=rpmps)

    
motor.reset()    


