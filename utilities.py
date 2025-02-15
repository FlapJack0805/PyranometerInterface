import paho.mqtt.client as mqtt
import math
import csv
import time
import usb.core
import usb.util
import usb
from software_testing_classes import MockAnalogIn
from software_testing_classes import MockADC

#Check to see if we're doing a software test
def initialize_adc(use_mock=False):
    if use_mock:
        return MockAnalogIn(MockADC())
    else:
        while (True):
            try:
                # Find the MCP2221 device
                mcp2221 = usb.core.find(idVendor=0x04D8, idProduct=0x00DD)  # MCP2221 vendor and product IDs
                if mcp2221 is None:
                    raise ValueError()
                else:
                    break
            except ValueError:
                print("MCP2221device not found, retrying in 5 seconds")
                time.sleep(5)
        
        MCP3421_ADDR = 0x68
        config_byte = 0b10001100
        dev.ctrl_transfer(0x40, 0x10, 0, 0, [MCP3421_AADR << 1, config_byte])

        #Wait for conversion to complete
        time.sleep(0.1)

        # Now, communicate via USB to the MCP3421 via I2C
        return mcp2221  # You would use the I2C communication manually with this device

# Takes a list of values and turns it into an average over a given time period
def average(values: list, time_interval: int) -> float:
    num_values = math.floor(time_interval / 3)
    valid_values = [v for v in values[-num_values:] if v is not None]
    if not valid_values:
        return 0
    return round(sum(valid_values) / len(valid_values), 2)

# Append a new reading to the end of our values list
def add_values(values: list, new_value: float):
    values.append(new_value)
    if len(values) > 200:
        values.pop(0)

# Resize CSV to ensure it doesn't exceed max data lines
def resize_csv(file_path: str, max_data_lines: int):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if len(lines) > max_data_lines:
            header = lines[0]
            num_data_lines = len(lines) - 1
            half_data_lines = math.ceil(num_data_lines / 2)
            data_lines = lines[-half_data_lines:]
            with open(file_path, 'w') as f:
                f.write(header)
                f.writelines(data_lines)
    except Exception as e:
        print(f"Error resizing CSV file: {e}")

def read_adc_value(mcp2221):
    #read 2 bytes from MCP3421
    response = mcp2221.ctrl_transfer(0xC0, 0x90, 0, 0, 2)

    #convert received bytes to an integer
    adc_value = (response[0] << 8) | response[1]
    if adc_value & 0x8000:  # Handle two's complement for negative values
        adc_value -= 1 << 16

    #calculate voltage (assuming PGA = 1, Vref = 2.048V)
    voltage = (adc_value / 32768.0) * 2.048

    return voltage

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")