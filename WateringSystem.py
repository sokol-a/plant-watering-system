import machine, utime
import network, socket
from machine import Pin
import _thread


analog_val = machine.ADC(27)
pump_pin = Pin(21, mode=Pin.OUT)
pump_pin.off()

dry_val = 23000
wet_val = 17600
def percentage(value):
    if value < 17600:
        value = 17600
    elif value > 23000:
        value = 23000
        
    
    rnge = dry_val - wet_val
    diff = abs(value-dry_val)
    percentage = 100*(diff/rnge)
    
    return int(percentage)
    

def fail_safe(time_stamps):
    
    if len(time_stamps) > 11:
        time_start_hour = time_stamps[-10][0]
        time_start_min = time_stamps[-10][1]
        time_end_hour = time_stamps[-1][0]
        time_end_min = time_stamps[-1][1]
     
        
        diff_hr = time_end_hour - time_start_hour
        
        if diff_hr == 1:
            min_start = 60 - time_start_min
            
            elapsed_mins = min_start + time_end_min
            
        elif diff_hr < 1:
            elapsed_mins = time_end_min - time_start_min
            
        else:
            pass
        
        if elapsed_mins < 3:
            print("I've watered too much, that's enough for now!")
            utime.sleep(600)
            return False
        else:
            return True
            
        
    else:
        return True


    

def background_thread():
    global last_watering
    last_watering = {"date": [utime.localtime()[0:3]],
                     "time": [utime.localtime()[3:6]]}
    global time_stamps
    time_stamps = []
    samples = 0
    while True:
        time_stamps.append(utime.localtime()[3:6])
        list_of_samples = []
        while len(list_of_samples) < 100:
            reading = analog_val.read_u16()
            list_of_samples.append(reading)
            utime.sleep(0.1)
        global average_val
        average_val = sum(list_of_samples)/ len(list_of_samples) 
        global soil_moisture
        soil_moisture = percentage(average_val)


        if soil_moisture < 25 and fail_safe(time_stamps):
            pump_pin.on()
            utime.sleep(2.5)
            pump_pin.off()
            
            last_watering["time"].append(utime.localtime()[3:6])
            last_watering["date"].append(utime.localtime()[0:3])
            
        else:
            pump_pin.off()
    

        
        if len(time_stamps) > 20:
            time_stamps = []
        
        if len(last_watering["time"]) > 10:
            last_watering["time"] = last_watering["time"][-10:]
            last_watering["date"] = last_watering["date"][-10:]

_thread.start_new_thread(background_thread, ())

while True:
    user_input = input("Enter command: ")
    
    if user_input == "m" and soil_moisture != None:
        print(f"Current soil moisture is: {soil_moisture}")
    elif user_input == "lw" and len(last_watering['time']) > 2:
        print(f"I was last watered at: {last_watering['time'][-1][0]}:{last_watering['time'][-1][1]}:{last_watering['time'][-1][2]} on {last_watering['date'][-1][1]}/{last_watering['date'][-1][2]} and also at: {last_watering['time'][-2][0]}:{last_watering['time'][-2][1]}:{last_watering['time'][-2][2]} on {last_watering['date'][-2][1]}/{last_watering['date'][-2][2]}")
    
    elif user_input == "adcval":
        print(f"Last ADC reading was: {average_val}")
        
    elif user_input == "qw":
        pump_pin.on()
        for i in range(5):
            secs = i+1
            print(f"Watering for {secs} seconds")
            utime.sleep(1)
            last_watering["time"].append(utime.localtime()[3:6])
            last_watering["date"].append(utime.localtime()[0:3])
        pump_pin.off()
        
    elif user_input == "stop":
        print("STOPPING!")
        pump_pin.off()
        
    elif user_input == "ts":
        print(time_stamps)
        
    else:
        continue
        
    
    
        
    
    