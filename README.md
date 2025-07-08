# 🚀 Talent Manager - AI Content Creation System

A centralized AI system that manages multiple autonomous AI talent personas across various content types and social media platforms. Each talent specializes in different niches (education, entertainment, lifestyle) and creates content, engages audiences, and optimizes performance without human intervention.

## ✨ Features

- 🎭 **Multi-Talent Management**: Oversee multiple AI personas simultaneously
- 🤖 **Autonomous Content Creation**: Automated script generation, voice synthesis, and video assembly
- 📊 **Performance Analytics**: Real-time tracking and optimization
- 🎯 **Platform Integration**: YouTube, TikTok, Instagram support
- 📅 **Smart Scheduling**: Automated content calendar management
- 🔒 **Secure & Compliant**: GDPR/CCPA compliant with content moderation

## 🏗️ Architecture

```
talent-manager/
├── core/                 # Core system components
│   ├── manager/         # Orchestration and scheduling
│   ├── security/        # Authentication and encryption
│   └── database/        # Database models and config
├── talents/             # AI talent personas
├── platforms/           # Social media integrations
├── content/             # Generated content storage
├── analytics/           # Performance tracking
└── dashboard/           # Web interface
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Redis (for background tasks)
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd talent-manager
```

2. **Set up Python environment**
```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

3. **Configure environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

4. **Initialize database**
```bash
python cli.py init
```

5. **Run the application**
```bash
# Using CLI
python cli.py run-server

# Or directly with uvicorn
uvicorn main:app --reload

# Or with Docker Compose
docker-compose up
```

## 🎭 Creating Your First Talent

### Using CLI
```bash
# Create a new talent
python cli.py create-talent

# List all talents
python cli.py list-talents

# Check system status
python cli.py status
```

### Using API
```bash
# Create talent via API
curl -X POST "http://localhost:8000/talents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex CodeMaster",
    "specialization": "Programming Tutorials",
    "personality": {
      "tone": "friendly and encouraging",
      "expertise_level": "intermediate to advanced",
      "teaching_style": "hands-on with practical examples"
    }
  }'
```

## 📋 Required API Keys

Add these to your `.env` file:

### Essential APIs
- **OpenAI API Key**: For content generation
- **ElevenLabs API Key**: For text-to-speech (optional, can use free alternatives)

### Platform APIs
- **YouTube Data API**: Client ID and Secret
- **TikTok Business API**: Client ID and Secret (future)
- **Instagram Basic Display API**: Client ID and Secret (future)

### Example .env Configuration
```bash
# Core APIs
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# Database
DATABASE_URL=sqlite:///./talent_manager.db

# Security
SECRET_KEY=your-super-secret-key-here

# YouTube API
YOUTUBE_CLIENT_ID=your-youtube-client-id
YOUTUBE_CLIENT_SECRET=your-youtube-client-secret
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=talents --cov=platforms

# Run specific test file
pytest tests/test_basic.py -v
```

## 📦 Docker Deployment

### Development
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d
```

### Production
```bash
# Build production image
docker build -t talent-manager:latest .

# Run with production settings
docker run -d \
  --name talent-manager \
  -p 8000:8000 \
  --env-file .env.production \
  talent-manager:latest
```

## 🔧 Development

### Project Structure
- **Core System**: Database models, API routes, authentication
- **Talent System**: AI persona management and content generation
- **Platform Integration**: YouTube, TikTok, Instagram APIs
- **Analytics**: Performance tracking and optimization
- **Dashboard**: Web interface for management

### Adding a New Talent

1. Create talent profile in `talents/` directory
2. Define personality and content strategy
3. Implement content generation pipeline
4. Set up platform-specific publishing
5. Configure performance tracking

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy core/ talents/ platforms/
```

## 📊 Current Status

### ✅ Phase 1: Foundation (COMPLETE)
- [x] Project structure and dependencies
- [x] Database models and configuration
- [x] Basic FastAPI application
- [x] CLI management tool
- [x] Docker configuration
- [x] Basic testing setup

### 🚧 Phase 2: Single Talent MVP (IN PROGRESS)
- [ ] Tech Educator talent implementation
- [ ] Content generation pipeline
- [ ] YouTube API integration
- [ ] Basic performance tracking

### 📋 Upcoming Phases
- **Phase 3**: Automation & Scheduling
- **Phase 4**: Multi-talent scaling
- **Phase 5**: Advanced features
- **Phase 6**: Multi-platform expansion

## 🎯 Performance Targets

- **Technical**: 99.5% uptime, <2hr content generation
- **Growth**: 1K+ subscribers per talent in 3 months
- **Revenue**: $500+ monthly revenue per talent in 6 months

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Open an issue on GitHub
- **API Reference**: Visit `/docs` when running the server

## 🌟 Roadmap

- [x] **Phase 1**: Foundation & Infrastructure
- [ ] **Phase 2**: Single Talent MVP
- [ ] **Phase 3**: Automation Pipeline
- [ ] **Phase 4**: Multi-Talent System
- [ ] **Phase 5**: Advanced Analytics
- [ ] **Phase 6**: Multi-Platform Support
- [ ] **Phase 7**: Web Dashboard
- [ ] **Phase 8**: Monetization Features

---

**Built with ❤️ for autonomous content creation**