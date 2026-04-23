import json
# from kafka import KafkaProducer
from confluent_kafka import Producer

class QbKafkaProducer:
    def __init__(self) -> None:
        self.producer = Producer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = 'test'

    def publish(self, method, body):
        print(f'Inside {method}: Sending to Kafka: ')
        print(body)
        self.producer.send('test', value=body)
