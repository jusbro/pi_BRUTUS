from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event2')

print(gamepad)

for event in gamepad.read_loop():
    if event.type == ecodes.EV_KEY:
        print(event)
    elif event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        print(ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value)
