# Task Management API

This is a **Task Management REST API** built using **Django REST Framework (DRF)** with **JWT authentication, caching (Redis), and task scheduling using a priority queue (Min-Heap)**.

## Features
- **JWT Authentication** (Login, Registration, Logout)
- **Task CRUD operations**
- **Filtering & Pagination** (Priority, Status)
- **Caching with Redis** to optimize database queries
- **Task scheduling using a Min-Heap (priority-based ordering)**
- **Postman collection** added for all API endpoints

---

## Installation & Setup

### **1️⃣ Clone the Repository**
```sh
 git clone <repo-url>
 cd task-manager-api
```

### **2️⃣ Create & Activate a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Configure Environment Variables**
Add this in setting : 
```sh
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}  
```

### **5️⃣ Run Redis with Docker**
If Redis is not installed locally, use Docker:
```sh
docker run --name redis -p 6379:6379 -d redis
```

### **6️⃣ Apply Migrations & Run Server**
```sh
python manage.py migrate
python manage.py runserver
```

---

## API Endpoints

### **Authentication APIs**
| Method | Endpoint | Description |
|--------|------------|-------------|
| POST | `/api/register/` | Register a new user |
| POST | `/api/login/` | User login (returns JWT tokens) |
| POST | `/api/logout/` | User logout |

### **Task APIs**
| Method | Endpoint | Description |
|--------|------------|-------------|
| GET | `/api/tasks/` | Get all tasks (supports filtering by priority & status) |
| POST | `/api/tasks/` | Create a new task |
| GET | `/api/tasks/{id}/` | Get task details |
| PUT | `/api/tasks/{id}/` | Update a task |
| DELETE | `/api/tasks/{id}/` | Delete a task |

---

## Postman Collection
A **Postman collection** with all API endpoints has been added to the repository. Import it into Postman to test the API easily.

---

## Deployment
To deploy the project using **Dockerfile**, add a `dockerfile` file:
```
FROM python:3.9-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt


COPY . .

RUN python manage.py makemigrations

RUN  python manage.py migrate

CMD [ "python","manage.py","runserver","0.0.0.0:8000" ]
```
Run the project using:
```sh
ocker build -t tasks .
```

---



