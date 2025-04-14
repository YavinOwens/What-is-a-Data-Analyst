# Development Environment Setup

This directory contains everything needed to set up a development environment for the GDPR fines analysis project, as described in Andi's story.

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Git

## Getting Started

### 1. Start the Docker containers

```bash
# From the _DevelopmentEnvironment directory
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache service (port 6379)
- PgAdmin interface (port 5050)
- VS Code in browser via code-server (port 8080)

### 2. Set up the Python environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify the database connection

```bash
# Make sure your .env file is properly configured
python src/db/init_db.py
```

You should see a success message if everything is working correctly.

## Development Tools

### VS Code in Browser

You can access VS Code directly in your browser:

- URL: http://localhost:8080
- Password: andi_password

This gives you a full VS Code experience with:
- Integrated terminal
- Syntax highlighting
- Extensions
- Debugging capabilities
- Git integration

### Database Access

You can access the PostgreSQL database in several ways:

1. **Direct connection**: Use the following details:
   - Host: localhost
   - Port: 5432
   - Database: gdpr_fines
   - Username: andi_user
   - Password: andi_password

2. **PgAdmin**:
   - URL: http://localhost:5050
   - Email: admin@example.com
   - Password: admin

   After logging in, add a new server with the following details:
   - Host: postgres (use this name, not localhost, because PgAdmin runs in a container)
   - Port: 5432
   - Database: gdpr_fines
   - Username: andi_user
   - Password: andi_password

### Redis Access

For Redis, you can use these connection details:

- Host: localhost
- Port: 6379
- No password (for development)

## Project Structure

- `docker-compose.yml`: Docker Compose configuration
- `init-scripts/`: Database initialization scripts
- `src/`: Source code
  - `db/`: Database interaction code
- `.env`: Environment variables for development

## Common Tasks

### Rebuilding the environment

```bash
docker-compose down
docker-compose up --build -d
```

### Resetting the database

```bash
docker-compose down -v
docker-compose up -d
```

### Executing database queries

```python
from src.db.init_db import execute_query

results = execute_query("SELECT * FROM gdpr.fines LIMIT 10")
for row in results:
    print(row)
```

## Troubleshooting

- **Database connection issues**: Ensure Docker containers are running and ports are not in use by other services
- **Python dependency issues**: Make sure you're using the correct virtual environment and all dependencies are installed
- **Port conflicts**: If you have services already running on the required ports, modify the `docker-compose.yml` file to use different ports 