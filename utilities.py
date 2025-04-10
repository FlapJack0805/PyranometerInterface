import paho.mqtt.client as mqtt
import math
import csv
import time


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


def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")
