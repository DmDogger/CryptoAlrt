from faststream import FastStream
from faststream.kafka import KafkaBroker

from config.broker import BrokerSettings
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream

from infrastructures.di_container import create_container

_settings = BrokerSettings()
broker = KafkaBroker(_settings.bootstrap_servers)
app = FastStream(broker)

# Wire Dishka into FastStream so FromDishka[...] works in subscribers.
_container = create_container()
setup_dishka_faststream(_container, app, auto_inject=True)

# Import consumers to register subscribers
from infrastructures.consumer.alert_triggered_consumer import (
    consume_alert_triggered,
)  # noqa: F401

# region agent log
try:
    import json, time

    with open(
        "/Users/dmitrii/CryptoAlrt/.cursor/debug.log", "a", encoding="utf-8"
    ) as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "pre-fix",
                    "hypothesisId": "H1",
                    "location": "infrastructures/broker/broker.py",
                    "message": "Broker module imported (KafkaBroker backend)",
                    "data": {"bootstrap": _settings.bootstrap_servers},
                    "timestamp": int(time.time() * 1000),
                }
            )
            + "\n"
        )
except Exception:
    pass
# endregion
