import random

class MockADC:
    def __init__(self):
        self.gain = 8
        self.resolution = 16

    def read_adc(self):
        return random.randint(1, 2000)  # Simulated ADC value with variabilit  # Simulated ADC value


class MockAnalogIn:
    def __init__(self, adc):
        self._adc = adc

    @property
    def value(self):
        return self._adc.read_adc()


class MockMQTTClient:
    def __init__(self):
        self.published_messages = []

    def connect(self, broker, port, keepalive):
        print(f"Mock connected to MQTT broker {broker}:{port}")

    def publish(self, topic, payload):
        print(f"Mock published to {topic}: {payload}")
        self.published_messages.append((topic, payload))

    def loop_start(self):
        pass
