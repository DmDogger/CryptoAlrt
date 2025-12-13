# Use Cases Tests

Этот каталог содержит юнит-тесты для use cases (бизнес-логики приложения).

## Структура

- `test_fetch_and_save_to_database.py` - Тесты для `FetchAndSaveUseCase`

## Запуск тестов

### Запустить все тесты use cases:
```bash
pytest tests/application/use_cases/ -v
```

### Запустить конкретный тестовый файл:
```bash
pytest tests/application/use_cases/test_fetch_and_save_to_database.py -v
```

### Запустить конкретный тест:
```bash
pytest tests/application/use_cases/test_fetch_and_save_to_database.py::TestFetchAndSaveUseCase::test_execute_with_existing_cryptocurrency -v
```

### С покрытием кода:
```bash
pytest tests/application/use_cases/ --cov=src/application/use_cases --cov-report=html
```

## Тесты FetchAndSaveUseCase

### Покрытые сценарии:

1. **test_execute_with_existing_cryptocurrency** - Сохранение цены для существующей криптовалюты
2. **test_execute_with_new_cryptocurrency** - Создание новой криптовалюты и сохранение цены
3. **test_execute_coingecko_returns_none** - Обработка None от CoinGecko API
4. **test_execute_coingecko_api_fails** - Обработка ошибок API
5. **test_execute_repository_save_fails** - Обработка ошибок сохранения криптовалюты
6. **test_execute_save_price_fails** - Обработка ошибок сохранения цены
7. **test_execute_with_different_coin_ids** - Работа с разными coin_id
8. **test_execute_full_flow_new_cryptocurrency** - Полный flow создания криптовалюты
9. **test_execute_logging** - Проверка логирования

## Используемые моки

- `mock_coingecko_client` - Мок CoinGecko клиента
- `mock_crypto_repository` - Мок репозитория криптовалют
- `sample_coingecko_dto` - Тестовый DTO от CoinGecko
- `sample_crypto_entity` - Тестовая сущность криптовалюты

## Примечания

- Все асинхронные тесты помечены декоратором `@pytest.mark.asyncio`
- Используется `unittest.mock.AsyncMock` для моков асинхронных методов
- Тесты изолированы и не требуют реальной базы данных или API
