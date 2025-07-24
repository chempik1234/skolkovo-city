# **Scalable AI-Powered Telegram Bot for Skolkovo** 🚀  

**A high-performance Telegram bot** built on `aiogram 3` with **Django admin panel**

Integrating **YandexGPT Pro**, **embeddings (Yandex Foundation Models)**, and external APIs (weather & events).

Features **RabbitMQ workers**, **Redis caching**, **rate limiting**, and **monitoring via Grafana/Prometheus**.

---

Thanks to donBarbos https://github.com/donBarbos/telegram-bot-template, copied some of his files

---

## **✨ Key Features**  
✅ **AI-Powered Chat** – YandexGPT Pro + embeddings for fast answers (fallback to full GPT if needed)  
✅ **External API Integration** – Weather (OpenWeatherMap) & Skolkovo Events  
✅ **Scalable Architecture** – Async workers (RabbitMQ), Redis caching, PostgreSQL  
✅ **Admin Panel** – Django-based management for content, users, and analytics  
✅ **Monitoring** – Grafana + Prometheus + Loki for logs  
✅ **Rate Limiting** – Protects YandexGPT API from abuse  
✅ **Dynamic Menus** – Category system with nested buttons (text, images, videos, links)  
✅ **Multi-Source Weather** – Aggregates responses from multiple providers (at least supports that) 

---

## **🛠 Tech Stack**  
| **Category**       | **Technologies**                    |  
|--------------------|-------------------------------------|  
| **Backend**        | Python (aiogram 3, Django, FastAPI) |  
| **AI**             | YandexGPT Pro, Yandex Embeddings    |  
| **APIs**           | OpenWeatherMap, Skolkovo Events API |  
| **Message Broker** | RabbitMQ (for task queues)          |  
| **Caching**        | Redis                               |  
| **DB**             | PostgreSQL (user data, questions)   |  
| **Monitoring**     | Grafana, Prometheus, Loki           |  
| **DevOps**         | Docker Compose                      |  

---

## **🚀 Quick Start (Docker)**  

### **Important notification**

Your host must support HTTPS in order to use webhooks. You have 2 options:
1. Use a proxy (e.g. **ngrok, cloudpub**) at home
2. Use a remote server with **SSL**

### **Environment Variables**  
Check config directory for .env.example file and create 3 files:
```
config/
├──.env.example  <-- already there
├──.env
├──.env.grafana
└──.env.rate_limiter
```

Then run the **Makefile**:

```bash  
git clone https://github.com/chempik1234/skolkovo-city.git  
cd skolkovo-bot  
make upd
```  

Then create a **django user**
```bash
docker compose -f docker/docker-compose.yml exec -it admin bash
python manage.py createsuperuser
```

### **Bot structure**  

Bot structure is created by admins themselves!

Use **django admin** to create **nested menus**: http://your-site:8080/admin


---

## **📊 Monitoring & Logs**  
- **Grafana**: `http://localhost:3000` (dashboards for bot metrics)  
- **Prometheus**: `http://localhost:9090` (scrapes service metrics)  
- **Loki**: `http://localhost:3100` (centralized logging)

---

## **🔌 API Integrations**  
| **Service**                  | **Usage**         |  
|------------------------------|-------------------|  
| **Yandex Foundation Models** | Embedding         |
| **YandexGPT Pro**            | AI answers        |  
| **OpenWeatherMap**           | Real-time weather |  
| **Skolkovo Events**          | Upcoming events   |  

---

## **📈 Performance Optimizations**  
⚡ **Redis caching** – Stores embeddings, user data, API responses  
⚡ **RabbitMQ workers** – Async tasks (e.g., category reloads)  
⚡ **Rate limiting** – Protects YandexGPT from spam  
⚡ **Multi-source weather** – Returns the first successful response

**⭐ Star this repo if you like it!**  

--- 

**🔗 Live Demo**: [bot link](https://t.me/skolkovocity_bot)  

