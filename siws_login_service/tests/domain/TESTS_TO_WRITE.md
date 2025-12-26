# Список тестов для Domain Layer

## Фикстуры доступные:
- `sample_wallet_vo` - WalletAddressVO
- `sample_nonce_vo` - NonceVO (сгенерированный)
- `sample_nonce_entity` - NonceEntity (созданный через create)
- `sample_wallet_entity` - WalletEntity (созданный через create)
- `sample_wallet_logged_in_event` - WalletLoggedInEvent (созданный через create_event)

---

## 1. test_wallet_address_vo.py

### TestWalletAddressVO

1. ✅ `test_create_valid_wallet_address_vo` - уже есть
   - Использует: `sample_wallet_vo`
   - Проверяет: создание валидного WalletAddressVO

2. `test_wallet_address_vo_from_string_creates_valid_instance`
   - Использует: создает WalletAddressVO через `from_string()`
   - Проверяет: factory method работает корректно

3. `test_wallet_address_vo_invalid_length_raises_error`
   - Создает WalletAddressVO с невалидной длиной (не 32 байта)
   - Ожидает: `InvalidWalletAddressError`

4. `test_wallet_address_vo_invalid_base58_raises_error`
   - Создает WalletAddressVO с невалидным base58
   - Ожидает: `InvalidWalletAddressError`

5. `test_wallet_address_vo_to_bytes_returns_correct_length`
   - Использует: `sample_wallet_vo`
   - Проверяет: `to_bytes()` возвращает 32 байта

6. `test_wallet_address_vo_from_string_with_non_string_raises_error`
   - Вызывает `from_string()` с не-строкой
   - Ожидает: `InvalidWalletAddressError`

---

## 2. test_nonce_vo.py

### TestNonceVO

1. `test_create_valid_nonce_vo`
   - Использует: `sample_nonce_vo`
   - Проверяет: создание валидного NonceVO

2. `test_nonce_vo_generate_creates_valid_nonce`
   - Вызывает `NonceVO.generate()`
   - Проверяет: создается валидный NonceVO

3. `test_nonce_vo_generate_creates_unique_values`
   - Вызывает `NonceVO.generate()` дважды
   - Проверяет: значения разные

4. `test_nonce_vo_generate_has_minimum_length`
   - Вызывает `NonceVO.generate()`
   - Проверяет: длина >= 8 символов

5. `test_nonce_vo_short_value_raises_error`
   - Создает NonceVO с длиной < 8 символов
   - Ожидает: `NonceValidationError`

6. `test_nonce_vo_empty_value_raises_error`
   - Создает NonceVO с пустым значением
   - Ожидает: `NonceValidationError`

---

## 3. test_signature_vo.py

### TestSignatureVO

1. `test_create_valid_signature_vo`
   - Создает валидный SignatureVO (64 байта)
   - Проверяет: создание успешно

2. `test_signature_vo_from_string_creates_valid_instance`
   - Использует `from_string()` для создания
   - Проверяет: factory method работает

3. `test_signature_vo_invalid_length_raises_error`
   - Создает SignatureVO с невалидной длиной (не 64 байта)
   - Ожидает: `SignatureValidationError`

4. `test_signature_vo_invalid_base58_raises_error`
   - Создает SignatureVO с невалидным base58
   - Ожидает: `SignatureValidationError`

5. `test_signature_vo_to_bytes_returns_correct_length`
   - Создает валидный SignatureVO
   - Проверяет: `to_bytes()` возвращает 64 байта

6. `test_signature_vo_from_string_with_non_string_raises_error`
   - Вызывает `from_string()` с не-строкой
   - Ожидает: `SignatureValidationError`

---

## 4. test_message_vo.py

### TestMessageVO

1. `test_create_valid_message_vo`
   - Создает валидный MessageVO
   - Использует: `sample_wallet_vo`, `sample_nonce_vo`

2. `test_create_message_vo_with_statement`
   - Создает MessageVO с statement
   - Проверяет: statement сохраняется

3. `test_create_message_vo_without_statement`
   - Создает MessageVO без statement (None)
   - Проверяет: statement = None

4. `test_message_vo_invalid_date_range_raises_error`
   - Создает MessageVO с issued_at >= expiration_time
   - Ожидает: `DateValidationError`

