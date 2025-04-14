#!/bin/bash
# Setup script for the development environment

# Print message
echo "Starting setup for the GDPR Fines Analysis development environment..."

# Step 1: Start Docker containers
echo "Step 1: Starting Docker containers..."
docker-compose up -d

# Step 2: Create virtual environment
echo "Step 2: Creating Python virtual environment..."
python3 -m venv venv

# Step 3: Activate virtual environment and install dependencies
echo "Step 3: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Wait for PostgreSQL to be ready
echo "Step 4: Waiting for PostgreSQL to be ready..."
sleep 10  # Simple wait for PostgreSQL to start

# Step 5: Create log directory
echo "Step 5: Creating log directory..."
mkdir -p logs

echo "====================================="
echo "Setup script completed!"
echo "You can now use the development environment."
echo "====================================="
echo "Services available:"
echo "PostgreSQL: localhost:5432"
echo "Redis: localhost:6379"
echo "PgAdmin: http://localhost:5050"
echo "====================================="
echo "To stop the environment, run:"
echo "docker-compose down"
echo "=====================================" 