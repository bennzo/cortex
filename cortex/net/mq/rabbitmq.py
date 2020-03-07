# TODO: Add documentation on how to add support for message queues
import pika
import bson


class SnapshotClient:
    def __init__(self, host, port, **config):
        self.fields = '.'.join(config['PARSERS'])
        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='snapshots', exchange_type='topic')

    def __del__(self):
        self.connection.close()

    def publish(self, message):
        self.channel.basic_publish(exchange='topic_logs',
                                   routing_key=self.fields,
                                   body=message)


class ParserClient:
    def __init__(self, host, port, field, parser):
        self.parser = parser
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()

        # Declare Snapshot exchange
        self.channel.exchange_declare(exchange='snapshots', exchange_type='topic')
        self.channel.queue_declare(queue=field)
        self.channel.queue_bind(exchange='topic_logs',
                                queue=field,
                                routing_key=f'#{field}#')
        self.channel.basic_consume(queue=field,
                                   on_message_callback=self.on_consume,
                                   auto_ack=True)

        # Declare Parsed Data exchange
        self.channel.exchange_declare(exchange='parsed_data', exchange_type='fanout')

    def __del__(self):
        self.connection.close()

    def consume(self):
        self.channel.start_consuming()

    def on_consume(self, channel, method, properties, body):
        parsed_data_encoded = self.parser(body)
        channel.basic_publish(exchange='parsed_data',
                              body=parsed_data_encoded)



class SaverClient:
    def __init__(self, host, port):
        pass

    def __del__(self):
        pass

    def consume(self, message):
        pass
