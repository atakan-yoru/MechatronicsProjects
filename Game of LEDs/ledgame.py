import machine
from machine import Pin, Timer
import utime
#defining variables
led_built = Pin(25, Pin.OUT)
po0, po1, po2, po3, po4, po5, po6, po7 = Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT), Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)
button_left = Pin(15, Pin.IN)
button_right = Pin(14, Pin.IN)
time=150  # period of shifting lights(acting period) 
state = 0 # state indicator of FSM 
r_bin = 0 # binary representation of player right's LED
l_bin = 0 # binary representation of player left's LED
merge = 0 # merged binary representation of LEDs
r_count = 0 # push count for player right
l_count = 0 # push count for player left
r_prev = 0 # prev state of right button
l_prev = 0 # prev state of left button
r_fault = False # double firing check for player right
l_fault = False # double firing check for player left
collision = False # collision check
r_reached=False # checks player right's LED reached end
l_reached=False # checks player left's LED reached end
lst = [0] + [2 ** i for i in range(8)] # 0 and powers of 2 in list form
r_score = 0 # score of player right
l_score = 0 # score of player left
#end of defining variables
def reset(): # this function resets variables to their initial values defined above (except r_score and l_score)
    global state,r_bin,l_bin,r_score,l_score,r_count,l_count,merge,r_prev,l_prev,collision,r_fault,l_fault,r_reached,l_reached
    state = 0
    r_bin = 0
    l_bin = 0
    merge = 0
    r_count = 0
    l_count = 0
    r_prev = 0
    l_prev = 0
    collision = False
    r_fault = False
    l_fault = False
    r_reached=False
    l_reached=False
    turn_off()

def formatter(byte):  # This functions turns an intiger to byte and returns formated string version
    s = bin(byte)[2:]
    while len(s) < 8:
        s = "0" + s
    return s

def turn_off():  # This function is used to turn off all leds
    for index in range(8):
        exec("po{}.value(0)".format(index))
    return 0

def bin_to_led(count):  # This function is used to represent binary formated string with the LEDs on the circuit
    turn_off()
    count = formatter(count)
    if len(count) <= 8:
        lst = [7, 6, 5, 4, 3, 2, 1, 0]
        for index, each in enumerate(count):
            if int(each):
                exec("po{}.value(1)".format(lst[index]))
    else:
        turn_off()
        return 0

def check_winner(): # this function checks winning conditions, defines and prints winner
    global r_score,l_score
    if r_score==5:
        print("Right Wins!!!!!!!!!!!")
        reset()
        r_score=0
        l_score=0
    elif l_score==5:
        print("Left Wins!!!!!!!!!!!")
        reset()
        r_score=0
        l_score=0
    
def decide(a): #this function decides state and decides what to do in particular states
    global state,r_score,l_score,r_reached,l_reached
    if state == 0:
        if r_count == 1:
            state = 1
        elif l_count == 1:
            state = 3
    elif state == 1:
        if l_count == 1:
            state = 2
        elif r_count == 2:
            l_score+=1
            utime.sleep_ms(time)
            reset()
            print("left scored - right double fired") 
            print("Left Score : {} Right score: {} ".format(l_score,r_score))
            check_winner()
        reach_end_checker()
        if r_reached==True:
            r_score+=1
            utime.sleep_ms(time)
            reset()
            print("right scored - right reached end")
            print("Left Score : {} Right score: {} ".format(l_score,r_score))
            check_winner()
    elif state == 3:
        if r_count == 1:
            state = 2
        elif l_count == 2:
            r_score+=1
            utime.sleep_ms(time)
            reset()
            print("right scored - left double fired")         
            print("Left Score : {} Right score: {} ".format(l_score,r_score))
            check_winner()
        reach_end_checker()
        if l_reached==True:
            l_score+=1
            utime.sleep_ms(time)
            reset()
            print("left scored - left reached end")
            print("Left Score : {} Right score: {} ".format(l_score,r_score))
            check_winner()
    elif state == 2:
        collision_checker()
        double_fault()
        if r_fault == True:
            l_score += 1
            print("left scored right double fired")
            print("Left Score : {} Right score: {} ".format(l_score,r_score))
            utime.sleep_ms(time)
            check_winner()
            reset()
        elif l_fault == True:
            r_score += 1
            print("right scored - left double fired")
            print("Left Score : {} Right score: {} ".format(l_score,r_score))
            utime.sleep_ms(time)
            check_winner()
            reset()
        elif collision == True:
            utime.sleep_ms(time)
            reset()
            print("draw")
            print("Left Score : {} Right score: {} ".format(l_score,r_score))

def collision_checker(): # checks whether the LEDs coincide 
    global lst, l_bin, r_bin, collision #lst contains powers of 2 from 0 to 128
    if r_bin - l_bin in lst: # checks wheteher difference between 2 LED's binary representations is power of 2 (lst)
        collision = True

def double_fault(): # checks double firing
    global r_fault, l_fault, r_count, l_count
    if r_count == 2:
        r_fault = True
    if l_count == 2:
        l_fault = True
    
def reach_end_checker(): # checks whether LED reaches other end
    global r_reached, l_reached
    if r_bin==1:
        r_reached=True
    if l_bin==128:
        l_reached=True

def move_leds(a): # this function does bitwise shift to LED's binary representation
    global r_bin, l_bin, merge
    merge = r_bin | l_bin
    if r_bin > 1:
        r_bin = r_bin >> 1
    if l_bin < 128:
        l_bin = l_bin << 1
    bin_to_led(merge)

def button_checker(a): # checks whether buttons are pushed and which one is pushed
                       # in this part, debounce is not used since it is handled using hardware solution( Schmitt-Trigger and capacitor) 
    global r_count, l_count, r_prev, l_prev, r_bin, l_bin
    if r_prev == 0 and button_right.value() == 1:
        r_prev = 1
    elif r_prev == 1 and button_right.value() == 0:
        r_count += 1
        if r_count == 1:
            r_bin = 128
        r_prev = 0
    if l_prev == 0 and button_left.value() == 1:
        l_prev = 1
    elif l_prev == 1 and button_left.value() == 0:
        l_count += 1
        if l_count == 1:
            l_bin = 1
        l_prev = 0

def run(): # This function is the main part of the code where timers of state machine are defined
    global r_score,l_score
    reset()
    turn_off()
    move_timer = Timer()
    button_timer = Timer()
    decide_timer = Timer()
    move_timer.init(period=time, mode=Timer.PERIODIC, callback=move_leds)
    button_timer.init(period=50, mode=Timer.PERIODIC, callback=button_checker)
    decide_timer.init(period=50, mode=Timer.PERIODIC, callback=decide)

run()