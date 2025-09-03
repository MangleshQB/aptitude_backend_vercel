import json
from kafka import KafkaProducer


class QbKafkaProducer:
    def __init__(self) -> None:
        self.producer = KafkaProducer(bootstrap_servers='192.168.1.202:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = 'test'

    def publish(self, method, body):
        print(f'Inside {method}: Sending to Kafka: ')
        print(body)
        self.producer.send('test', value=body)
