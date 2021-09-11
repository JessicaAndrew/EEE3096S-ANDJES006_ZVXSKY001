# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

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
    pass


# Setup Pins
def setup():
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
    PWM_buzzer = GPIO.PWM(buzzer,5)
    PWM_buzzer.start(0)
    #PWM_buzzer.ChangeDutyCycle(0)
    # Setup debouncing and callbacks
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_submit, GPIO.RISING, callback=btn_increase_pressed, bouncetime=100)
    GPIO.add_event_detect(btn_increase, GPIO.RISING, callback=btn_guess_pressed, bouncetime=100)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    score_count = eeprom.read(0,1) #not sure DOUBLE CHECK
    # Get the scores
    scores = []
    scores.append(eeprom.read_block(0,4))
    scores.append(eeprom.read_block(1,4))
    scores.append(eeprom.read_block(2,4))
    # convert the codes back to ascii
    for i in range(len(scores)):
        for j in range(3):
            scores[i][j] = chr(scores[i][j])
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    score_count_current, scores_current = fetch_scores()
    # include new score
    new_name = ""
    while len(new_name) != 3:
        new_name = input("Enter in a 3 letter username for your score: ")
    arr_user = list(new_name)
    arr_user.append(totalGuesses)
    scores_current.append(arr_user)
    # sort
    for x in range (len(scores_current-1)):
        for y in range (len(scores_current-1-x)):
            if scores_current[y][3] > scores_current[y+1][3]:
                temp = scores_current[y]
                scores_current [y] = scores_current[y+1]
                scores_current[y+1] = temp
    # update total amount of scores
    score_count_current = score_count_current + 1
    # write new scores
    #eeprom.clear() not sure if need to clear first
    eeprom.write_block(0, [score_count_current,0,0,0])
    for z in range(len(scores)):
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
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    
    # Compare the actual value with the user value displayed on the LEDs
    
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
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
