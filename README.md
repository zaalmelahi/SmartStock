# 📦 SmartStock
### Sales and Inventory Management System

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/mit)
[![Python Version](https://img.shields.io/badge/Python-3.10-green)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)

## 📝 Description
**SmartStock** is a comprehensive solution for managing business operations with a focus on user experience and modern technologies. It features robust inventory tracking, vendor/customer management, billing, invoicing, and real-time WhatsApp integration via WPPConnect.

## 🚀 Quick Start (with Docker)

The easiest way to get started is using Docker Compose.

### 1. Clone the Repository
```bash
git clone https://github.com/zaalmelahi/SmartStock.git
cd SmartStock
```

### 2. Configure Environment
Copy the example environment file and update the variables if necessary:
```bash
cp .env.example .env
```

### 3. Run with Docker Compose
SmartStock uses **Docker Profiles** to manage services efficiently:

*   **Standard (Web + DB):**
    ```bash
    docker compose --profile sales up -d
    ```
*   **Full Suite (Web + DB + WhatsApp Bot):**
    ```bash
    docker compose --profile sales --profile wppconnect up -d
    ```
*   **Admin Tools (PgAdmin):**
    ```bash
    docker compose --profile admin up -d
    ```

### 4. Access the Application
- **Web App:** [http://localhost:8000](http://localhost:8000)
- **PgAdmin:** [http://localhost:5052](http://localhost:5052)
- **WhatsApp API:** [http://localhost:21465](http://localhost:21465)

## 🛠 Manual Installation (Without Docker)

<details>
<summary>Click to view manual setup steps</summary>

### Prerequisites
- Python 3.10+
- PostgreSQL

### Steps
1. **Set Up Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Linux
    # or
    venv\Scripts\activate # Windows
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Database & Migrations**
    Configure your `.env` with local DB credentials, then:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
</details>

## 📸 Screenshots

<details>
  <summary>Click to view screenshots</summary>

  ![screenshot_1](https://github.com/user-attachments/assets/9bb2f5f9-d456-4681-b5de-8d82a3ef97d8)
  ![screenshot_2](https://github.com/user-attachments/assets/d6e14ba3-8827-41c1-9cdb-8f24add83f4d)
  ![screenshot_3](https://github.com/user-attachments/assets/6be5060e-974b-4289-bcdf-b852771833f8)
  ![screenshot_4](https://github.com/user-attachments/assets/5b176c44-82dd-4080-8259-0976029a496f)

</details>

## 👥 Author
- [Zaid Al-Melahi](https://github.com/zaalmelahi) - Integration & Dockerization

---
Happy coding! 🚀
