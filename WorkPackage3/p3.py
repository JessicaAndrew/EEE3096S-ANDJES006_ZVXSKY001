# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
guess_num = 0
value = 0
current_guess = 0

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    global value
    global guess_num
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        guess_num = 0
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    t = 0
    for t in range(3):
        if len(raw_data)-1 <= t:
            print(t, " - NULL took NULL guesses")
        else:
            print(t, " - ", raw_data[t+1][0] + raw_data[t+1][1] + raw_data[t+1][2], "took", raw_data[t+1][3], "guesses")
    menu()
    pass


# Setup Pins
def setup():
    global PWM_LED
    global PWM_buzzer
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    # Setup PWM channels
    PWM_LED = GPIO.PWM(LED_accuracy,1000)
    PWM_LED.start(0) 
    PWM_buzzer = GPIO.PWM(buzzer,1) #set frequency to 1Hz
    PWM_buzzer.start(0)
    PWM_buzzer.ChangeDutyCycle(0)
    # Setup debouncing and callbacks
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=400)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=400)
    eeprom.clear(2048)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = 0
    score_count = eeprom.read_block(0,1)[0] 
    # Get the scores
    scores = []
    g = 1
    for g in range(score_count+1):
    	scores.append(eeprom.read_block(g,4))
    # convert the codes back to ascii
    for i in range(len(scores)):
        if scores[i][3] == 0:
            scores[i][3] = 100
        for j in range(3):
            scores[i][j] = chr(scores[i][j])
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    global guess_num
    arr_user = []
    scores_current = []
    # fetch scores
    score_count_current = 0
    score_count_current, scores_current = fetch_scores()
    # include new score
    new_name = "NULL"
    while len(new_name) != 3:
        new_name = input("Enter in a 3 letter username for your score: ")
    arr_user = list(new_name)
    arr_user.append(guess_num)
    scores_current.append(arr_user)
    # sort
    #y = 1
    #x = 0
    for x in range (len(scores_current)-1):
        for y in range (len(scores_current)-1-x):
            #if scores_current[y][3] == 0:
            #   scores_current[y][3] = 100
            #if scores_current[x][3] == 0:
            #   scores_current[x][3] = 100
            if scores_current[y][3] > scores_current[y+1][3]:
                temp = scores_current[y]
                scores_current [y] = scores_current[y+1]
                scores_current[y+1] = temp
    # update total amount of scores
    score_count_current = score_count_current + 1
    # write new scores
    eeprom.clear(2048) #clear all 2048 bytes of eeprom
    eeprom.write_block(0, [score_count_current,0,0,0])
    for z in range(len(scores_current)):
        for u in range(3):
            scores_current[z][u] = ord(scores_current[z][u])
        eeprom.write_block(z+1, scores_current[z])
    menu()
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    global current_value
    global current_guess
    current_guess = 0
    if GPIO.input(11):
        current_guess = current_guess + 1
    if GPIO.input(13):
        current_guess = current_guess + 2
    if GPIO.input(15):
        current_guess = current_guess + 4
    if current_guess == 7:
        GPIO.output(LED_value, 0)
        current_guess = -1
    current_guess += 1
    tempValue = f'{current_guess:03b}'
    GPIO.output(11, int(tempValue[2]))
    GPIO.output(13, int(tempValue[1]))
    GPIO.output(15, int(tempValue[0]))
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    global current_guess
    global compare_value
    global PWM_LED
    global PWM_buzzer
    global guess_num
    start = time.time()
    
    while GPIO.input(channel) == 0:
        pass
        
    button_press = time.time() - start
    
    # Change the PWM LED, if it's close enough, adjust the buzzer
    # if it's an exact guess: disable LEDs and Buzzer, tell the user and prompt them for a name, fetch all the scores, add the new score, sort the scores, store the scores back to the EEPROM, being sure to update the score count
    test = False
    if 0.05 < button_press < 0.4:
        compare_value = abs(value-current_guess)
        guess_num += 1
        test = True
        if compare_value == 0:
            PWM_LED.ChangeDutyCycle(0)
            PWM_buzzer.ChangeDutyCycle(0)
            print("Congratulations that was a correct guess!\nThat took you ", guess_num, " guess/s!")
            GPIO.output(LED_value,0)
            GPIO.output(LED_accuracy,0)
            GPIO.output(buzzer,0)
            PWM_LED.ChangeDutyCycle(0)
            PWM_buzzer.ChangeDutyCycle(0)
            save_scores()
        else:
            accuracy_leds() 
            trigger_buzzer() 
    if button_press > 1:
        end_of_game = True
    if test == False:
        GPIO.output(LED_value, 0)
        GPIO.output(LED_accuracy, 0)
        GPIO.output(buzzer, 0)
        PWM_LED.ChangeDutyCycle(0)
        PWM_buzzer.ChangeDutyCycle(0)
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # The % brightness should be directly proportional to the % "closeness"
    # For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%; if they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global compare_value
    global PWM_LED
    global current_guess
    global value

    if current_guess > value:
        bright = (8-current_guess)/(8-value)
    else:
        bright = current_guess/value
    PWM_LED.ChangeDutyCycle(round(bright*100))
    pass

# Sound Buzzer
def trigger_buzzer():
    # Want the frequency of the buzzer to change, the buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3/2/1, the buzzer should sound once/twice/4 every second
    global compare_value
    global PWM_buzzer
    duty_cycle = 50
    frequency = 1
    
    if compare_value == 1:
        frequency = 4
    else:
        if compare_value == 2:
            frequency = 2
        else: 
            if compare_value == 3:
                frequency = 1
            else:
                duty_cycle = 0  #not sure if need to reset
    PWM_buzzer.ChangeFrequency(frequency)
    PWM_buzzer.ChangeDutyCycle(duty_cycle)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
