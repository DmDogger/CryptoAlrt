from faststream import FastStream
from faststream.kafka import KafkaBroker

from config.broker import BrokerSettings
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream

from infrastructures.di_container import create_container

_settings = BrokerSettings()
broker = KafkaBroker(_settings.bootstrap_servers)
app = FastStream(broker)

_container = create_container()
setup_dishka_faststream(_container, app, auto_inject=True)

from infrastructures.consumer import alert_triggered_consumer  # noqa: F401
