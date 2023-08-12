from typing import Optional

from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
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


    def __init__(self, config: LlmConfig, topic: Optional[str]) -> None:
        self.bootstrap_servers = [f"{server}:{config.broker_port}" for server in config.bootstrap_servers]

        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers)
        except Exception as e:
            raise
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        except Exception as e:
            raise
        try:
            self.consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)
        except Exception as e:
            raise
        if topic:
            self.create_topic(topic)

    def create_topic(self, topic_name: str) -> str:
        """Creates a topic if it doesn't exist"""

        if self.admin_client is None:
            raise Exception("Admin client not initialized")
        if topic_name in self.admin_client.list_topics():
            return f"Topic {topic_name} already exists"
        try:
            self.admin_client.create_topics(
                [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)])
            return f"Topic {topic_name} created"
        except Exception as e:
            return f"Topic {topic_name} already exists"

    def send_message(self, message: str, topic: str) -> None:
        """Sends a message to a topic"""

        if self.producer is None:
            raise Exception("Producer not initialized")
        self.producer.send(topic, message.encode("utf-8"))

    def consume_messages(self, topic: str) -> str:
        """Consumes a message from a topic"""

        if self.consumer is None:
            raise Exception("Consumer not initialized")
        self.consumer.subscribe([topic])
        for message in self.consumer:
            return message.value.decode("utf-8")