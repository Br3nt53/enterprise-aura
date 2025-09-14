import json

from aiokafka import AIOKafkaConsumer

from .base import DetectionSource, batch


class KafkaSource(DetectionSource):
    def __init__(self, brokers: str, topic: str, group_id: str = "aura-dev"):
        self.brokers, self.topic, self.group_id = brokers, topic, group_id

    async def frames(self):
        consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.brokers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await consumer.start()
        try:
            camera = []
            async for msg in consumer:
                camera.append(msg.value)
                if len(camera) >= 32:  # simple batch
                    yield batch(camera=camera)
                camera = []
        finally:
            await consumer.stop()
