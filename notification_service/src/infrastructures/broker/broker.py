from faststream import FastStream
from faststream.confluent import KafkaBroker

from config.broker import BrokerSettings

_settings = BrokerSettings()
broker = KafkaBroker(_settings.bootstrap_servers)
app = FastStream(broker)
