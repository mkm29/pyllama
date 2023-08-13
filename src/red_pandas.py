from typing import Optional, List
import re

from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.producer.future import FutureRecordMetadata

from config import LlmConfig


class RedPandas:
    """RedPandas class"""

    # properties
    @property
    def bootstrap_servers(self) -> list:
        return self._bootstrap_servers

    @bootstrap_servers.setter
    def bootstrap_servers(self, bootstrap_servers: list) -> None:
        self._bootstrap_servers = bootstrap_servers

    @property
    def admin_client(self) -> KafkaAdminClient:
        return self._admin_client

    @admin_client.setter
    def admin_client(self, admin_client: KafkaAdminClient) -> None:
        self._admin_client = admin_client

    @property
    def producer(self) -> KafkaProducer:
        return self._producer

    @producer.setter
    def producer(self, producer: KafkaProducer) -> None:
        self._producer = producer

    @property
    def consumer(self) -> KafkaConsumer:
        return self._consumer

    @consumer.setter
    def consumer(self, consumer: KafkaConsumer) -> None:
        self._consumer = consumer

    def __init__(self, config: LlmConfig, topic: Optional[str] = None, auto_offset_reset: Optional[str] = None) -> None:
        self.bootstrap_servers = [
            f"{server}:{config.broker_port}" for server in config.bootstrap_servers
        ]
        # assert that auto_offset_reset is earliest or latest
        assert auto_offset_reset in [None, "earliest", "latest"]


        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers
            )
        except Exception as e:
            raise
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        except Exception as e:
            raise
        try:
            self.consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers, auto_offset_reset=auto_offset_reset)
        except Exception as e:
            raise
        if config.topic_name:
            self.create_topic(topic)

    def create_topic(self, topic_name: str) -> str:
        """Creates a topic if it doesn't exist"""

        if self.admin_client is None:
            raise Exception("Admin client not initialized")
        if topic_name in self.admin_client.list_topics():
            return f"Topic {topic_name} already exists"
        try:
            self.admin_client.create_topics(
                [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)]
            )
            return f"Topic {topic_name} created"
        except Exception as e:
            return f"Topic {topic_name} already exists"


    def send_message(self, message: bytes, topic: str) -> List[FutureRecordMetadata]:
        """Sends a message to a topic"""

        if self.producer is None:
            raise Exception("Producer not initialized")
        if message == b'':
            return
        # regex = re.compile(r'\d+\.')
        # if regex.match(message.decode("utf-8")):
        #     return

        # if message contains a newline character it will base64 encode the message
        if b"\n" in message:
            # split into 2 messages
            messages = message.split(b"\n")
        else:
            messages = [message]
        results = []
        for msg in messages:
            results.append(self.producer.send(topic, value=msg))
        # flush
        self.producer.flush()

    def consume_messages(self, topic: str, offset: int = None) -> str:
        """Consumes a message from a topic"""

        if self.consumer is None:
            raise Exception("Consumer not initialized")
        print("Consuming messages")
        self.consumer.subscribe([topic])
        value = []
        for message in self.consumer:
            print(f"Consumed message: {message.value.decode('utf-8')}")
            value.append(message.value.decode("utf-8"))
        return "\n".join(value)
