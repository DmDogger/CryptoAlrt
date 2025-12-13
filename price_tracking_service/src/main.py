from faststream import FastStream
from dishka.integrations.faststream import setup_dishka
import structlog

from infrastructures.di_container import create_container
from infrastructures.tasks.tasks import kafka_broker, taskiq_broker, register_tasks

logger = structlog.getLogger(__name__)

container = create_container()


app = FastStream(kafka_broker)

setup_dishka(container, app)




