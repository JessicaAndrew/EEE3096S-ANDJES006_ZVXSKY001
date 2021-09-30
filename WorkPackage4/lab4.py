import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import threading
import datetime
import RPi.GPIO as GPIO

# initialising varibles to be used in functions
toggle = 10.0
startTime = datetime.datetime.now().second
btn = 26
index = 0
check = 0
minute = datetime.datetime.now().minute

def set_toggle(root_path):
   global index
   global toggle
   # change ADC sample rate
   if index == 0:
      toggle = 5.0
      index = index + 1
   elif index == 1:
      toggle = 1.0
      index = index + 1
   elif index == 2:
      toggle = 10.0
      index = 0
   

def begin_sensing():
   global toggle
   global minute
   global check
   # start threading functionality
   thread = threading.Timer(toggle, begin_sensing)
   thread.daemon = True
   thread.start()
   temp = round((chanTEMP.voltage-0.5)/0.01,2) # calculate temperature from thermistor
   
   # statement to prevent time from resetting to 0 every 60s
   if datetime.datetime.now().minute !=  minute:
       check = check + 60 
   
   print(str(datetime.datetime.now().second-startTime+check) + "s\t\t" + str(chanTEMP.value) + "\t\t" + str(temp)+ "C\t\t" + str(chanLDR.value))
   minute = datetime.datetime.now().minute

if __name__ == "__main__":
   spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) # create the spi bus
   cs = digitalio.DigitalInOut(board.D5) # create the cs (chip select)
   mcp = MCP.MCP3008(spi, cs) # create the mcp object
   chanTEMP = AnalogIn(mcp, MCP.P1) # create an analog input channel on pin 1
   chanLDR = AnalogIn(mcp, MCP.P2) # create an analog input channel on pin 2
   GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) # setup for button
   GPIO.add_event_detect(btn, GPIO.FALLING, callback=set_toggle, bouncetime=400) # enable button debouncing
   
   print("Runtime\t\tTemp Reading\tTemp\t\tLight Reading")
   begin_sensing() # call function to generate output
   while True:
      pass # run forever
