# TODO: Add documentation on how to add support for message queues
import pika
import bson
from ..protocol import Snapshot


class SnapshotClient:
    def __init__(self, host, port, **config):
        self.fields = '.'.join(config['PARSERS'])
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()

        # Declare Snapshot exchange
        self.channel.exchange_declare(exchange='snapshots', exchange_type='topic')

    def __del__(self):
        self.connection.close()

    def publish(self, message):
        print('published')
        self.channel.basic_publish(exchange='snapshots',
                                   routing_key=self.fields,
                                   body=message)


class ParserClient:
    def __init__(self, host, port, parser):
        self.parser = parser
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()

        # Declare Snapshot exchange
        self.channel.exchange_declare(exchange='snapshots', exchange_type='topic')
        self.channel.queue_declare(queue=self.parser.field)
        self.channel.queue_bind(exchange='snapshots',
                                queue=self.parser.field,
                                routing_key=f'#.{self.parser.field}.#')
        self.channel.basic_consume(queue=self.parser.field,
                                   on_message_callback=self.on_consume,
                                   auto_ack=True)

        # Declare Parsed Data exchange
        self.channel.exchange_declare(exchange='parsed_data', exchange_type='direct')

    def __del__(self):
        self.connection.close()

    def consume(self):
        self.channel.start_consuming()

    def on_consume(self, channel, method, properties, body):
        parsed_data_encoded = self.parser(body)
        print(f'consumed: {body}')      # DEBUG
        channel.basic_publish(exchange='parsed_data',
                              routing_key=self.parser.field,
                              body=parsed_data_encoded)


class SaverClient:
    def __init__(self, host, port, db_client):
        self.db_client = db_client
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()

        # Declare Parsed Data exchange
        self.channel.exchange_declare(exchange='parsed_data', exchange_type='direct')
        self.channel.queue_declare(queue='save')

        for field in Snapshot.fields.keys():
            self.channel.queue_bind(exchange='parsed_data',
                                    queue='save',
                                    routing_key=field)
        self.channel.basic_consume(queue='save',
                                   on_message_callback=self.on_consume,
                                   auto_ack=True)

    def __del__(self):
        self.connection.close()

    def consume(self):
        self.channel.start_consuming()

    def on_consume(self, channel, method, properties, body):
        print(f'consumed: {body}')      # DEBUG
        self.db_client.save(field=method.routing_key, data=body)
