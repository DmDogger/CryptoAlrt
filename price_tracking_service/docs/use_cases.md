## CrptoAlrt Overview (Microservice: Alert)

**Microservice overviews:**

As a component of the CryptoAlrt system, the Alerts Microservice automatically retrieves real-time cryptocurrency data from the Coingecko API. It allows users to set personalized alerts and immediately broadcasts updates via a message broker.

This microservice is responsible for:
- **Fetching cryptocurrency prices** from CoinGecko
- **Storing historical prices** in the database
- **Publishing price update events** to the message broker (Kafka)
- **Managing price alerts** (create / update / delete / list)
- **Checking alert thresholds** and publishing “alert triggered” events

Core domain entities:
- **CryptocurrencyEntity**: cryptocurrency (symbol, name, coingecko_id)
- **AlertEntity**: price alert (email, cryptocurrency, threshold_price, is_active, is_triggered)

Main broker topics:
- **`price_updates_topic`**: events about cryptocurrency price updates
- **`alert_created_topic`**: events about created price-change alerts (relative alerts)
- **`alert_triggered_topic`**: events about triggered price alerts (absolute thresholds)

---

## Use Cases Summary

| Use Case Class                               | Responsibility                                                |
|---------------------------------------------|----------------------------------------------------------------|
| `FetchAndSaveUseCase`                       | Fetch price from CoinGecko and save it to DB                  |
| `PublishPriceUpdateToBrokerUseCase`         | Publish “price updated” event to Kafka                        |
| `PublishAlertPriceChangedToBrokerUseCase`   | Publish relative price-change alert creation event            |
| `ProcessPriceUpdateUseCase`                 | Orchestrate full price update workflow                        |
| `SaveAlertToDBUseCase`                      | Create and persist fixed-threshold alert in DB                |
| `GetAlertsUseCase`                          | Get active, not triggered alerts by user email                |
| `UpdateAlertUseCase`                        | Partially update alert and publish update events              |
| `DeleteAlertUseCase`                        | Delete user’s alert by ID (with ownership check)              |
| `CheckThresholdUseCase`                     | Check thresholds, publish “alert triggered” and mark as used  |

---


### I. Use Case: Fetch and save

**File**: `src/application/use_cases/fetch_and_save_to_database.py`  
**Class**: `FetchAndSaveUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `coin_id: str` (CoinGecko ID, e.g. `"bitcoin"`)                             |
| Output      | `(CryptocurrencyEntity, Decimal)` (entity + current USD price)             |
| Side Effects| Creates cryptocurrency if missing; inserts price record into DB             |
| Errors      | `UnsuccessfullyCoinGeckoAPICall`, `UnexpectedError`                         |

Main steps:
- Fetch price via **CoinGeckoClientProtocol.fetch_price**.
- Find cryptocurrency by symbol, or create a new one.
- Save price via **CryptocurrencyRepository.save_price**.
- Return the entity and current price.

---

### II. Use Case: Publish price updated to broker

**File**: `src/application/use_cases/publish_price_update_to_broker.py`  
**Class**: `PublishPriceUpdateToBrokerUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `cryptocurrency_id: UUID`, `new_price: Decimal`                             |
| Output      | `None`                                                                      |
| Side Effects| Sends event to Kafka topic `price_updates_topic`                            |
| Errors      | `CryptocurrencyNotFound`, `PublishError`                                    |

---

### III. Use Case: Publish alert "Price changed" to broker

**File**: `src/application/use_cases/publish_alert_price_changed_to_broker.py`  
**Class**: `PublishAlertPriceChangedToBrokerUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `cryptocurrency_id: UUID`, `user_email: str`, `new_price: Decimal`, `threshold_percent: Decimal`, `threshold_price: Decimal` |
| Output      | `None`                                                                      |
| Side Effects| Publishes relative price-change alert to topic `alert_created_topic`        |
| Errors      | `CryptocurrencyNotFound`, `PublishError`                                    |

---

### IV: Main Use Case: Process update (The orchestrator)

**File**: `src/application/use_cases/process_price_update.py`  
**Class**: `ProcessPriceUpdateUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `coin_id: str`                                                              |
| Output      | `(CryptocurrencyEntity, Decimal)`                                           |
| Side Effects| DB writes, event publishing to Kafka, alert checking                        |
| Errors      | `UnsuccessfullyCoinGeckoAPICall`, `RepositoryError`, `PublishError`, `UnexpectedError` |

Internally orchestrates:
- **FetchAndSaveUseCase**
- **PublishPriceUpdateToBrokerUseCase**
- **CheckThresholdUseCase**

---

### V: Use Case: Save alert to database

**File**: `src/application/use_cases/save_alert_to_database.py`  
**Class**: `SaveAlertToDBUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `alert_pydantic: AlertCreateRequest`                                        |
| Output      | `None`                                                                      |
| Side Effects| Inserts a new `Alert` record into DB                                        |
| Errors      | `CryptocurrencyNotFound`, `AlertSavingError`                                |

---

### VI: Use Case: Get alerts

**File**: `src/application/use_cases/get_alerts_list_by_email.py`  
**Class**: `GetAlertsUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `email: str`                                                                |
| Output      | `list[AlertEntity]`                                                         |
| Filters     | `is_active == True`, `is_triggered == False` (in repository)               |
| Errors      | `RepositoryError`, `ValueError`                                             |

---

### VII: Use Case: 

