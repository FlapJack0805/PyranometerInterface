import paho.mqtt.client as mqtt
import math
import csv
import time
import board
import adafruit_mcp3421.mcp3421 as ADC
from adafruit_mcp3421.analog_in import AnalogIn
from software_testing_classes import MockAnalogIn
from software_testing_classes import MockADC


#Check to see if we're doing a software test
#If we are doing a test initailze the test 
#and put us in that mode
def initialize_adc(use_mock=False):
    if use_mock:
        return MockAnalogIn(MockADC())
    else:
        i2c = board.I2C()
        adc = ADC.MCP3421(i2c, gain=8, resolution=16, continuous_mode=True)
        return AnalogIn(adc)


# Takes a list of values and turns it into an average over a given time period
# time_interval is in seconds
# If the correct amount of time has not passed yet it gives the average of the values since the start of the program
# Doesn't take into account null values
def average(values: list, time_interval: int) -> float: 
    num_values = math.floor(time_interval / 3)

    # Filter out None values
    valid_values = [v for v in values[-num_values:] if v is not None]

    if not valid_values:
        return 0  # Return 0 if there are no valid readings

    return round(sum(valid_values) / len(valid_values), 2)

# Append a new reading to the end of our values list
# If the list is currently as big as it needs to be (200 values), remove the first element
def add_values(values: list, new_value: float):
    values.append(new_value)
    if len(values) > 200:
        values.pop(0)

# Resize CSV to ensure it doesn't exceed max data lines
def resize_csv(file_path: str, max_data_lines: int):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Check if there are more data lines than the maximum allowed
        if len(lines) > max_data_lines:  # There should be more than max_data_lines total lines
            header = lines[0]  # Store the header line
            # Calculate the number of data lines to keep (half of current lines minus the header)
            num_data_lines = len(lines) - 1  # Total lines minus the header
            half_data_lines = math.ceil(num_data_lines / 2)  # Keep half, rounded up

            # Retain only the last half_data_lines lines of data
            data_lines = lines[-half_data_lines:]  # Get the last half_data_lines lines
            with open(file_path, 'w') as f:
                f.write(header)  # Write the header back
                f.writelines(data_lines)
    except Exception as e:
        print(f"Error resizing CSV file: {e}")


# MQTT setup
mqtt_broker = "put broker address here"  # Replace with your broker address
mqtt_port = 1883  # Default MQTT port
mqtt_topic = "put topic here"  # Topic where data will be published

# Callback when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

# Callback for publishing messages
def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")
