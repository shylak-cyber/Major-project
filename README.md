# Major Project

A high-performance backend application built using **FastAPI**, featuring authentication, product management, Redis caching, benchmarking utilities, and dashboard analytics.

---

## 🚀 Features

- 🔐 JWT Authentication System
- 📦 Product Management APIs
- ⚡ Redis Caching Integration
- 📊 Benchmark & Performance Monitoring
- 🧠 Service Layer Architecture
- 🗄️ Database Integration
- 📈 Dashboard Interface
- 🔄 Cache Strategies & Optimization
- 🛠️ Modular API Structure

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **Caching:** Redis
- **Authentication:** JWT Tokens
- **Frontend Dashboard:** HTML
- **ORM / Models:** SQLAlchemy
- **API Testing:** Swagger UI

---

## 📂 Project Structure

```bash
Major-project/
│
├── auth_routes.py          # Authentication APIs
├── benchmark_routes.py     # Benchmark APIs
├── benchmark_service.py    # Benchmark logic
├── cache_routes.py         # Cache management routes
├── config.py               # Configuration settings
├── connection.py           # Database connection
├── dashboard.html          # Dashboard UI
├── dependencies.py         # Dependency injection
├── jwt_handler.py          # JWT token handling
├── main.py                 # Main FastAPI app
├── models.py               # Database models
├── password.py             # Password hashing utilities
├── product_routes.py       # Product APIs
├── product_service.py      # Product business logic
├── redis_client.py         # Redis connection setup
├── schemas.py              # Pydantic schemas
├── seed.py                 # Database seed data
├── services.py             # Core services
├── stats.py                # Statistics module
├── strategies.py           # Cache strategies
└── README.md
