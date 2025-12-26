# Domain Layer Documentation

This document provides comprehensive documentation for all entities, value objects, and their methods in the SIWE (Sign-In With Ethereum) authentication service domain layer.

---

## Table of Contents

1. [Entities](#entities)
   - [WalletEntity](#walletentity)
   - [NonceEntity](#nonceentity)
2. [Value Objects](#value-objects)
   - [WalletAddressVO](#walletaddressvo)
   - [NonceVO](#noncevo)
   - [SignatureVO](#signaturevo)
   - [MessageVO](#messagevo)
3. [Exceptions](#exceptions)

---

## Entities

### WalletEntity

**File**: `src/domain/entities/wallet_entity.py`

**Description**: Entity representing a wallet in the SIWE authentication system. This entity encapsulates wallet information including the unique identifier, wallet address, and timestamps for tracking activity and creation time. The entity is immutable (frozen) to ensure data integrity.

**Attributes**:
- `uuid: UUID` - Unique identifier for the wallet entity
- `wallet_address: WalletAddressVO` - The wallet address as a WalletAddressVO value object
- `last_active: datetime` - Timestamp of the last activity/authentication for this wallet
- `created_at: datetime` - Timestamp when the wallet entity was first created

#### Methods

##### `__post_init__(self) -> None`

Validates the wallet entity fields during initialization.

**Validation Rules**:
- Ensures `wallet_address` is a valid `WalletAddressVO` instance
- Ensures `created_at` timestamp is not in the future

**Raises**:
- `InvalidWalletAddressError`: If `wallet_address` is not a `WalletAddressVO` instance
- `DateValidationError`: If `created_at` is in the future (greater than or equal to current time)

**Example**:
```python
wallet = WalletEntity(
    uuid=UUID("..."),
    wallet_address=WalletAddressVO(value="..."),
    last_active=datetime.now(UTC),
    created_at=datetime.now(UTC)
)
```

---

##### `ping(self) -> WalletEntity`

Updates the `last_active` timestamp to the current time. Since the entity is immutable (frozen dataclass), this method returns a new `WalletEntity` instance with the `last_active` field set to the current time. This is used to track when a wallet was last used for authentication.

**Returns**: A new `WalletEntity` instance with `last_active` set to the current timestamp

**Example**:
```python
updated_wallet = wallet.ping()
# updated_wallet.last_active is now datetime.now(UTC)
```

---

##### `to_bytes(self) -> bytes`

Converts the wallet address to its byte representation. Decodes the base58-encoded wallet address string into bytes. This is useful for cryptographic operations and signature verification.

**Returns**: The wallet address as bytes (32 bytes for Solana addresses)

**Raises**:
- `InvalidWalletAddressError`: If the wallet address cannot be decoded from base58

**Example**:
```python
wallet_bytes = wallet.to_bytes()
# Returns 32-byte representation of the wallet address
```

---

### NonceEntity

**File**: `src/domain/entities/nonce_entity.py`

**Description**: Entity representing a nonce record for SIWE authentication. This entity encapsulates all the information needed for a SIWE authentication session, including the nonce value, wallet address, domain, and timing information. It tracks whether the nonce has been used and whether it has expired.

**Attributes**:
- `uuid: UUID` - Unique identifier for the nonce record
- `wallet_address: WalletAddressVO` - Solana address performing the signing
- `nonce: NonceVO` - Randomized token used to prevent replay attacks, at least 8 alphanumeric characters
- `domain: str` - RFC 4501 DNS authority that is requesting the signing
- `statement: str | None` - Human-readable ASCII assertion that the user will sign, must not contain newline characters
- `uri: str` - RFC 3986 URI referring to the resource that is the subject of the signing
- `version: str | None` - Current version of the message
- `expiration_time: datetime` - ISO 8601 datetime string indicating when the signed message expires
- `used_at: datetime | None` - Timestamp when the nonce was used, None if not yet used (default: None)
- `issued_at: datetime` - ISO 8601 datetime string of the current time when the message was issued (default: current time)
- `chain_id: str` - Chain ID to which the session is bound, and the network where Contract Accounts must be resolved (default: "mainnet-beta")

#### Methods

##### `__post_init__(self) -> None`

Validates the nonce entity fields during initialization.

**Validation Rules**:
- Ensures `nonce` is a valid `NonceVO` instance
- Ensures `wallet_address` is a valid `WalletAddressVO` instance
- Ensures `issued_at` time is before `expiration_time`

**Raises**:
- `NonceValidationError`: If the nonce is not a valid `NonceVO` instance
- `InvalidWalletAddressError`: If the wallet address is not a valid `WalletAddressVO` instance
- `DateValidationError`: If `issued_at` is greater than or equal to `expiration_time`

---

##### `is_expired(self) -> bool`

Checks if the nonce has expired by comparing the current time with the expiration time.

**Returns**: `True` if the current time is greater than or equal to the expiration time, `False` otherwise

**Example**:
```python
if nonce.is_expired():
    raise NonceExpiredError("Nonce has expired")
```

---

##### `is_used(self) -> bool`

Checks if the nonce has been used by checking if `used_at` is not None.

**Returns**: `True` if the nonce has been marked as used (`used_at` is not None), `False` otherwise

**Example**:
```python
if nonce.is_used():
    raise NonceAlreadyUserError("Nonce has already been used")
```

---

##### `convert_to_message_vo(self) -> MessageVO`

Converts the nonce entity to a `MessageVO` value object. Creates a `MessageVO` instance from the nonce entity's data, which can be used for generating the message string that users will sign.

**Returns**: A `MessageVO` instance containing all the message data from this entity

**Example**:
```python
message_vo = nonce.convert_to_message_vo()
message_string = message_vo.to_string()
```

---

##### `mark_as_used(self) -> NonceEntity`

Marks the nonce as used by creating a new entity with `used_at` timestamp. Since the entity is immutable (frozen dataclass), this method returns a new `NonceEntity` instance with the `used_at` field set to the current time.

**Returns**: A new `NonceEntity` instance with `used_at` set to the current timestamp

**Example**:
```python
used_nonce = nonce.mark_as_used()
# used_nonce.used_at is now datetime.now(UTC)
```

---

## Value Objects

### WalletAddressVO

**File**: `src/domain/value_objects/wallet_vo.py`

**Description**: Value object representing a wallet address. Validates that the wallet address is a valid base58-encoded string with a decoded length of 32 bytes (standard Solana address length).

**Attributes**:
- `value: str` - The wallet address as a base58-encoded string

#### Methods

##### `__post_init__(self) -> None`

Validates that the wallet address decodes to exactly 32 bytes.

**Validation Rules**:
- The base58-decoded address must be exactly 32 bytes long

**Raises**:
- `InvalidWalletAddressError`: If the decoded address length is not 32 bytes

**Example**:
```python
wallet_address = WalletAddressVO(value="Base58EncodedAddress...")
```

---

##### `to_bytes(value: str) -> bytes` (static method)

Converts a base58-encoded wallet address to bytes.

**Parameters**:
- `value: str` - The base58-encoded wallet address string

**Returns**: The decoded wallet address as bytes (32 bytes)

**Example**:
```python
bytes_repr = WalletAddressVO.to_bytes("Base58EncodedAddress...")
```

---

### NonceVO

**File**: `src/domain/value_objects/nonce_vo.py`

**Description**: Value object representing a nonce for SIWE authentication. A nonce is a randomized token used to prevent replay attacks in authentication. The nonce must be at least 8 alphanumeric characters long as per SIWE specification.

**Attributes**:
- `value: str` - The nonce string value, must be at least 8 characters long

#### Methods

##### `__post_init__(self) -> None`

Validates that the nonce value meets the minimum length requirement.

**Validation Rules**:
- The nonce must not be empty
- The nonce must have at least 8 characters (SIWE specification requirement)

**Raises**:
- `NonceValidationError`: If the nonce is empty or shorter than 8 characters

**Example**:
```python
nonce = NonceVO(value="atleast8chars")
```

---

##### `generate(cls) -> NonceVO` (class method)

Generates a new random nonce value. Creates a new `NonceVO` instance with a randomly generated UUID hex string, which provides a cryptographically secure nonce value.

**Returns**: A new `NonceVO` instance with a randomly generated nonce value

**Example**:
```python
nonce = NonceVO.generate()
# Creates a nonce with a random UUID hex string (32 characters)
```

---

### SignatureVO

**File**: `src/domain/value_objects/signature_vo.py`

**Description**: Value object representing a cryptographic signature. Validates that the signature is a valid base58-encoded string with a decoded length of 64 bytes (512 bits), which is the standard length for Ed25519 signatures used in Solana.

**Attributes**:
- `value: str` - The signature as a base58-encoded string

#### Methods

##### `__post_init__(self) -> None`

Validates that the signature decodes to exactly 64 bytes.

**Validation Rules**:
- The base58-decoded signature must be exactly 64 bytes long (Ed25519 signature length)

**Raises**:
- `SignatureValidationError`: If the decoded signature length is not 64 bytes

**Example**:
```python
signature = SignatureVO(value="Base58EncodedSignature...")
```

---

##### `to_bytes(value: str) -> bytes` (static method)

Converts a base58-encoded signature to bytes.

**Parameters**:
- `value: str` - The base58-encoded signature string

**Returns**: The decoded signature as bytes (64 bytes)

**Example**:
```python
bytes_repr = SignatureVO.to_bytes("Base58EncodedSignature...")
```

---

### MessageVO

**File**: `src/domain/value_objects/message_vo.py`

**Description**: Value object representing a SIWE (Sign-In With Ethereum) message for Solana. This class encapsulates all the fields required for a SIWE authentication message, following the SIWE specification adapted for Solana blockchain.

**Attributes**:
- `wallet_address: WalletAddressVO` - Solana address performing the signing
- `domain: str` - RFC 4501 DNS authority that is requesting the signing
- `statement: str | None` - Human-readable ASCII assertion that the user will sign, must not contain newline characters
- `uri: str` - RFC 3986 URI referring to the resource that is the subject of the signing
- `version: str | None` - Current version of the message
- `nonce: NonceVO` - Randomized token used to prevent replay attacks, at least 8 alphanumeric characters
- `expiration_time: datetime` - ISO 8601 datetime string indicating when the signed message expires
- `issued_at: datetime` - ISO 8601 datetime string of the current time when the message was issued (default: current time)
- `chain_id: str` - Chain ID to which the session is bound, and the network where Contract Accounts must be resolved (default: "mainnet-beta")

#### Methods

##### `__post_init__(self) -> None`

Validates that the `issued_at` time is before the `expiration_time`.

**Validation Rules**:
- Ensures `issued_at` is strictly before `expiration_time`
- Ensures `wallet_address` is a valid `WalletAddressVO` instance

**Raises**:
- `DateValidationError`: If `issued_at` is greater than or equal to `expiration_time`
- `InvalidWalletAddressError`: If `wallet_address` is not a `WalletAddressVO` instance

**Example**:
```python
message = MessageVO(
    wallet_address=WalletAddressVO(value="..."),
    domain="example.com",
    statement="Please sign in",
    uri="https://example.com",
    version="1",
    nonce=NonceVO(value="..."),
    expiration_time=datetime.now(UTC) + timedelta(hours=1),
    issued_at=datetime.now(UTC)
)
```

---

##### `from_record(cls, record: NonceVO) -> MessageVO` (class method)

Creates a `MessageVO` instance from a `NonceVO` record. **Note**: This method signature appears to be incorrect in the current implementation - it should accept a `NonceEntity` instead of `NonceVO`.

**Parameters**:
- `record: NonceVO` - The NonceVO record containing message data (Note: implementation may expect NonceEntity)

**Returns**: A new `MessageVO` instance constructed from the record data

**Example**:
```python
message = MessageVO.from_record(nonce_entity)
```

---

##### `to_string(self) -> str`

Converts the message to a formatted string representation. Formats the message according to SIWE specification, including all required fields in a human-readable format suitable for user signing.

**Returns**: A formatted string representation of the message ready for signing

**Format**:
```
{domain} wants you to sign in with your Solana account:
{wallet_address}

{statement}

URI: {uri}
Version: {version}
Chain ID: {chain_id}
Nonce: {nonce}
Issued At: {issued_at}
Expiration Time: {expiration_time}
```

**Example**:
```python
message_string = message.to_string()
# User signs this string with their wallet
```

---

## Exceptions

All domain exceptions inherit from `DomainError` base class.

**File**: `src/domain/exceptions.py`

### DomainError

Base exception class for all domain-related errors.

---

### SignatureVerificationFailed

**Inherits from**: `DomainError`

**Description**: Raised when signature verification fails during authentication. This occurs when the cryptographic signature does not match the expected signature for the given message and wallet address.

**Example**:
```python
raise SignatureVerificationFailed("Signature verification failed for wallet address")
```

---

### SignatureValidationError

**Inherits from**: `DomainError`

**Description**: Raised when the signature value fails validation, such as incorrect length or format. This is raised during signature creation/validation, not during verification.

**Example**:
```python
raise SignatureValidationError("Expected signature to decode to 64 bytes, but got 32 bytes")
```

---

### InvalidWalletAddressError

**Inherits from**: `DomainError`

**Description**: Raised when the provided wallet address is invalid or malformed. This can occur when:
- The wallet address is not a valid base58-encoded string
- The decoded address length is not 32 bytes
- The wallet address is not a `WalletAddressVO` instance when expected

**Example**:
```python
raise InvalidWalletAddressError("Expected wallet address to decode to 32 bytes, but got different length")
```

---

### InvalidNonceError

**Inherits from**: `DomainError`

**Description**: Raised when the provided nonce is invalid or does not match the expected format. This is a general nonce validation error.

**Example**:
```python
raise InvalidNonceError("Nonce format is invalid")
```

---

### NonceExpiredError

**Inherits from**: `DomainError`

**Description**: Raised when the nonce has expired and can no longer be used for authentication. This occurs when attempting to use a nonce after its `expiration_time` has passed.

**Example**:
```python
raise NonceExpiredError("Nonce has expired and cannot be used")
```

---

### NonceValidationError

**Inherits from**: `DomainError`

**Description**: Raised when the nonce value fails validation, such as being too short or empty. This is raised during nonce creation when the value does not meet the minimum requirements (at least 8 characters).

**Example**:
```python
raise NonceValidationError("Nonce value must be at least 8 characters long, got 5 characters")
```

---

### NonceAlreadyUserError

**Inherits from**: `DomainError`

**Description**: Raised when the nonce has already been used and cannot be reused. This prevents replay attacks by ensuring each nonce can only be used once.

**Example**:
```python
raise NonceAlreadyUserError("Nonce has already been used and cannot be reused")
```

---

### NonceNotFoundError

**Inherits from**: `DomainError`

**Description**: Raised when the requested nonce is not found in the system. This occurs when attempting to retrieve or use a nonce that does not exist in the repository.

**Example**:
```python
raise NonceNotFoundError("Nonce with UUID {uuid} not found")
```

---

### InvalidSignatureFormat

**Inherits from**: `DomainError`

**Description**: Raised when the signature format is invalid or does not match the expected structure. This is different from `SignatureValidationError` as it focuses on format/structure rather than length.

**Example**:
```python
raise InvalidSignatureFormat("Signature format is invalid")
```

---

### DateValidationError

**Inherits from**: `DomainError`

**Description**: Raised when date/time validation fails, typically when a "time after" is greater than or equal to a "time before". This is used to ensure logical ordering of timestamps (e.g., `issued_at` must be before `expiration_time`, `created_at` cannot be in the future).

**Example**:
```python
raise DateValidationError("issued_at (2024-01-01T12:00:00Z) must be before expiration_time (2024-01-01T11:00:00Z)")
```

---

## Summary

The domain layer provides a robust, type-safe implementation of SIWE authentication for Solana:

- **Entities** (`WalletEntity`, `NonceEntity`) represent core business objects with lifecycle management
- **Value Objects** (`WalletAddressVO`, `NonceVO`, `SignatureVO`, `MessageVO`) encapsulate validated domain concepts
- **Exceptions** provide clear error handling for domain validation failures

All entities and value objects are:
- **Immutable** (frozen dataclasses) to ensure data integrity
- **Validated** through `__post_init__` methods
- **Type-safe** with proper type hints
- **Well-documented** with comprehensive docstrings
