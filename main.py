from utilities import *
import paho.mqtt.client as mqtt
import math
import csv
import time
import board
import adafruit_mcp3421.mcp3421 as ADC
from adafruit_mcp3421.analog_in import AnalogIn
from software_testing_classes import MockAnalogIn
from software_testing_classes import MockADC


# Main function
def main():
    # Set up MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    # Connect to the MQTT broker
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()  # Start the MQTT client loop

    file_path = 'pyranometer_data.csv'

    with open(file_path, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(['Time (s)', 'ADC Value', '30s Avg', '5m Avg', '10m Avg'])

        # Initialize the I2C connection
        while True:
            try:
                i2c = board.I2C()  # Initialize I2C bus
                break
            except Exception as e:
                print(f"Couldn't find board, retrying in 5 seconds: {e}")
                time.sleep(5)

        # Initialize the MCP3421 ADC
        while True:
            try:
                adc = ADC.MCP3421(i2c, gain=8, resolution=16, continuous_mode=True)
                break
            except Exception as e:
                print(f"ADC initialization error: {e}, retrying in 5 seconds")
                time.sleep(5)

        adc_channel = AnalogIn(adc)

        print(f"ADC initialized with gain: {adc.gain}X, resolution: {adc.resolution}-bit")

        pyranometer_values = []
        current_time = 0
        while True:
            try:
                value = adc_channel.value
                add_values(pyranometer_values, value)
                mean_30_sec = average(pyranometer_values, 30)
                mean_5_min = average(pyranometer_values, 300)
                mean_10_min = average(pyranometer_values, 600)

                # Write data to CSV
                csv_writer.writerow([current_time, value, mean_30_sec, mean_5_min, mean_10_min])

                # Publish data to MQTT
                payload = {
                    'time': current_time,
                    'adc_value': value,
                    'mean_30_sec': mean_30_sec,
                    'mean_5_min': mean_5_min,
                    'mean_10_min': mean_10_min
                }
                payload_str = str(payload)  # Convert dictionary to string
                client.publish(mqtt_topic, payload_str)

                # Resize CSV to keep size under limit
                resize_csv(file_path, 2000)

                time.sleep(3)
                current_time += 3
            
            except Exception as e:
                # Handle data read errors and continue processing
                print(f"Error reading data: {e}. Continuing operation with None value.")
                add_values(pyranometer_values, None)
                time.sleep(3)
                current_time += 3

if __name__ == "__main__":
    main()