5. `test_message_vo_invalid_wallet_address_type_raises_error`
   - Создает MessageVO с невалидным типом wallet_address
   - Ожидает: `InvalidWalletAddressError`

6. `test_message_vo_to_string_contains_all_fields`
   - Использует: созданный MessageVO
   - Проверяет: `to_string()` содержит все обязательные поля

7. `test_message_vo_to_string_includes_statement_when_present`
   - Создает MessageVO со statement
   - Проверяет: `to_string()` включает statement

8. `test_message_vo_to_string_excludes_statement_when_none`
   - Создает MessageVO без statement
   - Проверяет: `to_string()` не включает statement

9. `test_message_vo_to_string_format_is_correct`
   - Проверяет: формат соответствует SIWE спецификации

10. `test_message_vo_from_record_creates_valid_instance`
    - **ПРОБЛЕМА**: метод принимает NonceVO, но должен принимать NonceEntity
    - Если исправлено: тестировать создание из NonceEntity

---

## 5. test_wallet_entity.py

### TestWalletEntity

1. `test_create_valid_wallet_entity`
   - Использует: `sample_wallet_entity`
   - Проверяет: создание успешно

2. `test_wallet_entity_create_generates_uuid`
   - Вызывает `WalletEntity.create()`
   - Проверяет: UUID сгенерирован

3. `test_wallet_entity_create_sets_current_timestamps`
   - Вызывает `WalletEntity.create()`
   - Проверяет: last_active и created_at установлены на текущее время

4. `test_wallet_entity_invalid_wallet_address_type_raises_error`
   - Создает WalletEntity с невалидным типом wallet_address
   - Ожидает: `InvalidWalletAddressError`

5. `test_wallet_entity_future_created_at_raises_error`
   - Создает WalletEntity с created_at в будущем
   - Ожидает: `DateValidationError`

6. `test_wallet_entity_ping_updates_last_active`
   - Использует: `sample_wallet_entity`
   - Вызывает `ping()`
   - Проверяет: last_active обновлен, created_at не изменился

7. `test_wallet_entity_ping_returns_new_instance`
   - Использует: `sample_wallet_entity`
   - Вызывает `ping()`
   - Проверяет: возвращается новый экземпляр (immutability)

8. `test_wallet_entity_ping_preserves_other_fields`
   - Использует: `sample_wallet_entity`
   - Вызывает `ping()`
   - Проверяет: остальные поля не изменились

9. `test_wallet_entity_to_bytes_returns_correct_length`
   - Использует: `sample_wallet_entity`
   - Проверяет: `to_bytes()` возвращает 32 байта

10. `test_wallet_entity_to_bytes_handles_invalid_address`
    - Создает WalletEntity с невалидным адресом (если возможно)
    - Проверяет: `to_bytes()` вызывает `InvalidWalletAddressError`

---

## 6. test_nonce_entity.py

### TestNonceEntity

1. `test_create_valid_nonce_entity`
   - Использует: `sample_nonce_entity`
   - Проверяет: создание успешно

2. `test_nonce_entity_create_generates_uuid`
   - Вызывает `NonceEntity.create()`
   - Проверяет: UUID сгенерирован

3. `test_nonce_entity_create_sets_default_values`
   - Вызывает `NonceEntity.create()` с минимальными параметрами
   - Проверяет: domain="cryptoalrt.io", uri по умолчанию, version="1"

4. `test_nonce_entity_create_sets_expiration_time`
   - Вызывает `NonceEntity.create()` с ttl_time
   - Проверяет: expiration_time = issued_at + ttl_time минут

5. `test_nonce_entity_invalid_nonce_type_raises_error`
   - Создает NonceEntity с невалидным типом nonce
   - Ожидает: `NonceValidationError`

6. `test_nonce_entity_invalid_wallet_address_type_raises_error`
   - Создает NonceEntity с невалидным типом wallet_address
   - Ожидает: `InvalidWalletAddressError`

7. `test_nonce_entity_invalid_statement_type_raises_error`
   - Создает NonceEntity с statement не-строкой
   - Ожидает: `DomainError`

8. `test_nonce_entity_invalid_date_range_raises_error`
   - Создает NonceEntity с issued_at >= expiration_time
   - Ожидает: `DateValidationError`

9. `test_nonce_entity_is_expired_returns_false_for_valid_nonce`
   - Использует: `sample_nonce_entity` (не истекший)
   - Проверяет: `is_expired()` возвращает False