**File**: `src/application/use_cases/update_alert.py`  
**Class**: `UpdateAlertUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `alert_to_update: AlertUpdateRequest`, `alert_id: UUID`                     |
| Output      | `AlertEntity` (updated)                                                    |
| Side Effects| DB update, publish `AlertUpdatedEvent` to Kafka                             |
| Special     | When `threshold_price` changes, `is_triggered` is reset to `False`          |
| Errors      | `AlertNotFound`, `RepositoryError`, `DomainValidationError`                 |

---

### VIII: Use Case: Delete alert

**File**: `src/application/use_cases/delete_alert.py`  
**Class**: `DeleteAlertUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `alert_id: UUID`, `email: str`                                              |
| Output      | `None`                                                                      |
| Side Effects| Deletes alert from DB if it belongs to the given email                      |
| Errors      | `AlertNotFound`, DB-related exceptions                                      |

---

### IX: Use Case: Check threshold

**File**: `src/application/use_cases/check_threshold.py`  
**Class**: `CheckThresholdUseCase`

| Aspect       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Input       | `cryptocurrency: str`, `current_price: Decimal`                             |
| Output      | `None`                                                                      |
| Filters     | Only alerts with `is_active == True` and `is_triggered == False`            |
| Side Effects| Publishes `ThresholdTriggeredEvent` to Kafka, sets `is_triggered=True` in DB|
| Errors      | `RepositoryError`, `PublishError`                                           |

---

## Database Schema

You can place this into a separate file like `docs/schema.md` if you prefer.

### Tables Overview

| Table Name            | Model Class             | Description                        |
|-----------------------|-------------------------|------------------------------------|
| `cryptocurrency`      | `Cryptocurrency`        | Base cryptocurrency metadata       |
| `cryptocurrency_price`| `CryptocurrencyPrice`   | Historical price snapshots         |
| `alerts`              | `Alert`                 | User price alerts                  |

---

### Table: `cryptocurrency`

**Model**: `src/infrastructures/database/models/cryptocurrency.py` → `Cryptocurrency`

| Column        | Type                      | Constraints                                  | Description                    |
|---------------|---------------------------|----------------------------------------------|--------------------------------|
| `id`          | `UUID`                    | PK, unique, not null, default `uuid4()`      | Internal identifier            |
| `symbol`      | `String(100)`             | unique, not null                             | Symbol, e.g. `BTC`             |
| `name`        | `String(10)`              | unique, not null                             | Human-readable name            |
| `created_at`  | `DateTime`                | not null, default `now()`                    | Creation timestamp             |
| `coingecko_id`| `String(20)`              | not null                                     | CoinGecko ID (`bitcoin`, …)    |

Relations:
- `alerts`: one-to-many → `Alert`
- `price_history`: one-to-many → `CryptocurrencyPrice`

---

### Table: `cryptocurrency_price`

**Model**: `CryptocurrencyPrice`

| Column                        | Type                 | Constraints                                  | Description                           |
|-------------------------------|----------------------|----------------------------------------------|---------------------------------------|
| `id`                          | `UUID`              | PK, not null, `server_default=now()`         | Price record ID                        |
| `cryptocurrency_id`           | `UUID`              | FK → `cryptocurrency.id`                     | Linked cryptocurrency                  |
| `price_usd`                   | `Numeric(10,2)`     | not null                                     | Price in USD                           |
| `last_updated`                | `DateTime`          | default `now()`                              | Timestamp of this price                |
| `market_cap_usd`              | `Numeric(30,2)`     | nullable                                     | Market cap in USD                      |
| `total_volume_24h_usd`        | `Numeric(30,2)`     | nullable                                     | 24h volume in USD                      |
| `high_24h`                    | `Numeric(30,2)`     | nullable                                     | 24h high                               |
| `low_24h`                     | `Numeric(30,2)`     | nullable                                     | 24h low                                |
| `price_change_24h`            | `Numeric(20,8)`     | nullable                                     | 24h price change (absolute)            |
| `price_change_percentage_24h` | `Numeric(10,4)`     | nullable                                     | 24h price change percentage            |

Relation:
- `cryptocurrency`: many-to-one → `Cryptocurrency`

---

### Table: `alerts`

**Model**: `src/infrastructures/database/models/alert.py` → `Alert`

| Column           | Type                 | Constraints                                  | Description                                      |
|------------------|----------------------|----------------------------------------------|--------------------------------------------------|
| `id`             | `UUID`              | PK, unique, not null, default `uuid4()`      | Alert ID                                         |
| `email`          | `String(100)`       | not null                                     | User email                                       |
| `cryptocurrency_id` | `UUID`           | FK → `cryptocurrency.id`, not null           | Target cryptocurrency                            |
| `threshold_price`| `Numeric(10,2)`     | not null                                     | Alert threshold in USD                           |
| `is_triggered`   | `Boolean`           | nullable (migration), default `False`        | Has this alert already been triggered?           |
| `is_active`      | `Boolean`           | not null, default `True`                     | Is alert currently active                        |
| `created_at`     | `DateTime(tz=True)` | not null, default `now()`                    | Creation timestamp                               |

Relation:
- `cryptocurrency`: many-to-one → `Cryptocurrency`

Alert behavior:
- New alerts are created with `is_triggered = False`.
- When a threshold is reached and event is published, alert is updated to `is_triggered = True`.
- When `threshold_price` is changed via `UpdateAlertUseCase`, `is_triggered` is reset to `False`.
