# 📦 SmartStock
### Sales and Inventory Management System

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/mit)
[![Python Version](https://img.shields.io/badge/Python-3.10-green)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)

## 🌟 Features
- **Real-time Inventory Tracking**: Manage products, categories, and stock levels.
- **Sales & Purchase Management**: Easy-to-use interfaces for billing and purchasing.
- **AI-Powered WhatsApp Bot**: 
  - Get instant sales summaries.
  - Check debt and top customers.
  - Create purchase orders via natural language.
- **PgAdmin Integration**: Direct database management via a secure UI.
- **Fully Dockerized**: Deployment-ready with Docker Compose profiles.

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

### 4. Access the Application
- **Web App:** [http://localhost:8000](http://localhost:8000)
- **WhatsApp API:** [http://localhost:21465](http://localhost:21465)

## � Screenshots

### 🤖 AI WhatsApp Assistant
<div align="center">
  <img src="docs/screenshots/whatsapp_sales_stats.png" alt="Sales Stats" width="45%" />
  <img src="docs/screenshots/whatsapp_analytics.png" alt="Analytics" width="45%" />
  <br>
  <img src="docs/screenshots/whatsapp_purchase_flow.png" alt="Purchase Flow" width="90%" />
</div>

### 🏢 Web Dashboard & Integration
<details>
  <summary>Click to view system screenshots</summary>

  #### 📊 Inventory Management
  ![Invoices](https://github.com/user-attachments/assets/5b176c44-82dd-4080-8259-0976029a496f)
  
  #### 🔗 WPPConnect Integration
  ![Integration Detail](docs/screenshots/app_detail.png)
  ![Conversations](docs/screenshots/conversations_list.png)
  
  #### ⚙️ Configuration
  ![Config](docs/screenshots/config_update.png)
</details>

## 👥 Author
- [Zaid Al-Melahi](https://github.com/zaalmelahi) - Integration & Dockerization

---
Happy coding! 🚀
