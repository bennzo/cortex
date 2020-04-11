import pika
import bson
from ..protocol import Snapshot


class SnapshotClient:
    """RabbitMQ Snapshot client

    Used by the main server as to communicate Snapshots to other listeners on the exchange
    such as the Parsers and the Savers

    Args:
        host (:obj:`str`): Hostname of the RabbitMQ server
        port (:obj:`int`): Port of the RabbitMQ server
    """
    def __init__(self, host, port, **config):
        self.parsers = config['PARSERS']
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, heartbeat=0))
        self.channel = self.connection.channel()

        # Declare Snapshot exchange
        self.channel.exchange_declare(exchange='snapshots', exchange_type='topic')

    def __del__(self):
        self.connection.close()

    def publish(self, message):
        """Publishes a message to the queue

        Args:
            message (:obj:`str`): Message to publish
        """
        # TODO: remove print
        # print('published')
        # Intersect between the snapshot fields and the supported parsers
        exist_supported_fields = message['snapshot'].keys() & set(self.parsers)
        self.channel.basic_publish(exchange='snapshots',
                                   routing_key='.'.join(exist_supported_fields),
                                   body=bson.encode(message))


class ParserClient:
    """RabbitMQ Parser client

    Envelopes a :class:`cortex.parsers.parser.Parser` and uses it to parse consumed Snapshots and publish
    parsed Snapshots

    Args:
        host (:obj:`str`): Hostname of the RabbitMQ server
        port (:obj:`int`): Port of the RabbitMQ server
        port (:class:`cortex.parsers.parser.Parser`): A Snapshot parser
    """
    def __init__(self, host, port, parser):
        self.parser = parser
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, heartbeat=0))
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
        """Start consuming from the message queue
        """
        self.channel.start_consuming()

    def on_consume(self, channel, method, properties, body):
        """Callback function on message consuming

        The callback basically parses the consumed message and publishes it to the saver exchange
        """
        # TODO: remove print
        # print(f'consumed: {body}')      # DEBUG
        parsed_data_encoded = self.parser(body)
        channel.basic_publish(exchange='parsed_data',
                              routing_key=self.parser.field,
                              body=parsed_data_encoded)


class SaverClient:
    """RabbitMQ Saver client

    Envelopes a Database SaverClient from :mod:`cortex.net.db` and uses it to save consumed Snapshots to the database

    Args:
        host (:obj:`str`): Hostname of the RabbitMQ server
        port (:obj:`int`): Port of the RabbitMQ server
        db_client: A Database SaverClient from :mod:`cortex.net.db`
    """
    def __init__(self, host, port, db_client):
        self.db_client = db_client
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, heartbeat=0))
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
        """Start consuming from the message queue
        """
        self.channel.start_consuming()

    def on_consume(self, channel, method, properties, body):
        """Callback function on message consuming

        The callback basically calls the db client save method with the consumed message
        """
        # TODO Remove print
        # print(f'consumed: {body}')      # DEBUG
        self.db_client.save(field=method.routing_key, data=body)
