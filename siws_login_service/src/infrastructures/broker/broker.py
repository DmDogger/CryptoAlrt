from faststream import FastStream
from faststream.kafka import KafkaBroker

from src.config.broker import BrokerSettings

_settings = BrokerSettings()
broker = KafkaBroker(_settings.bootstrap_servers)
app = FastStream(broker)


