# 📦 SmartStock - Sales & Inventory Management
### Integrated with AI WhatsApp Assistant

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/mit)
[![Python](https://img.shields.io/badge/Python-3.10-green)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092e20)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## 🌟 Features
- **Real-time Inventory tracking**: Products, categories, and stock management.
- **Sales & Purchase workflows**: Detailed billing and supply chain management.
- **🤖 AI WhatsApp Chatbot**:
  - Get instant sales summaries & analytics via WhatsApp.
  - Interactive purchase order creation using natural language.
  - Track customer loyalty and debts.
- **Fully Dockerized**: Easy setup with Docker Compose profiles.
- **Security**: Built-in protection for sensitive data and session management.

---

## 🚀 Quick Start (with Docker)

### 1. Configure the environment
```bash
cp .env.example .env
```

### 2. Start the services
SmartStock uses Docker Profiles for flexibility:

*   **Standard (App + Database):**
    ```bash
    docker compose --profile sales up -d
    ```
*   **Full Integration (App + Database + WhatsApp API):**
    ```bash
    docker compose --profile sales --profile wppconnect up -d
    ```

### 3. Access
- **Web App**: [http://localhost:8000](http://localhost:8000)
- **WhatsApp API**: [http://localhost:21465](http://localhost:21465)

---

## 📸 Screenshots

### 🤖 AI WhatsApp Assistant
| Sales Stats | Analytics |
| :---: | :---: |
| ![Sales Stats](docs/screenshots/whatsapp_sales_stats.png) | ![Analytics](docs/screenshots/whatsapp_analytics.png) |

**AI Purchase Order Flow**
![Purchase Flow](docs/screenshots/whatsapp_purchase_flow.png)

### 🏢 Web Management Dashboard
<details>
<summary>Click to expand system screenshots</summary>

#### 🔗 Integration Management
Showcasing the WPPConnect session and configuration.
![Integration](docs/screenshots/app_detail.png)

#### 💬 Conversations Logging
Track all messages sent and received via the AI bot.
![Conversations](docs/screenshots/conversations_list.png)

#### ⚙️ Configuration
Securely manage API tokens and connection settings.
![Config](docs/screenshots/config_update.png)

#### 📊 Dashboard Preview
![Inventory](https://github.com/user-attachments/assets/5b176c44-82dd-4080-8259-0976029a496f)
</details>

---

## 🛠 Manual Installation
<details>
<summary>View manual setup steps</summary>

1. **Install Python 3.10+ and PostgreSQL.**
2. **Setup venv**: `python -m venv venv && source venv/bin/activate`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Migrate**: `python manage.py migrate`
5. **Run**: `python manage.py runserver`
</details>

## 👥 Authors
- [Stephen Murichu](https://github.com/munuhee) - Original Creator
- [Zaid Al-Melahi](https://github.com/zaalmelahi) - Integration & Dockerization

---
Happy coding! 🚀
