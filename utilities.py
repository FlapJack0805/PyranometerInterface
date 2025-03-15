import paho.mqtt.client as mqtt
import math
import csv
import time
import usb.core
import usb.util
import usb
import hid

#Check to see if we're doing a software test
def initialize_adc():
    while True:
        try:
            mcp2221 = hid.device()
            mcp2221.open(0x04D8, 0x00DD)
            
            break
        except Exception as e:
            print(f"MCP2221 device not found, retrying in 5 seconds")
            time.sleep(5)

    return mcp2221


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
    MCP3421_ADDR = 0x68
    config_byte = 0b10011100  # Set resolution, PGA, and mode

    #Send I2C write command to configure MCP3421
    mcp2221.write([0x10, MCP3421_ADDR << 1, config_byte])

    #wait for conversion to complete (MCP3421 needs time)
    time.sleep(0.1)

    #Request 3 bytes from MCP3421
    mcp2221.write([0x40, MCP3421_ADDR << 1, 3])
    response = mcp2221.read(3)

    #Convert the response into an integer (24-bit value)
    adc_value = (response[0] << 16) | (response[1] << 8) | response[2]

    #Handle two's complement for negative values (24-bit sign bit)
    if adc_value & 0x800000:
        adc_value -= 1 << 24

    #Calculate voltage (PGA = 1, Vref = 2.048V)
    voltage = (adc_value / 8388608.0) * 2.048  # 2^23 = 8388608 for 24-bit

    return voltage

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")