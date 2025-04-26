# Valley View Farms Golf League Project

This project is a complete golf league management system designed for the Valley View Farms Golf League.

It includes:
- **Player Registration**
- **Handicap Calculation**
- **Round Score Tracking**
- **League Standings and Statistics**
- **Automatic data sync** between MySQL and PostgreSQL
- **Dockerized Deployment**

---

## 📦 Technologies Used
- **Flask (Python)** – Frontend API and web app
- **MySQL** – Main database for app operations
- **PostgreSQL** – Backup and stats reporting database
- **.NET Core (C#)** – Worker service to transfer and calculate data
- **Docker / Docker Compose** – Containerized environment
- **Kubernetes YAML files** – For future production deployment

---

## 🚀 How to Install and Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/raorosz/golf_project_v1.git
cd golf_project_v1
```

### 2. Build and Start Docker Containers
```bash
docker-compose up --build
```

This will spin up:
- Flask app (Python)
- MySQL database
- PostgreSQL database
- Worker service (C#)

App will be available at:  
👉 `http://localhost:5000`

### 3. Access MySQL and PostgreSQL
- **MySQL**: `localhost:3306`
- **PostgreSQL**: `localhost:5432`

Credentials (inside docker-compose):
- Username: `root` / `postgres`
- Password: `P@ssword`

---

## 🏌️ Main Features
- Add Players & Teams
- Enter Round Scores
- View Live League Standings and Stats

---

## 📂 Project Structure
```text
/src
   /flask_app      # Python web app (Flask)
   /worker_app     # .NET Core Worker (C#)
   /mysql          # MySQL docker config
   /postgres       # PostgreSQL docker config
   /kubernetes     # Deployment YAMLs
/docker-compose.yaml
/README.md
```
## 🎥 Project Demo Video

[![Watch the video](https://img.shields.io/badge/YouTube-Project%20Demo-red?logo=youtube&logoColor=white)](https://youtu.be/RWCRX5PooJk)

## 🎥 [Watch Project Demo on YouTube](https://youtu.be/RWCRX5PooJk)

---

> Built with ❤️ by Robert Orosz.
