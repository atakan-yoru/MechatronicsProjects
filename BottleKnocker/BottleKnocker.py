import machine
import machine
from machine import Pin, Timer, PWM
import utime

count = 0
instant_sense = 0
sensor_trig = False

pin_distance = Pin(16, Pin.IN)

engine_pin1 = Pin(8, Pin.OUT)
engine_pin2 = Pin(9, Pin.OUT)
pwm_engine=PWM(Pin(10))
pwm_engine.freq(50)

knock_pin1 = Pin(11, Pin.OUT)
knock_pin2 = Pin(12, Pin.OUT)

state = 1

abolo = 0

search = None
prev_bottle = -1
skip = None

def checker(inp):
    indexes = []
    """Checks Start and Stop Byte"""
    if inp[0] == "A" and inp[-1] == "Z":
        for i, j in enumerate(inp):
            """Takes the indexes of alphabetic items in the message"""
            if j.isalpha():
                indexes.append(i)
        indexes.pop(-1)
        indexes.pop(0)
        """Checks for empty byte"""
        for each in indexes:
            if not inp[each + 1].isdigit():
                print("Message has empty byte.")
                return 2
        else:
            return 1
    else:
        print("Start or Stop byte is missing.")
        return 0


def parser(inp):
    if checker(inp) == 1:
        indexes = []
        for i, j in enumerate(inp):
            if j.isalpha():
                indexes.append(i)
        messages = []
        for index, each in enumerate(indexes):
            try:
                messages.append(int(inp[each + 1:indexes[index + 1]]))
            except ValueError:
                continue
            except IndexError:
                continue
    elif checker(inp) == 0:
        print("Error in message")
        return 0

    return messages


def knock(pin2, pin1, ms=80):
    # ms=80
    pin1.value(0)
    pin2.value(0)
    starttime = utime.ticks_ms()
    pin2.value(1)
    while utime.ticks_diff(utime.ticks_ms(), starttime) < ms:
        pass
    pin2.value(0)
    pin1.value(1)
    starttime = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), starttime) < 1.6 * ms:
        pass
    pin1.value(0)


def positive_spin(pin3, pin4, duty=15000):
    pwm_engine.duty_u16(duty)
    pin4.value(0)
    pin3.value(1)


def negative_spin(pin3, pin4, duty=14000):
    pwm_engine.duty_u16(duty)
    pin4.value(1)
    pin3.value(0)


def sense(pin_distance):
    global instant_sense
    instant_sense = int(pin_distance.value() == False)
    return int(pin_distance.value() == False)


def stop(pin3, pin4):
    pin4.value(0)
    pin3.value(0)
    pwm_engine.duty_u16(0)


"""
while True:

    while sense(pin_distance) == False:
        negative_spin(engine_pin1, engine_pin2)
    stop(engine_pin1, engine_pin2)
    knock(knock_pin1, knock_pin2, 80)
"""
def counter_for_count(pin_distance):
    global count
    global sensor_trig
    if sense(pin_distance) and sensor_trig == False:
        count += 1
        sensor_trig = True
    elif not sense(pin_distance):
        sensor_trig = False

def counter(t):
    global pin_distance
    global count, skip
    global sensor_trig
    if sense(pin_distance) and sensor_trig == False and state != 3:
        count += 1
        skip -= 1
        sensor_trig = True
    elif not sense(pin_distance):
        sensor_trig = False
# and utime.ticks_diff(utime.ticks_ms(),abolo) > 200


def decider(t):
    global state, prev_bottle, skip, search, prev_state
    if state == 1:
        if instant_sense == 1 and skip == 0:
            state = 3
    elif state == 2:
        if instant_sense == 1 and skip == 0:
            state = 3

    elif state == 3:
        try:                                                                  #A4B2C3D1Z
            prev_bottle = ord_list.index(search_list[0])
            a=ord_list.index(search_list[1])
            ord_list.remove(search_list[0])
            search_list.remove(search_list[0])
            """
            print("Search={}".format(search_list))
            print("Ordered={}".format(ord_list))
            print("Prev=",str(prev_bottle))
            """
            search = search_list[0]
            index_diff = a - prev_bottle + 1
            if index_diff>0:
                skip = abs(index_diff) -1
            else:
                skip = abs(index_diff) +1
            """
            print("Skip=",str(skip))
            print("diff=",str(index_diff))
            """
            if index_diff < 0 and instant_sense == 0:
                state = 2  # negative
            elif index_diff > 0 and instant_sense == 0:
                state = 1  # positive
            elif index_diff==0 and instant_sense == 0:
                state=2
        except IndexError:
            print("all bottles knocked")
            state = -1

def act(t):
    
    if state == 1:
        positive_spin(engine_pin1,engine_pin2,14000)
    elif state == 2:
        negative_spin(engine_pin1,engine_pin2,13000)
    elif state ==3:
        stop(engine_pin1,engine_pin2)
        knock(knock_pin1,knock_pin2)
        abolo = utime.ticks_ms()
        utime.sleep_ms(200)
        
def runner():
    sense_timer = Timer()
    act_timer = Timer()
    decide_timer = Timer()

    act_timer.init(period=80, mode=Timer.PERIODIC, callback=act)
    sense_timer.init(period=40, mode=Timer.PERIODIC, callback=counter)
    decide_timer.init(period=80, mode=Timer.PERIODIC, callback=decider)


inp = input("Given an input: ")

search_list = parser(inp)
if len(search_list)==0:
        
    start_time = utime.ticks_ms()
    flag=True
    while flag :
        while sense(pin_distance) == False:
            positive_spin(engine_pin1, engine_pin2)
            if utime.ticks_diff(utime.ticks_ms(),start_time) > 5200:
                stop(engine_pin1,engine_pin2)
                flag=False
                break
        utime.sleep_ms(20)
        counter_for_count(pin_distance)
    print(count)
else:
        
    ord_list = search_list.copy()
    ord_list.sort()
    search = search_list[0]
    index_diff = ord_list.index(search) - prev_bottle
    skip = abs(index_diff)
    runner()
