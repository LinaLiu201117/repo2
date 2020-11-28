# Add your Python code here. E.g.
from microbit import *
import neopixel

_SEG = bytearray(b'\x3F\x06\x5B\x4F\x66\x6D\x7D\x07\x7F\x6F\
\x77\x7C\x39\x5E\x79\x71\x3D\x76\x06\x1E\x76\x38\x55\x54\x3F\
\x73\x67\x50\x6D\x78\x3E\x1C\x2A\x76\x6E\x5B\x00\x40\x63')

# define
RGB_LED_NUM = 20
RGB_COLOR_NUM = 8
RGB_COLOR = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 255),
]

# RGB
rgbLedUpdateTime = 100
rgbLedTimeCnt = 0
rgbLedCurIndex = 0
rgbLedColorIndex = 1

# LIGHT
LIGHT_VALUE_MAX = 10
lightCurValue = 0
lightLastValue = 0
lightTimeCnt = 0
lightValuebuf = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
lightValueIndex = 0

# MUSIC
musicCurPlaySta = 0
musicExpectPlaySta = 0

# DISPLAY
curPicIndex = 0
displayTimeCnt = 0
displayUpdateTime = 100

# CFG
lightThreshold = 100
np = neopixel.NeoPixel(pin2, RGB_LED_NUM)

# turn on led
def rgbLedCtrlOn(ledIndex, colorIndex):
    global nb
    for i in range(0, RGB_LED_NUM):
        if i == ledIndex:
            # on
            np[i] = RGB_COLOR[colorIndex]
        else:
            # off
            np[i] = RGB_COLOR[0]
    # show
    np.show()
    return

# rgb time modify
def rgbLedTimeSet(value):
    # var declare
    global rgbLedUpdateTime
    # cpy
    rgbLedUpdateTime = value
    return


# rgb led task
def rgbLedTask():
    # var declare
    global rgbLedTimeCnt
    global rgbLedCurIndex
    global rgbLedColorIndex

    # time cal
    rgbLedTimeCnt += 1
    if rgbLedTimeCnt < rgbLedUpdateTime:
        return
    # restart cal
    rgbLedTimeCnt = 0

    # rgb update
    rgbLedCtrlOn(rgbLedCurIndex, rgbLedColorIndex)

    # switch to next led
    rgbLedCurIndex += 1
    if RGB_LED_NUM <= rgbLedCurIndex:
        rgbLedCurIndex = 0
        # switch to next color
        rgbLedColorIndex += 1
        if RGB_COLOR_NUM <= rgbLedColorIndex:
            # start from one
            rgbLedColorIndex = 1
    return

# light task
def lightTask():
    # var declare
    global lightTimeCnt
    global lightCurValue
    global lightLastValue
    global lightValuebuf
    global lightValueIndex
    global displayUpdateTime

    # time 1s
    lightTimeCnt += 1
    if lightTimeCnt < 50:
        return
    lightTimeCnt = 0

    # lightValuebuf[lightValueIndex] = pin1.read_analog()
    lightCurValue = pin1.read_analog()
    print("\r\n ", lightCurValue)
    # lightValuebuf.sort()
    # lightValueSum = 0
    # for i in range(1, LIGHT_VALUE_MAX-2):
    #     lightValueSum = lightValueSum + lightValuebuf[i]
    # lightCurValue = lightValueSum/(LIGHT_VALUE_MAX-2)

    # lightValueIndex += 1
    # if lightValueIndex >= LIGHT_VALUE_MAX:
    #     lightValueIndex = 0

    if lightCurValue != lightLastValue:
        if abs(lightCurValue - lightLastValue) < 10:
            return
        # light value update
        lightLastValue = lightCurValue
        # update displayTime
        displayUpdateTime = lightLastValue//20
        # print for debug
        # print("\r\n", lightLastValue)
        # change rgb time
        if 800 > lightLastValue:
            rgbLedTimeSet(5)
        else:
            rgbLedTimeSet(60)
    return

