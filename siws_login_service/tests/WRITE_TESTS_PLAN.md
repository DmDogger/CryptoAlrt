# План написания тестов для сущностей и value objects

## Статус тестирования

### ✅ Готово (есть тесты)

#### 1. NonceEntity (`test_nonce_entity.py`)
- ✅ `test_create_valid_nonce_entity` - создание валидной сущности
- ✅ `test_mark_used_works_correct` - метод `mark_as_used()` работает корректно
- ✅ `test_not_marks_as_used_again` - нельзя пометить как использованный дважды
- ✅ `test_datetime_validator_works_correct` - валидация дат (issued_at < expiration_time)
- ✅ `test_is_expired_works_correct` - метод `is_expired()` работает корректно
- ✅ `test_is_used_works_correct` - метод `is_used()` работает корректно

**Отсутствует:**
- ❌ Тест для метода `create()` (фабричный метод)
- ❌ Тест для метода `convert_to_message_vo()`
- ❌ Тест валидации `__post_init__` для невалидного `nonce` (не NonceVO)
- ❌ Тест валидации `__post_init__` для невалидного `wallet_address` (не WalletAddressVO)
- ❌ Тест валидации `__post_init__` для невалидного `statement` (не строка)

#### 2. NonceVO (`test_nonce_vo.py`)
- ✅ `test_create_valid_nonce_vo` - создание валидного VO
- ✅ `test_incorrect_length_nonce` - валидация длины (< 8 символов)
- ✅ `test_nonce_creates_unique_values` - метод `generate()` создает уникальные значения
- ✅ `test_nonce_vo_empty_value_raises_error` - пустое значение вызывает ошибку
- ✅ `test_nonce_vo_generate_creates_valid_nonce` - `generate()` создает валидный nonce
- ✅ `test_nonce_vo_generate_has_minimum_length` - `generate()` создает nonce с длиной >= 8

**Покрытие полное** ✅

#### 3. SignatureVO (`test_signature_vo.py`)
- ✅ `test_create_valid_signature_vo` - создание валидного VO
- ✅ `test_signature_vo_from_string_creates_valid_instance` - фабричный метод `from_string()`
- ✅ `test_correct_signature_to_bytes` - метод `to_bytes()` возвращает 64 байта
- ✅ `test_signature_vo_invalid_length_raises_error` - невалидная длина вызывает ошибку
- ✅ `test_signature_vo_invalid_base58_raises_error` - невалидные символы base58 вызывают ошибку
- ✅ `test_signature_vo_from_string_with_non_string_raises_error` - не-строка вызывает ошибку

**Покрытие полное** ✅

#### 4. WalletAddressVO (`test_wallet_address_vo.py`)
- ✅ `test_create_valid_wallet_address_vo` - создание валидного VO
- ✅ `test_correct_wallet_to_bytes` - метод `to_bytes()` возвращает 32 байта
- ✅ `test_correct_wallet_instance_from_string` - фабричный метод `from_string()`
- ✅ `test_raises_error_from_string_method` - невалидная длина вызывает ошибку
- ✅ `test_raises_error_when_incorrect_alphabet_for_base58` - невалидные символы base58 вызывают ошибку
- ✅ `test_wallet_address_vo_from_string_with_non_string_raises_error` - не-строка вызывает ошибку

**Покрытие полное** ✅

---

### ❌ Не готово (нет тестов)

#### 1. WalletEntity - **НЕТ ТЕСТОВ**

**Методы для тестирования:**

1. **`__post_init__()`** - валидация при создании
   - ✅ Валидный `wallet_address` (WalletAddressVO)
   - ❌ Невалидный `wallet_address` (не WalletAddressVO) → `InvalidWalletAddressError`
   - ❌ `created_at` в будущем → `DateValidationError`

2. **`create()`** - фабричный метод
   - ✅ Создание с валидным `wallet_address`
   - ✅ Автоматическая генерация UUID
   - ✅ Установка `last_active` и `created_at` в текущее время

3. **`ping()`** - обновление `last_active`
   - ✅ Обновление `last_active` на текущее время
   - ✅ Возвращает новый экземпляр (immutable)
   - ✅ Сохраняет остальные поля без изменений

4. **`to_bytes()`** - конвертация в байты
   - ✅ Возвращает 32 байта
   - ✅ Корректная декодировка base58
   - ❌ Ошибка при невалидном base58 → `InvalidWalletAddressError`

#### 2. MessageVO - **НЕТ ТЕСТОВ**

**Методы для тестирования:**

1. **`__post_init__()`** - валидация при создании
   - ✅ Валидный `wallet_address` (WalletAddressVO)
   - ❌ Невалидный `wallet_address` (не WalletAddressVO) → `InvalidWalletAddressError`
   - ❌ `issued_at >= expiration_time` → `DateValidationError`

2. **`from_record()`** - фабричный метод (принимает NonceVO, но по документации должен принимать NonceEntity)
   - ⚠️ **Проблема**: Метод принимает `NonceVO`, но по логике должен принимать `NonceEntity`
   - Нужно проверить текущую реализацию и возможно исправить

3. **`to_string()`** - конвертация в строку для подписи
   - ✅ Корректное форматирование всех полей
   - ✅ Обработка `statement` (если None, то не включается)
   - ✅ Форматирование дат в ISO 8601
   - ✅ Все обязательные поля присутствуют

---

## План действий

### Приоритет 1: WalletEntity
1. Создать файл `test_wallet_entity.py`
2. Написать тесты для `__post_init__()` (валидация)
3. Написать тесты для `create()` (фабричный метод)
4. Написать тесты для `ping()` (обновление активности)
5. Написать тесты для `to_bytes()` (конвертация)

### Приоритет 2: MessageVO
1. Создать файл `test_message_vo.py`
2. Написать тесты для `__post_init__()` (валидация)
3. Написать тесты для `from_record()` (проверить сигнатуру метода)
4. Написать тесты для `to_string()` (форматирование сообщения)

### Приоритет 3: Дополнительные тесты для NonceEntity
1. Тест для метода `create()` (фабричный метод)
2. Тест для метода `convert_to_message_vo()`
3. Дополнительные тесты валидации в `__post_init__()`

---

## Итого

- **Готово**: 4 из 6 (NonceVO, SignatureVO, WalletAddressVO - полностью; NonceEntity - частично)
- **Не готово**: 2 из 6 (WalletEntity, MessageVO)
- **Частично готово**: NonceEntity (не хватает нескольких тестов)
