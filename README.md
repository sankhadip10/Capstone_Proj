# README.md - Setup instructions for developers
## 🚀 Development Setup

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Setup secrets (required):**
   ```bash
   # Copy the template
   cp .env.docker.example .env.docker
   
   # Edit with your actual development credentials
   nano .env.docker  # or use your preferred editor
   ```

3. **Get Razorpay test credentials:**
   - Go to [Razorpay Dashboard](https://dashboard.razorpay.com/app/keys)
   - Copy your Test Key ID and Secret
   - Add them to `.env.docker`

4. **Start the development environment:**
   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f web
   ```

5. **Access the application:**
   - Django App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin (admin/1122334455)
   - Flower (Celery): http://localhost:5555
   - Email Testing: http://localhost:5000

### Important Notes

- ⚠️ **Never commit `.env.docker`** - it contains sensitive credentials
- ✅ **Always use `.env.docker.example`** as a template for new developers
- 🔐 **Keep your test credentials secure** - don't share them publicly

### Testing
```bash
docker-compose --profile testing run --rm tests
```

### Stopping
```bash
docker-compose down
```