10. `test_nonce_entity_is_expired_returns_true_for_expired_nonce`
    - Создает истекший NonceEntity (expiration_time в прошлом)
    - Проверяет: `is_expired()` возвращает True

11. `test_nonce_entity_is_used_returns_false_for_unused_nonce`
    - Использует: `sample_nonce_entity` (не использованный)
    - Проверяет: `is_used()` возвращает False

12. `test_nonce_entity_is_used_returns_true_for_used_nonce`
    - Создает использованный NonceEntity (used_at не None)
    - Проверяет: `is_used()` возвращает True

13. `test_nonce_entity_mark_as_used_sets_used_at`
    - Использует: `sample_nonce_entity`
    - Вызывает `mark_as_used()`
    - Проверяет: used_at установлен

14. `test_nonce_entity_mark_as_used_returns_new_instance`
    - Использует: `sample_nonce_entity`
    - Вызывает `mark_as_used()`
    - Проверяет: возвращается новый экземпляр (immutability)

15. `test_nonce_entity_mark_as_used_preserves_other_fields`
    - Использует: `sample_nonce_entity`
    - Вызывает `mark_as_used()`
    - Проверяет: остальные поля не изменились

16. `test_nonce_entity_mark_as_used_already_used_raises_error`
    - Создает уже использованный NonceEntity
    - Вызывает `mark_as_used()`
    - Ожидает: `NonceAlreadyUsedError`

17. `test_nonce_entity_convert_to_message_vo_creates_valid_message`
    - Использует: `sample_nonce_entity`
    - Вызывает `convert_to_message_vo()`
    - Проверяет: создается валидный MessageVO

18. `test_nonce_entity_convert_to_message_vo_preserves_all_fields`
    - Использует: `sample_nonce_entity`
    - Вызывает `convert_to_message_vo()`
    - Проверяет: все поля из entity сохранены в MessageVO

---

## 7. test_wallet_logged_in_event.py

### TestWalletLoggedInEvent

1. `test_create_valid_wallet_logged_in_event`
   - Использует: `sample_wallet_logged_in_event`
   - Проверяет: создание успешно

2. `test_wallet_logged_in_event_default_values`
   - Создает WalletLoggedInEvent напрямую
   - Проверяет: source="SIWS", device_id и logged_in установлены

3. `test_wallet_logged_in_event_create_event_generates_uuid`
   - Вызывает `create_event()`
   - Проверяет: event_id сгенерирован (UUID v4)

4. `test_wallet_logged_in_event_create_event_sets_current_time`
   - Вызывает `create_event()`
   - Проверяет: logged_in установлен на текущее время

5. `test_wallet_logged_in_event_create_event_with_device_id`
   - Вызывает `create_event()` с указанным device_id
   - Проверяет: device_id используется переданный

6. `test_wallet_logged_in_event_create_event_without_device_id`
   - Вызывает `create_event()` без device_id
   - Проверяет: device_id = getnode()

7. `test_wallet_logged_in_event_create_event_sets_source_to_siws`
   - Вызывает `create_event()`
   - Проверяет: source="SIWS"

8. `test_wallet_logged_in_event_create_event_uses_provided_wallet_address`
   - Вызывает `create_event()` с wallet_address
   - Проверяет: wallet_address используется переданный

9. `test_wallet_logged_in_event_create_event_with_wallet_vo_value_raises_error`
   - **ПРОБЛЕМА**: в фикстуре передается `sample_wallet_vo.value` вместо `sample_wallet_vo`
   - Если исправлено: тест не нужен
   - Если не исправлено: тест должен проверить, что передача строки вызывает ошибку

---

## Итого: ~60 тестов

### Приоритет:
1. **Высокий**: Валидация (ошибки при невалидных данных)
2. **Средний**: Factory методы (create, generate, from_string)
3. **Средний**: Бизнес-логика (ping, mark_as_used, is_expired, is_used)
4. **Низкий**: Конвертация (to_bytes, to_string, convert_to_message_vo)

### Замечания:
1. В фикстуре `sample_nonce_entity` опечатка: `wallet_adress` → `wallet_address`
2. В фикстуре `sample_wallet_logged_in_event` передается `sample_wallet_vo.value` вместо `sample_wallet_vo`
3. Метод `MessageVO.from_record()` принимает `NonceVO`, но должен принимать `NonceEntity` (судя по коду)
