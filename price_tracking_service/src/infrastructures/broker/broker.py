from faststream import FastStream
from faststream.kafka import KafkaBroker
from taskiq_faststream import BrokerWrapper

from config.broker import BrokerSettings

_settings = BrokerSettings()
broker = KafkaBroker(_settings.bootstrap_servers)
app = FastStream(broker)

taskiq_broker = BrokerWrapper(broker)
