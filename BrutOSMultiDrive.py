
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
yBut = 306
bBut = 304
killBut = 317

min = 0
max = 65535

driveState = "joyThrotJoySteer"
newDriveState = ""

#Preset variables 
RJoyThrottle = 0
LJoyThrottle = 0
throtVal = 0.5
speedModify = 1

#I dont think I need this any more, yet here it is...
gamepad =0

#GPIO Output Pin Numbers
programLED = 18
bluetoothLED = 16
hornLED = 13


#BOARD SETUP
kit = MotorKit(i2c=board.I2C())
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(programLED, GPIO.OUT)
GPIO.setup(bluetoothLED,GPIO.OUT)
GPIO.setup(hornLED, GPIO.OUT)

#WELCOME MESSAGES
#Only called when the program first launches
#It drops into checkController
def welcome():
    GPIO.output(programLED, GPIO.HIGH)
    print("Welcome to BrutOS V1.1 ")
    print()
    print("This software makes use of single JOYSTICK CONTROL")
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
            GPIO.output(hornLED, GPIO.HIGH)
            time.sleep(0.05)
            GPIO.output(hornLED, GPIO.LOW)
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
    print(driveState)

#DRIVE THE MOTORS ONLY IF THE BLUETOOH CONTROLLER IS CONNECTED
#Try to move, but if the joystick is not connected, catch the error and move to reconnect the bluetooth device
def motorDrive():
    global driveState
    global newDriveState
    while True:
        try:
            gamepad = InputDevice('/dev/input/event2')
            for event in gamepad.read_loop():
                if event.type == ecodes.EV_ABS:
                    try:
                        print("Found ABS code")
                        if driveState == "joyThrotJoySteer":
                            print("Switching to single joystick control")
                            normalizedX = 0.0
                            normalizedY = 0.0
                            xAxis = gamepad.absinfo(ecodes.ABS_X).value
                            print('Captured xAxis value')
                            yAxis = gamepad.absinfo(ecodes.ABS_Y).value
                            print('Captured yAxis value')
                            normalizedX = 2.0 * (xAxis - min) / (max - min) - 1.0
                            normalizedY = -(2.0 * (yAxis - min) / (max - min) - 1.0)
                            print('Normalized values')

                            print("X: " + str(normalizedX))
                            print("Y: " + str(normalizedY))
                            print()
                            rMotor = ((normalizedY) - (normalizedX))
                            lMotor = ((normalizedY) + (normalizedX))
                            if rMotor > 1.0:
                                rMotor = 1.0
                            if lMotor > 1.0:
                                lMotor = 1.0
                            if rMotor < -1.0:
                                rMotor = -1.0
                            if lMotor < -1.0:
                                lMotor = -1.0
                            print('RightMotor: ' + str(rMotor))
                            print('LeftMotor: ' + str(lMotor))

                            kit.motor2.throttle = rMotor
                            kit.motor1.throttle = lMotor
                        elif driveState == "trigThrotJoySteer":
                            print("switching drive modes to trigger throttle and joystick steering")
                            try:
                                if event.code == rTrig:
                                    print("right trigger")
                                elif event.code == lTrig:
                                    print("left trigger")
                                elif event.code == rBump:
                                    print("Right bumper")
                                elif event.code == lBump:
                                    print("Left bumper")
                            except:
                                print("error driving in this mode")
                        elif driveState == "tankControl":
                            absEvent = categorize(event)
                            if ecodes.bytype[absEvent.event.type][absEvent.event.code] == "ABS_Y":
                                RJoyThrottle = ((absEvent.event.value - 32768)/32768)*-1
                                print("Left Y: ", absEvent.event.value, "       R_Throttle: ", RJoyThrottle)
                                kit.motor1.throttle = RJoyThrottle
                            elif ecodes.bytype[absEvent.event.type][absEvent.event.code] == "ABS_RY":
                                LJoyThrottle = ((absEvent.event.value - 32768)/32768)*-1
                                print("Right Y: ", absEvent.event.value, "       L_Throttle: ", LJoyThrottle)
                                kit.motor2.throttle = LJoyThrottle
                        else:
                            print("error assigning drive mode, defaulting to tank controls")
                    except:
                        print("Error getting ABS code")
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
                    if event.code == yBut:
                        try:
                            print("Y button pressed")
                            print("Honking Horn")
                            GPIO.output(hornLED, GPIO.HIGH)
                            time.sleep(0.1)
                        except:
                            print("Error Honking Horn")
                        GPIO.output(hornLED, GPIO.LOW)
                    if event.code == bBut:
                        try:
                            if driveState == "joyThrotJoySteer":
                                newDriveState = "trigThrotJoySteer"
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)

                            elif driveState =="trigThrotJoySteer":
                                newDriveState = "tankControl"
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)
                            elif driveState == "tankControl":
                                newDriveState = "joyThrotJoySteer"
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)
                            print("switching drive modes from "+driveState+ " to "+newDriveState)
                            driveState = newDriveState
                        except:
                            print("Error determining new drive state, default drive mode remains")        
                    if event.code == killBut:
                        print("KILLING MOTORS!")
                        try:
                            kit.motor1.throttle = 0
                            kit.motor2.throttle = 0
                            print("MOTORS STOPPED!")
                            print("Pausing for 5 seconds")
                            counter = 0
                            while counter < 3:
                                GPIO.output(hornLED, GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(hornLED, GPIO.LOW)
                                time.sleep(0.1)
                                counter = counter + 1
                            time.sleep(5)
                            GPIO.output(hornLED, GPIO.HIGH)
                            time.sleep(0.1)
                            GPIO.output(hornLED, GPIO.LOW)
                            time.sleep(0.1)
                        except:
                            print("ERROR! Unable to stop motors!")

        except:
            print("Joystick Disconnected, please reconnect")
            GPIO.output(bluetoothLED, GPIO.LOW)
            checkController()


#MAIN LOOP
welcome()
checkController()
robotReadyMessage()
motorDrive()
