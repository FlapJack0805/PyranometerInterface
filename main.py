from utilities import *

def main():
    #MQTT setup
    '''
    mqtt_broker = "mqtt_broker_address"
    mqtt_port = 1883
    mqtt_topic = "pyranometer/data"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()
'''
    file_path = 'pyranometer_data.csv'

    with open(file_path, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Time (s)', 'ADC Value', '30s Avg', '5m Avg', '10m Avg'])

    #initialize the MCP2221 device
    mcp2221 = initialize_adc()

    pyranometer_values = []
    current_time = 0

    while True:
        try:
            value = read_adc_value(mcp2221)
            add_values(pyranometer_values, value)

            #compute averages
            mean_30_sec = average(pyranometer_values, 30)
            mean_5_min = average(pyranometer_values, 300)
            mean_10_min = average(pyranometer_values, 600)

            #write data to CSV
            with open(file_path, mode='a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([current_time, value, mean_30_sec, mean_5_min, mean_10_min])

            #publish data to MQTT
            payload = {
                'time': current_time,
                'adc_value': value,
                'mean_30_sec': mean_30_sec,
                'mean_5_min': mean_5_min,
                'mean_10_min': mean_10_min
            }
            #client.publish(mqtt_topic, str(payload))


            time.sleep(3)
            current_time += 3
        
        except Exception as e:
            print(f"Error reading data: {e}. Continuing operation with None value.")
            add_values(pyranometer_values, None)
            time.sleep(3)
            current_time += 3

if __name__ == "__main__":
    main()
