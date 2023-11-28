# Include the library files
import I2C_LCD_driver
import RPi.GPIO as GPIO
from time import sleep

COL_1 = 5
COL_2 = 6
COL_3 = 13
COL_4 = 19

ROW_1 = 12
ROW_2 = 16
ROW_3 = 20
ROW_4 = 21

BUZZER_PIN = 17

RELAY_PIN = 27
relayState = True

lcd = I2C_LCD_driver.lcd()

# Starting text
lcd.lcd_display_string("System loading", 1, 1)
for a in range(0, 16):
    lcd.lcd_display_string(".", 2, a)
    sleep(0.1)
lcd.lcd_clear()

keypadPressed = -1

secretCode = "1111"
userInput = ""

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)


GPIO.setup(COL_1, GPIO.OUT)
GPIO.setup(COL_2, GPIO.OUT)
GPIO.setup(COL_3, GPIO.OUT)
GPIO.setup(COL_4, GPIO.OUT)


GPIO.setup(ROW_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ROW_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ROW_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ROW_4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def keypad_callback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

GPIO.add_event_detect(ROW_1, GPIO.RISING, callback=keypad_callback)
GPIO.add_event_detect(ROW_2, GPIO.RISING, callback=keypad_callback)
GPIO.add_event_detect(ROW_3, GPIO.RISING, callback=keypad_callback)
GPIO.add_event_detect(ROW_4, GPIO.RISING, callback=keypad_callback)

def set_all_rows(state):
    GPIO.output(COL_1, state)
    GPIO.output(COL_2, state)
    GPIO.output(COL_3, state)
    GPIO.output(COL_4, state)

# Check or clear PIN
def handle_commands():
    global relayState
    global userInput
    pressed = False
    GPIO.output(COL_1, GPIO.HIGH)
    
    # Clear PIN 
    if GPIO.input(ROW_1) == 1:
        print("Input reset!")
        lcd.lcd_clear()
        lcd.lcd_display_string("Clear", 1, 5)
        sleep(1)
        pressed = True
    GPIO.output(COL_1, GPIO.HIGH)

    if not pressed and GPIO.input(ROW_2) == 1:
        if userInput == secretCode:
            print("Code correct!")
            lcd.lcd_clear()
            lcd.lcd_display_string("Successful", 1, 3)
            
            if relayState:
                GPIO.output(RELAY_PIN, GPIO.LOW)
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                sleep(0.3)
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                sleep(1)
                relayState = False
                
            elif not relayState:
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                sleep(0.3)
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                sleep(1)
                relayState = True
            
        else:
            print("Incorrect code!")
            lcd.lcd_clear()
            lcd.lcd_display_string("Wrong PIN!", 1, 3)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            sleep(0.3)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            sleep(0.3)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(BUZZER_PIN, GPIO.LOW) 
        pressed = True
    GPIO.output(COL_1, GPIO.LOW)
    if pressed:
        userInput = ""
    return pressed

def read(column, characters):
    global userInput
    GPIO.output(column, GPIO.HIGH)
    if GPIO.input(ROW_1) == 1:
        userInput = userInput + characters[0]
        print(userInput)
        lcd.lcd_display_string(str(userInput), 2, 0)
    if GPIO.input(ROW_2) == 1:
        userInput = userInput + characters[1]
        print(userInput)
        lcd.lcd_display_string(str(userInput), 2, 0)
    if GPIO.input(ROW_3) == 1:
        userInput = userInput + characters[2]
        print(userInput)
        lcd.lcd_display_string(str(userInput), 2, 0)
    if GPIO.input(ROW_4) == 1:
        userInput = userInput + characters[3]
        print(userInput)
        lcd.lcd_display_string(str(userInput), 2, 0)
    GPIO.output(column, GPIO.LOW)

try:
    while True:       
        lcd.lcd_display_string("Enter your PIN:", 1, 0)
        if keypadPressed != -1:
            set_all_rows(GPIO.HIGH)
            if GPIO.input(keypadPressed) == 0:
                keypadPressed = -1
            else:
                sleep(0.1)
        else:
            if not handle_commands():
                read(COL_1, ["D", "C", "B", "A"])
                read(COL_2, ["#", "9", "6", "3"])
                read(COL_3, ["0", "8", "5", "2"])
                read(COL_4, ["*", "7", "4", "1"])
                sleep(0.1)
            else:
                sleep(0.1)
except KeyboardInterrupt:
    print("Stopped!")