# display task
def displayTask():
    # var declare
    global displayTimeCnt
    global curPicIndex
    global displayUpdateTime

    # time 1s
    displayTimeCnt += 1
    if displayTimeCnt < displayUpdateTime:
        return
    displayTimeCnt = 0

    if curPicIndex == 0:
        display.show(Image.HEART)
        curPicIndex = 1
    else:
        display.show(Image.HEART_SMALL)
        curPicIndex = 0

# TM1637
def tm1637Init():
    tm1637_data_cmd()
    tm1637_dsp_ctrl()

def tm1637_start():
    cnt = 0
    # C->1
    pin14.write_digital(1)
    # D->1
    pin0.write_digital(1)
    # DELAY 1us
    cnt = cnt + 1
    # D->0
    pin0.write_digital(0)

def tm1637_stop():
    cnt = 0
    # C->0
    pin14.write_digital(0)
    # DELAY
    cnt = cnt + 1
    # D->0
    pin0.write_digital(0)
    # DELAY
    cnt = cnt + 1
    # C->1
    pin14.write_digital(1)
    # DELAY
    cnt = cnt + 1
    # D->1
    pin0.write_digital(1)

def tm1637_ask():
    cnt = 0
    # C->0
    pin14.write_digital(0)
    cnt = cnt + 1
    # C->1
    pin14.write_digital(1)
    cnt = cnt + 1
    # C->0
    pin14.write_digital(0)

def tm1637_data_cmd():
    tm1637_start()
    tm1637_write_byte(0x40)
    tm1637_ask()
    tm1637_stop()

def tm1637_dsp_ctrl():
    tm1637_start()
    tm1637_write_byte(0x88 | 0x07)
    tm1637_ask()
    tm1637_stop()

def tm1637_write_byte(b):
    cnt = 0
    for i in range(8):
        # CLK
        pin14.write_digital(0)
        # DAT
        pin0.write_digital((b >> i) & 1)
        # DELAY
        cnt = cnt + 1
        # CLK
        pin14.write_digital(1)
        # DELAY
        cnt = cnt + 1

def tm1637_write(segments, pos=0):
    if not 0 <= pos <= 3:
        raise ValueError("Position out of range")
    tm1637_data_cmd()
    tm1637_start()
    tm1637_write_byte(0xC0 | pos)
    tm1637_ask()
    for seg in segments:
        tm1637_write_byte(0xFF)
        tm1637_ask()
    tm1637_stop()
    tm1637_dsp_ctrl()

def tm1637_encode_string(string):
    segments = bytearray(len(string))
    for i in range(len(string)):
        segments[i] = tm1637_encode_char(string[i])
    return segments

def tm1637_encode_char(char):
    o = ord(char)
    if o == 32:
        return _SEG[36]  # space
    if o == 42:
        return _SEG[38]  # star/degrees
    if o == 45:
        return _SEG[37]  # dash
    if o >= 65 and o <= 90:
        return _SEG[o-55]  # uppercase A-Z
    if o >= 97 and o <= 122:
        return _SEG[o-87]  # lowercase a-z
    if o >= 48 and o <= 57:
        return _SEG[o-48]  # 0-9
    raise ValueError("Character out of range:\
    {:d} '{:s}'".format(o, chr(o)))
'''
def tm1637Number(num):
    num = max(-999, min(num, 9999))
    string = '{0: >4d}'.format(num)
    tm1637_write(tm1637_encode_string(string))
'''

while True:
    # var
    # power voice
    # music.play(music.JUMP_UP)

    # display init
    display.show(Image.HAPPY)

    # tm1637
    # tm1637Init()
    # tm1637Number(100)

    while True:
        # rgb led task
        rgbLedTask()

        # light task
        lightTask()

        # display task
        displayTask()

        # sleep
        sleep(10)
