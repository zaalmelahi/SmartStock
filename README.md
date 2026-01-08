<img width="1024" height="515" alt="config_update" src="https://github.com/user-attachments/assets/56ad1bf4-5952-438f-a0fb-9379dc8d5e96" /># 📦 SmartStock - Sales & Inventory Management
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

## 📸 Screenshots & Gallery

### 🤖 AI WhatsApp Assistant
| Sales Stats | Analytics |
| :---: | :---: |
| ![Sales Stats](https://raw.githubusercontent.com/zaalmelahi/SmartStock/main/docs/screenshots/whatsapp_sales_stats.png) | ![Analytics](https://raw.githubusercontent.com/zaalmelahi/SmartStock/main/docs/screenshots/whatsapp_analytics.png) |

**AI Purchase Order Flow**  
![Purchase Flow](https://raw.githubusercontent.com/zaalmelahi/SmartStock/main/docs/screenshots/whatsapp_purchase_flow.png)

### 🏢 Web Management & Integration
<details>
  <summary>Click to view system & integration screenshots</summary>

  #### 🔗 Integration Detail
 <img width="1024" height="519" alt="app_detail" src="https://github.com/user-attachments/assets/c7147377-4a64-47b0-b7f4-22b71b882eac" />
<img width="1024" height="562" alt="app_edit" src="https://github.com/user-attachments/assets/3431792f-81fe-49ff-829f-9fc825a40f69" />
<img width="1024" height="515" alt="config_update" src="https://github.com/user-attachments/assets/87a985cc-ca2f-4173-bead-7fd430ff2182" />


  #### 💬 Conversations Logging
<img width="1024" height="518" alt="conversations_list" src="https://github.com/user-attachments/assets/d08f2161-18e5-401f-9751-d809004a8388" />
<img width="1024" height="517" alt="conversation_detail" src="https://github.com/user-attachments/assets/c0bd0827-1616-41a0-8a7b-a4ef9b19e205" />



  #### ⚙️ Configuration
  <img width="1024" height="515" alt="config_update" src="https://github.com/user-attachments/assets/60cb0e53-0d28-4bae-a1d5-e12dd210189b" />

#### ⚙️ WhatsApp
<img width="1024" height="728" alt="whatsapp_sales_stats" src="https://github.com/user-attachments/assets/ebe6bb35-c95d-46e7-b2e2-1cb4cd98eb1c" />
<img width="1024" height="575" alt="whatsapp_purchase_flow" src="https://github.com/user-attachments/assets/f5a384ce-92a6-4817-b746-c38fc360808b" />
<img width="1024" height="627" alt="whatsapp_analytics" src="https://github.com/user-attachments/assets/8295e483-2e34-4937-bef8-849bd2850845" />


</details>

### 🖼 Full System Gallery
<details>
  <summary>Click to view all 15 legacy screenshots</summary>

  ![screenshot_1](https://github.com/user-attachments/assets/9bb2f5f9-d456-4681-b5de-8d82a3ef97d8)

  ![screenshot_2](https://github.com/user-attachments/assets/d6e14ba3-8827-41c1-9cdb-8f24add83f4d)

  ![screenshot_3](https://github.com/user-attachments/assets/6be5060e-974b-4289-bcdf-b852771833f8)

  ![screenshot_4](https://github.com/user-attachments/assets/5b176c44-82dd-4080-8259-0976029a496f)

  ![screenshot_5](https://github.com/user-attachments/assets/c9ab8f77-bf2a-4b1e-bc66-986101d4991b)

  ![screenshot_6](https://github.com/user-attachments/assets/3db3ca87-28a8-4fee-8cc7-fcc9481076f4)

  ![screenshot_7](https://github.com/user-attachments/assets/1197a79f-8e11-41e1-a8a8-4ea5f0ac0391)

  ![screenshot_8](https://github.com/user-attachments/assets/a340d85b-76dc-4618-b530-97cd620ef649)

  ![screenshot_9](https://github.com/user-attachments/assets/751fe028-6115-424e-b69c-0fedfa9f321f)

  ![screenshot_10](https://github.com/user-attachments/assets/d3905ec2-c843-468c-bdd4-799955854fd6)

  ![screenshot_11](https://github.com/user-attachments/assets/99bb9f1c-4688-4049-b31e-5de1bd817304)

  ![screenshot_12](https://github.com/user-attachments/assets/a0ea68c0-2969-42e4-81cd-fbf6efffd569)

  ![screenshot_13](https://github.com/user-attachments/assets/9fbd7b1c-d60c-456a-957c-4a033cf76d89)

  ![screenshot_14](https://github.com/user-attachments/assets/b6eabb9a-119a-418d-af56-b44d316bf6be)

  ![screenshot_15](https://github.com/user-attachments/assets/ec117dfd-e0ee-46ff-9486-b5262f58b901)
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
- [Zaid Al-Melahi](https://github.com/zaalmelahi) - Integration & Dockerization

---
Happy coding! 🚀
