from aiokafka import AIOKafkaProducer
from core.utils.settings import settings
import uuid
from core.helper.producer_helper import *
from core.utils.init_log import logger


async def produce_event(topic: str, value, key: str = str(uuid.uuid4()), headers: tuple | None = None) -> None:
    try:
        # Get the producer
        producer = AIOKafkaProducer(
            client_id=settings.api_event_streaming_client_id,
            bootstrap_servers=settings.api_event_streaming_host, 
        )

        # Start the producer and get brokers metedata
        logger.info('Starting kafka producer.')
        await producer.start()

        # Check if topic already exists
        topic_exist = await topic_exists(topic=topic)
        logger.info(f"Checking if topic:{topic} exists.")
        if not topic_exist:
            logger.info(f"Topic: {topic} not found.")
            await create_topic(topic=topic)

        # Produce message
        await producer.send_and_wait(key=key.encode(), value=value, topic=topic, headers=headers)

    except Exception as err:
        logger.error(f"Failed to start Kafka producer due to error: {str(err)}", exc_info=1)
    finally:
        logger.info('Closing Kafka producer.')
        await producer.stop()