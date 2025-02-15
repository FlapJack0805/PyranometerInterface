from utilities import *
from software_testing_classes import MockMQTTClient

def test_main():
    mock_adc = initialize_adc(use_mock=True)
    mock_client = MockMQTTClient()

    file_path = 'pyranometer_data.csv'

    with open(file_path, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(['Time (s)', 'ADC Value', '30s Avg', '5m Avg', '10m Avg'])

        pyranometer_values = []
        for _ in range(10000):  # Simulate 10 readings
            value = mock_adc.value
            add_values(pyranometer_values, value)
            mean_30_sec = average(pyranometer_values, 30)
            mean_5_min = average(pyranometer_values, 300)
            mean_10_min = average(pyranometer_values, 600)

            payload = {
                'time': _ * 3,
                'adc_value': value,
                'mean_30_sec': mean_30_sec,
                'mean_5_min': mean_5_min,
                'mean_10_min': mean_10_min
            }
            mock_client.publish("test/topic", str(payload))

            csv_writer.writerow([payload['time'], value, mean_30_sec, mean_5_min, mean_10_min])


test_main()
