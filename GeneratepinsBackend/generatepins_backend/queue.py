import json
import pika

from .db import USERNAME, PASSWORD, MQ_HOST, VIRTUAL_HOST, WORKER_KEY, WORKER_QUEUE

exchange_name = "messaging"
queue_name = WORKER_QUEUE
binding_key = WORKER_KEY


def publish_message(data):
    params = pika.ConnectionParameters(host=MQ_HOST,
                                       virtual_host=VIRTUAL_HOST,
                                       credentials=pika.PlainCredentials(
                                           username=USERNAME,
                                           password=PASSWORD))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name,
                             exchange_type="topic",
                             durable=True)

    channel.queue_declare(queue=queue_name)

    channel.queue_bind(queue=queue_name,
                       exchange=exchange_name,
                       routing_key=binding_key)

    channel.basic_publish(exchange=exchange_name,
                          routing_key=binding_key,
                          body=json.dumps(data))

    print("Droped Messsage")

    connection.close()
