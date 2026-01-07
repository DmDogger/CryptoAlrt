### Microservices Overview

| Service Name | Description | Status | Quality |
| :--- | :--- | :--- | :--- |
| **price_tracking_service** | Monitors cryptocurrency prices and manages alerts. Triggers notifications once a threshold is reached. | ![Active](https://img.shields.io/badge/Status-Active-brightgreen) | ![Pylint](https://img.shields.io/badge/PyLint-10.0-brightgreen) ![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen) |
| **notification_service** | Centralized notification delivery. Supports **Email**; **Telegram** is on the roadmap. | ![Active](https://img.shields.io/badge/Status-Active-brightgreen) | ![Pylint](https://img.shields.io/badge/PyLint-9.8-brightgreen) ![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen) |
| **siws_login_service** | Authentication based on **SIWS**. Verifies ed25519 signatures and issues JWTs. | ![Active](https://img.shields.io/badge/Status-Active-brightgreen) | ![Pylint](https://img.shields.io/badge/PyLint-10.0-brightgreen) ![Coverage](https://img.shields.io/badge/Coverage-98%25-brightgreen) |
| **portfolio_tracker** | Asset management and analytics service for tracking user holdings. | ![In Development](https://img.shields.io/badge/Status-In_Development-orange) | ![Pylint](https://img.shields.io/badge/PyLint-N/A-grey) ![Coverage](https://img.shields.io/badge/Coverage-N/A-grey) |
