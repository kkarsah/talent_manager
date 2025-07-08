#!/bin/bash
# setup.sh - Complete Phase 1 Setup Script

echo "🚀 Setting up Talent Manager - Phase 1"
echo "=================================="

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
poetry install

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your API keys"
fi

# Create necessary directories
echo "📁 Creating content directories..."
mkdir -p data
mkdir -p content/{scripts,audio,video,thumbnails}
mkdir -p logs

# Initialize database
echo "🗄️ Initializing database..."
poetry run python cli.py init

# Run tests to ensure everything works
echo "🧪 Running tests..."
poetry run pytest tests/ -v

# Check system status
echo "🔍 Checking system status..."
poetry run python cli.py status

echo ""
echo "✅ Phase 1 setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Create your first talent: poetry run python cli.py create-talent"
echo "3. Start the server: poetry run python cli.py run-server"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "📚 For more info, check the README.md file"