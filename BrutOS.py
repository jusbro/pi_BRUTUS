
#IMPORTS
from evdev import InputDevice, categorize, ecodes
import time
import board
from adafruit_motorkit import MotorKit
import RPi.GPIO as GPIO

#CONSTANTS AND VARIABLES
#Controller Mapping: These numbers represent the button presses from the particual Joystick I use
throtVal = 0.5
rTrig = 311
lTrig = 310
rBump = 309
lBump = 308
minus = 312
plus = 313
xBut = 307

#Preset variables 
RJoyThrottle = 0
LJoyThrottle = 0
throtVal = 0.5
speedModify = 1

#I dont think I need this any more, yet here it is...
gamepad =0

#GPIO Output Pin Numbers
programLED = 18
bluetoothLED = 19
speedLED = 13


#BOARD SETUP
kit = MotorKit(i2c=board.I2C())
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(programLED, GPIO.OUT)
GPIO.setup(bluetoothLED,GPIO.OUT)
GPIO.setup(speedLED, GPIO.OUT)

#WELCOME MESSAGES
#Only called when the program first launches
#It drops into checkController
def welcome():
    GPIO.output(programLED, GPIO.HIGH)
    print("Welcome to BrutOS V1.1 ")
    print()
    print("This software makes use of JOYSTICK CONTROL")
    print()
    print("Establishing Bluetooth Controller Connection")
    print()

#CHECK FOR BLUETOOTH CONNECTED DEVICES
#Will hold the program here unless it detects a joystick is present
#The program will come back here, and hold here, if the joystick drops the execution of this program
def checkController():
    contTrue = False
    while contTrue == False:
        try:
            gamepad = InputDevice('/dev/input/event2')
            print("Controller Sucessfully Paired")
            GPIO.output(bluetoothLED, GPIO.HIGH)
            contTrue = True
            #I dont know if I still need to return gamepad...
            return gamepad
        except:
            #Drop here is no controller is found, and stay here until one is found
            print("No controller connected")
            GPIO.output(bluetoothLED, GPIO.LOW)
            time.sleep(1)

 #NOTIFY USER THAT ROBOT IS READY TO RUMBLE           
def robotReadyMessage():
    print("Initializing Drive System")
    print()
    print("Brutus is Ready for Terror!")
    print()

#DRIVE THE MOTORS ONLY IF THE BLUETOOH CONTROLLER IS CONNECTED
#Try to move, but if the joystick is not connected, catch the error and move to reconnect the bluetooth device
def motorDrive():
    while True:
        try:
            gamepad = InputDevice('/dev/input/event2')
            for event in gamepad.read_loop():
                if event.type == ecodes.EV_ABS:
                    absEvent = categorize(event)
                    if ecodes.bytype[absEvent.event.type][absEvent.event.code] == "ABS_Y":
                        RJoyThrottle = ((absEvent.event.value - 32768)/32768)*-1
                        print("Left Y: ", absEvent.event.value, "       R_Throttle: ", RJoyThrottle)
                        kit.motor1.throttle = RJoyThrottle
                    elif ecodes.bytype[absEvent.event.type][absEvent.event.code] == "ABS_RY":
                        LJoyThrottle = ((absEvent.event.value - 32768)/32768)*-1
                        print("Right Y: ", absEvent.event.value, "       L_Throttle: ", LJoyThrottle)
                        kit.motor2.throttle = LJoyThrottle
                elif event.value == 1:
                    if event.code == xBut:
                        try:
                            print("X Button Pressed")
                            print("Toggling Speed of motors")
                            if speedModify == 1:
                                speedModify = .05
                            else:
                                speedModify = 1
                            print("Current Speed Modifier: ", speedModify)
                        except:
                            print("Invalid speed change")
        except:
            print("Joystick Disconnected, please reconnect")
            GPIO.output(bluetoothLED, GPIO.LOW)
            checkController()


#MAIN LOOP
welcome()
checkController()
robotReadyMessage()
motorDrive()
