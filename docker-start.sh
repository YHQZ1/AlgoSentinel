#!/bin/bash

# AlgoSentinel - Docker Production Build Script

echo "🐳 Building AlgoSentinel with Docker..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

echo "📋 Building containers..."
docker compose build

echo ""
echo "✅ Build complete!"
echo ""
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "📍 Services are running:"
echo "   • Frontend:    http://localhost:3000"
echo "   • API:         http://localhost:8000"
echo "   • API Docs:    http://localhost:8000/docs"
echo "   • Dashboard:   http://localhost:8501"
echo "   • Redis:       localhost:6379"
echo ""
echo "📊 View logs:"
echo "   docker compose logs -f frontend"
echo "   docker compose logs -f api"
echo "   docker compose logs -f trading_bot"
echo "   docker compose logs -f ai_sentinel"
echo ""
echo "🛑 Stop services:"
echo "   docker compose down"
echo ""
