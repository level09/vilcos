#!/bin/bash

# ANSI color codes for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display banner
echo -e "${BLUE}"
echo "╔═════════════════════════════════════════════════════════════╗"
echo "║           VILCOS STATIC SITE DEPLOYMENT                     ║"
echo "║                Single Docker Container                      ║"
echo "╚═════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is required but not installed.${NC}"
    echo "Please install Docker first."
    exit 1
fi

# Check if dist directory exists and has been built
if [ ! -d "dist" ] || [ ! -f "dist/templates/index.html" ]; then
  echo -e "${YELLOW}Building website assets...${NC}"
  npm install && npm run build
fi

# Make sure index.html exists
if [ ! -f "dist/templates/index.html" ]; then
  echo -e "${RED}Error: dist/templates/index.html not found after build. Check your build configuration.${NC}"
  exit 1
fi

# Define image name and container name
IMAGE_NAME="vilcos-static"
CONTAINER_NAME="vilcos-site"

# Clean up any existing container
if docker ps -a | grep -q $CONTAINER_NAME; then
  echo -e "${YELLOW}Stopping and removing existing container...${NC}"
  docker stop $CONTAINER_NAME >/dev/null 2>&1
  docker rm $CONTAINER_NAME >/dev/null 2>&1
fi

# Optional: Clean up any dangling images
docker image prune -f >/dev/null 2>&1

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t $IMAGE_NAME -f docker-deploy/Dockerfile .

# Run the container
echo -e "${YELLOW}Starting container...${NC}"
docker run -d --name $CONTAINER_NAME -p 8080:80 $IMAGE_NAME

echo -e "${GREEN}✓ Static site deployed successfully!${NC}"
echo -e "${BLUE}➤ Your site is now available at:${NC} http://localhost:8080"
echo -e "${YELLOW}To stop the container: docker stop $CONTAINER_NAME${NC}"
echo -e "${YELLOW}To view logs: docker logs -f $CONTAINER_NAME${NC}"

# Ask if user wants to see logs
read -p "Would you like to see the logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker logs -f $CONTAINER_NAME
fi 