from domain.events.threshold_triggered import ThresholdTriggeredEvent


class CheckThresholdUseCase:
    def __init__(
            self,
            threshold_triggered_event: ThresholdTriggeredEvent,

    ):
        self._threshold_triggered_event = threshold_triggered_event



# TODO: нужен список событий
# TODO: сначала проверяем трешхолд и если тру, тогда отправляем событие
# TODO: здесь будет проверка трешхолда и публикация события