# RESTful URL Shortener
![Licence](https://img.shields.io/badge/Licence-MIT-green?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/dettinjo/kube-url-shortener?style=for-the-badge)
![GitHub contributors](https://img.shields.io/github/contributors/dettinjo/kube-url-shortener?style=for-the-badge)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#group-members">Group Members</a>
    <li>
      <a href="#about-the-project">About the Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#features">Features</a></li>
        <li><a href="#structure">Structure</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li>
      <a href="#api-endpoints">API Endpoints</a>
      <ul>
        <li><a href="#authentication-service">Authentication Service</a></li>
        <li><a href="#url-shortener-service">URL Shortener Service</a></li>
      </ul>
    </li>
    <li>
      <a href="#testing">Testing</a>
    </li>
    <li>
      <a href="#contribution">Contribution</a>
    </li>
  </ol>
</details>

---

<!-- GROUP MEMBERS -->
## Group Members
- **Azeem Aamer** - 2793200 - <m.a.aamer@student.vu.nl>
- **Joel Dettinger** - 2837238 - <j.dettinger@student.vu.nl>
- **Yusuf Aydoğan** - 2692505 - <h.y.aydogan@student.vu.nl>

---

<!-- PROJECT OVERVIEW -->
## About the Project

The **RESTful URL Shortener** is a **Flask-based microservices** setup, consisting of:
1. A dedicated **Authentication Service** for multi-user management, issuing JSON Web Tokens (JWTs).
2. A **URL Shortener Service** that shortens URLs, tracks usage statistics, and enforces access control via JWTs.

Users register and authenticate against the **Authentication Service** and obtain a JWT. The **URL Shortener** then uses that token to verify user permissions, create new short IDs (either randomly generated or custom), redirect on GET requests, and manage URL statistics.

### Built With
- [![PythonBadge]](https://www.python.org/doc/)
- [![DockerBadge]](https://docs.docker.com/)
- [![BashBadge]](https://www.gnu.org/software/bash/manual/bash.html)

### Features
1. **JWT-Based Authentication**: Users must log in with the Auth Service to get a token.  
2. **Shorten URLs**: Generate either a random short ID or supply a **custom** short ID.  
3. **Always Create a New Short ID**: Reposting the same URL will **not** return the old short ID—each POST creates a unique new one.  
4. **Retrieve & Redirect**: A GET request to the shortened URL returns an HTTP 301 redirect to the original URL.  
5. **Multi-User**: Each URL belongs to the user who created it.  
6. **Store Mappings in SQLite**: Persistent storage for both user credentials and URL mappings.  
7. **Track Usage**: The number of times a shortened URL has been accessed.  
8. **Validate URLs**: Basic format validation ensures well-formed submissions.  
9. **Unit Tests**: Ensure that each service and feature works as intended.

---

### Structure

```
<base folder>/
├── auth_service/
│   ├── __init__.py          # Initializes Flask app
│   ├── app.py               # Entrypoint to run Authentication Service
│   ├── database.py          # SQLite DB logic for user management
│   ├── requirements.txt     # Dependencies (Flask, Regex, etc.)
│   ├── routes.py            # API endpoints for user registration, login, password changes
│   ├── utils.py             # Helper functions (Base64 encoding, hashing, JWT creation/verification)
├── kubernetes/              # Kubernetes configuration files
├── postman/
│   ├── postman.json         # Postman Collection to test endpoints
├── tests/
│   ├── test_app.py          # TA Provided Unit Tests
├── url_shortener_service/
│   ├── __init__.py          # Initializes Flask app
│   ├── app.py               # Entrypoint to run URL Shortener Service
│   ├── database.py          # SQLite DB logic for URL mappings & stats
│   ├── requirements.txt     # Dependencies (Flask, Regex, etc.)
│   ├── routes.py            # API endpoints for shortening & retrieving URLs
│   ├── utils.py             # Helper functions (Base62, random short ID generation, JWT verification)
├── .dockerignore            # Specifies files and directories to ignore when building the Docker image
├── .env.example             # Template for environment variables (copy and rename to .env for local setup)
├── .gitignore               # Defines files and directories to exclude from Git version control
├── docker-compose.yml       # Defines multi-container Docker application configuration
├── Dockerfile               # Instructions for building the application’s Docker image
├── group20_web_service*.pdf # Documentation or report related to the project
└── README.md                # Project documentation and setup instructions
```

<!-- PROJECT SETUP -->
## Getting Started

### 1️⃣ Installation

#### Clone the Repository
```bash
git clone https://github.com/akseron/Group20_web_service_3.git
cd Group20_web_service_3
```

#### Set Up a Virtual Environment
Execute in each microservice directory:
```bash
python3 -m venv virtual_env
source virtual_env/bin/activate  # On Linux/Mac
virtual_env\Scripts\activate  # On Windows

pip install -r requirements.txt
```

#### Set Up Environment Variables
Before running the application, copy .env.example to .env and update necessary values:
```bash
cp .env.example .env
```

---

### 2️⃣ Running the Application

#### 🔹 Option 1: Run with Docker (Recommended)
```sh
docker compose up --build -d
```
To stop:
```sh
docker compose down
```

#### 🔹 Option 2: Run Without Docker (Manual Setup)
```sh
python -m auth_service.app
python -m url_shortener_service.app
```

---

<!-- API ENDPOINTS -->
## API Endpoints

### Authentication Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | Retrieve all users (mainly for debugging) |
| `POST` | `/users` | Create a new user (requires username & password) |
| `PUT` | `/users` | Update an existing user’s password |
| `POST` | `/users/login` | Log in user (returns JWT) or verify an existing one |

### URL Shortener Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/` | Create a new short URL (can supply short_id for custom). Always creates a unique entry. |
| `GET` | `/<short_id>` | Retrieve original URL |
| `PUT` | `/<short_id>` | Update an existing URL |
| `DELETE` | `/<short_id>` | Delete a short URL |
| `GET` | `/stats/<short_id>` | Get the number of times a short URL was accessed |
| `GET` | `/>` | Retrieve all short IDs (owned by the authenticated user) |
| `DELETE` | `/` | Delete all short IDs owned by the authenticated user |

#### Example Usage

1. **Obtain a JWT** (Authentication Service)
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "mypass"}' \
     http://localhost:8001/users/login
# Returns: {"token": "<JWT>"}
```

2.	**Create a Short URL** (URL Shortener)
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT>" \
     -d '{"url": "https://example.com"}' \
     http://localhost:8000/
# Returns: {"id": "<generatedShortID>", "value": "https://example.com"}
```

3. **Create a Short URL with Custom ID**
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT>" \
     -d '{"url": "https://example2.com", "short_id": "myCustomID"}' \
     http://localhost:8000/
# Returns: {"id": "myCustomID", "value": "https://example2.com"}
```

4. **Retrieve & Redirect**
```bash
curl -X GET http://localhost:8000/<short_id>
# This performs an HTTP 301 redirect to the original link. 
```

5. **Get Stats**
```bash
curl -X GET -H "Authorization: Bearer <JWT>" \
     http://localhost:8000/stats/<short_id>
# Returns: {"short_id": "<short_id>", "clicks": 5}
```

---

<!-- TESTING -->
## Testing

The application includes **unit tests** under `tests` folder.

### Run Tests
```bash
python -s tests/test_app.py
```

### Expected Output
```
.........
----------------------------------------------------------------------
Ran 7 tests in 0.XXXs

OK
```

<!-- MARKDOWN LINKS & IMAGES -->
[PythonBadge]:https://img.shields.io/badge/python-yellow?style=for-the-badge&logo=python&logoColor=white
[DockerBadge]:https://img.shields.io/badge/Docker-%231D63ED?style=for-the-badge&logo=docker&logoColor=white
[BashBadge]:https://img.shields.io/badge/GNU%20Bash-black?style=for-the-badge&logo=gnubash&logoColor=white
