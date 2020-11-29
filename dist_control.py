#!/usr/bin/env python3
#-- coding: utf-8 --
# Copyright (c) 2005-2020 BelSD - Jean-Pierre Waldorf
#
# Cat food dispenser toy
#
import os
import sys
from os.path import getmtime
from time import sleep
import RPi.GPIO as GPIO #Importe la bibliothèque pour contrôler les GPIOs

WATCHED_FILE_TIME = getmtime(__file__)

loop = True
nbStepsPerRev = 'Stop'

GPIO.setmode(GPIO.BCM) #Définit le mode de numérotation (BMC)
GPIO.setwarnings(False) #On désactive les messages d'alerte

LED_R = 4 #Définit le numéro du port GPIO qui alimente la led Rouge
LED_G = 17 #Définit le numéro du port GPIO qui alimente la led Vert
BUTTON = 27 #Définit le numéro du port GPIO du Bouton
Step_up = 5
Step_down = 6
Halt = 13

#Active le contrôle du GPIO
GPIO.setup(LED_R, GPIO.OUT)
GPIO.setup(LED_G, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Step_up, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Step_down, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Halt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(LED_R, GPIO.HIGH) #On l'allume
    
# Définition des pins GPIO 18,22,24,26 GPIO24,GPIO25,GPIO8,GPIO7
StepPins = [24,25,8,7]

for pin in StepPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)
# temps de vitesse
WaitTime = 0.001

# Définition pour des demi-séquences
StepCount = 8
Seq = [[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]

def steps(nb):
    StepCounter = 0
    if nb<0: sign=-1
    else: sign=1
    nb=sign*nb*2
    for i in range(nb):
        for pin in range(4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += sign
        # si nombre positif alors sens des aiguilles d'une montre
        if (StepCounter==StepCount):
            StepCounter = 0
        # si nombre négatif alors sens contraire des aiguilles d'une montre
        if (StepCounter<0):
            StepCounter = StepCount-1
        # Attente entre les mouvementss
        sleep(WaitTime)

def button_callback(channel):
    global nbStepsPerRev
    nbStepsPerRev=512 # 2048 = 1 tour -> 1/4 de tour = 512

def Step_up_callback(channel):
    global nbStepsPerRev
    nbStepsPerRev = 32 

def Step_down_callback(channel):
    global nbStepsPerRev
    nbStepsPerRev = -32 

def Halt_callback(channel):
    global loop
    loop = False

GPIO.add_event_detect(BUTTON,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(Step_up,GPIO.RISING,callback=Step_up_callback)
GPIO.add_event_detect(Step_down,GPIO.RISING,callback=Step_down_callback)
GPIO.add_event_detect(Halt,GPIO.RISING,callback=Halt_callback)


# Start main loop
if __name__ == '__main__' :
    try:
        while loop:
            if getmtime(__file__) != WATCHED_FILE_TIME:
                print ('Restart...')
                for pin in StepPins:
                    GPIO.output(pin, False)
                GPIO.output(LED_R, GPIO.LOW) #On éteind
                GPIO.output(LED_G, GPIO.LOW) #On éteind la Led vert
                GPIO.cleanup()
                os.execv(sys.executable, ['python3'] + sys.argv)
            if nbStepsPerRev!='Stop':
                GPIO.output(LED_G, GPIO.HIGH) #On allume la led vert
                steps(int(nbStepsPerRev))
                nbStepsPerRev = 'Stop'
                GPIO.output(LED_G, GPIO.LOW) #On éteind la Led vert
            sleep(0.5)
    except KeyboardInterrupt:
        sleep(1)

    print("\nStop")
    for pin in StepPins:
        GPIO.output(pin, False)
    GPIO.output(LED_R, GPIO.LOW) #On éteind
    GPIO.output(LED_G, GPIO.LOW) #On éteind la Led vert
    GPIO.cleanup()
    sys.exit()
    