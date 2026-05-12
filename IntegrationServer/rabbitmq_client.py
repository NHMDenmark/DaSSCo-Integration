import threading
from typing import Callable, Optional, Dict
import pika
import json
import signal
import logging
import ssl

class RabbitMqClient:

    def __init__(
        self,
        host_name: str = 'biovault.bhsi.xyz',
        port: int = 5672,
        run_async: bool = False,
        credentials: Optional[Dict[str, str]] = None,
    ):  
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.ssl_options = pika.SSLOptions(context)
        self.host_name = host_name
        self.port = port
        self.run_async = run_async
        self.credentials = credentials
        self._connection = self._create_connection()
        self.channel = self._connection.channel()
        self._producer_channel = None
        self._consumer_channel = None
        self._exit_event = threading.Event()


    def _create_connection(self):
        """
        Creates a connection to the RabbitMQ server
        :return: a blocking connection
        """
        params_kwargs = {"host": self.host_name, "port": self.port, "virtual_host": "/", "ssl_options": self.ssl_options}
        credentials = self._get_credentials()

        if credentials is not None:
            username, password = credentials
            params_kwargs["credentials"] = pika.PlainCredentials(username, password)

        connection = pika.BlockingConnection(pika.ConnectionParameters(**params_kwargs))

        return connection

    def add_handler(self, queue: str, handler: Callable):
        """
        Creates a synchronous or asynchronous depending on the run_async flag.

         consumer to a given queue
        :param queue: The name of the queue to consume messages from
        :param handler: The callback function to be executed
        :return: None
        """
        if self.run_async:
            self._add_handler_async(queue, handler)
        else:
            self._add_handler_sync(queue, handler)


    def _add_handler_sync(self, queue: str, handler: Callable):
        """
        Creates a synchronous consumer that listens for messages from a given queue.
        :param queue: The name of the queue to consume messages from.
        :param handler: The callback function to be executed whenever a message is consumed from the queue.
        :return: None
        """
        if self._consumer_channel is None:
            self._consumer_channel = self._connection.channel()
        self._prepare_consumer(self._consumer_channel, queue, handler)

    def _add_handler_async(self, queue: str, handler: Callable):
        """
        Creates an asynchronous consumer that listens for messages from a given queue.
        :param queue: The name of the queue to consume messages from.
        :param handler: The callback function to be executed whenever a message is consumed from the queue.
        :return: None
        """
        connection = self._create_connection()
        channel = connection.channel()
        thread = threading.Thread(
            target = self._consumer_thread,
            args = (channel, queue, handler),
            daemon = True
        )
        thread.start()

    def _consumer_thread(self, channel, queue, handler):
        """
        Used by an asynchronous handler to prepare a threaded consumer.
        :param channel: The channel used for message consumption.
        :param queue: The name of the queue to consume messages from.
        :param handler: The callback function to be executed whenever a message is consumed from the queue.
        :return: None
        """
        self._prepare_consumer(channel, queue, handler)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.close()

    def _prepare_consumer(self, channel, queue, handler):
        """
        Prepares a consumer on the specified channel for the given queue.

        The function declares the queue and ensures that it is durable and sets up a consumer callback.
        When the message arrives, the callback invokes the provided handler, and acknowledges the message.
        If the processing of the message fails, the message is negatively acknowledged.

        :param channel: The channel used for message consumption.
        :param queue: The name of the queue to consume messages from.
        :param handler: The callback function to be executed whenever a message is consumed from the queue.
        :return: None
        """
        channel.queue_declare(queue=queue, durable=True)

        def callback(ch, method, properties, body):
            try:
                message = body.decode('utf-8')
                handler(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Failed to process message: {body}. Error: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        channel.basic_consume(queue=queue, on_message_callback=callback)

    def publish(self, queue: str, payload: any):
        """
        Publishes a message to the specified queue.
        :param queue: The name of the queue to publish messages to.
        :param payload: The message to be published.
        :return: None
        """
        if self._producer_channel is None:
            self._producer_channel = self._connection.channel()
        self._producer_channel.basic_publish(
            exchange = '',
            routing_key = queue,
            body= json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode = pika.DeliveryMode.Persistent))

    def _get_credentials(self):
        """
        Extracts the credentials from the provided credentials dictionary.
        :return: A tuple (username, password) if credentials exist; otherwise None.
        """
        if self.credentials is not None:
            try:
                username = self.credentials['username']
                password = self.credentials['password']
            except KeyError:
                raise ValueError("Credentials must contain 'username' and 'password'")
            return username, password
        return None

    def _signal_handler(self, _signum, _frame):
        """
        Handles termination signals and triggers graceful shutdown.
        """
        self._exit_event.set()

    def start_consuming(self):
        """
        Starts the message consumption process.

        In asynchronous mode, signal handlers are registered for graceful shutdown.
        :return: None
        """
        if self.run_async:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self._exit_event.wait()
        else:
            try:
                self._consumer_channel.start_consuming()
            except KeyboardInterrupt:
                if self._consumer_channel is not None:
                    self._consumer_channel.close()
                if self._producer_channel is not None:
                    self._producer_channel.close()
                self._connection.close()
    
    def consume_one(self, queue: str, auto_ack: bool = False) -> Optional[str]:
        """
        Consumes a single message from the given queue.

        :param queue: Name of the queue to consume from.
        :param auto_ack: Whether to automatically acknowledge the message.
        :return: The message as a string, or None if no message is available.
        """
        #channel = self._connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)

        method_frame, header_frame, body = self.channel.basic_get(queue=queue, auto_ack=auto_ack)

        if method_frame:
            if not auto_ack:
                self.channel.basic_ack(method_frame.delivery_tag)
            return body.decode('utf-8')
        else:
            return None
        
    def get_msg_count(self, queue: str):

        queue = self.channel.queue_declare(queue=queue, durable=True)

        count = queue.method.message_count

        return count