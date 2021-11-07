"""
Utilities for interacting with RabbitMQ message broker
"""
import pika


def create_queue(host, queue):
    """
    Create queue
    :param host: hostname
    :param queue: queue name
    :return:
            connection: connection
            channel: channel
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    return connection, channel


def receive(channel, queue):
    """
    Receive single message from the specified queue
    :param channel: channel
    :param queue: queue name
    :return:
    """
    method_frame, header_frame, body = channel.basic_get(queue=queue)
    if method_frame is None:
        return ''
    else:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        return body
