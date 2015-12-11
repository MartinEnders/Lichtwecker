#!/usr/bin/python3

import time
import pigpio 

LED_PIN = 24
SSR_PIN = 23
TESTING = True

 
# #connect to pigpiod daemon
pi = pigpio.pi()

# setup pin as an output
pi.set_mode(LED_PIN, pigpio.OUTPUT)

# pi set frequency
pi.set_PWM_frequency(LED_PIN, 1200)


if(TESTING):
    dimm_dauer = 8 #sekunden
    nachleuchten = 1 #sekunden
    pwm_start = 1000
    pwm_ende  = 2550
else:
    pwm_start = 1200
    pwm_ende  = 2550
    dimm_dauer = 1800 #sekunden
    nachleuchten = 1800 #sekunden


def start_dimming():
    try:
        pi.write(SSR_PIN,1)
        print("start")
        time.sleep(0.2)
        for i in range(pwm_start,pwm_ende):
            pi.set_PWM_dutycycle(LED_PIN,i/10)
            time.sleep(dimm_dauer / (pwm_ende - pwm_start))

        time.sleep(nachleuchten)
    finally:
        print("disable ssr")
        pi.write(SSR_PIN,0)
        time.sleep(0.5)
        print("disable pwm")
        pi.set_PWM_dutycycle(LED_PIN,0)
        pi.stop()

def light_on():
    pi.write(SSR_PIN,1)
    pi.set_PWM_dutycycle(LED_PIN,255)

def light_off():
    pi.set_PWM_dutycycle(LED_PIN,0)
    pi.write(SSR_PIN,0)


start_dimming()


exit()
        
