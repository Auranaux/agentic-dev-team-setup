# Agentic Dev Team - Heroku Deployment

A production-ready agentic multi-agent web development system built with FastAPI, PostgreSQL, and OpenAPI contracts. Designed for seamless deployment to Heroku with built-in GitHub integration.

## Features

- **Orchestrator**: Intelligent intake system with slot filling and PRD generation
- **Backend**: RESTful API with CRUD operations following OpenAPI contracts
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **OpenAPI Contracts**: Source of truth API specification with validation
- **LLM Integration**: Model-agnostic support for OpenAI and Anthropic
- **CI/CD**: Automated testing and contract validation
- **Heroku Ready**: Optimized for Heroku deployment with buildpacks

## Quick Start

### Local Development

1. **Set up Python environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database URL and API keys
export DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/agentic
```

3. **Run database migrations**:
```bash
alembic upgrade head
```

4. **Start the development server**:
```bash
uvicorn app.main:app --reload --port 8000
```

5. **Access the application**:
- API Documentation: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json
- Health Check: http://localhost:8000/healthz

### Sample API Usage

**Start an intake conversation**:
```bash
curl -X POST http://localhost:8000/intake/start \
  -H "Content-Type: application/json" -d '{"project_name":"My Project"}'
```

**Create a draft**:
```bash
curl -X POST http://localhost:8000/v1/drafts \
  -H "Content-Type: application/json" \
  -d '{"owner":"dev","payload":{"type":"feature","status":"draft"}}'
```

**List drafts**:
```bash
curl http://localhost:8000/v1/drafts
```

**Commit intake (generate PRD)**:
```bash
curl -X POST http://localhost:8000/intake/commit \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"conv_12345678"}'
```

## Heroku Deployment

### Step-by-Step Heroku Setup

1. **Create Heroku App**:
   - Go to [Heroku Dashboard](https://dashboard.heroku.com)
   - Click "New" → "Create new app"
   - Choose app name and region
   - Click "Create app"

2. **Connect GitHub Repository**:
   - In your Heroku app dashboard, go to "Deploy" tab
   - Under "Deployment method", select "GitHub"
   - Connect your GitHub account if not already connected
   - Search for "agentic-dev-team-heroku" repository
   - Click "Connect"

3. **Enable Automatic Deploys**:
   - In the "Deploy" tab, scroll to "Automatic deploys"
   - Select the branch you want to deploy from (usually `main`)
   - Click "Enable Automatic Deploys"

4. **Add Heroku Postgres**:
   - Go to "Resources" tab
   - In "Add-ons" section, search for "Heroku Postgres"
   - Select "Heroku Postgres" and choose plan (Mini is fine for development)
   - Click "Submit Order Form"
   - This automatically sets the `DATABASE_URL` environment variable

5. **Configure Environment Variables**:
   - Go to "Settings" tab
   - Click "Reveal Config Vars"
   - Add the following variables:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `RUN_DB_MIGRATIONS` | `1` | Enables automatic migrations on startup |
   | `LLM_PROVIDER` | `openai` or `anthropic` | Choose your LLM provider |
   | `OPENAI_API_KEY` | `your_openai_key` | Required if using OpenAI |
   | `ANTHROPIC_API_KEY` | `your_anthropic_key` | Required if using Anthropic |
   | `ALLOWED_ORIGINS` | `*` | CORS origins (use specific domains in production) |
   | `API_KEY` | `your_api_key` | Optional API key for authentication |

6. **Deploy**:
   - Go back to "Deploy" tab
   - Click "Deploy Branch" for manual deployment
   - Or push to your connected branch for automatic deployment

### Verification

After deployment, test your Heroku app:

```bash
# Replace <YOUR_APP_NAME> with your actual Heroku app name
export HEROKU_APP_URL=https://<YOUR_APP_NAME>.herokuapp.com

# Health check
curl $HEROKU_APP_URL/healthz

# API documentation
open $HEROKU_APP_URL/docs

# Test draft creation
curl -X POST $HEROKU_APP_URL/v1/drafts \
  -H "Content-Type: application/json" \
  -d '{"owner":"test","payload":{"message":"Hello from Heroku!"}}'

# List drafts
curl $HEROKU_APP_URL/v1/drafts
```

### Alternative: Heroku CLI Deployment

If you prefer using the Heroku CLI:

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Add Postgres addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set RUN_DB_MIGRATIONS=1
heroku config:set LLM_PROVIDER=openai
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set ALLOWED_ORIGINS=*

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string (auto-set by Heroku Postgres) |
| `RUN_DB_MIGRATIONS` | No | `0` | Set to `1` to run migrations on startup |
| `LLM_PROVIDER` | No | `openai` | LLM provider: `openai` or `anthropic` |
| `OPENAI_API_KEY` | Conditional | - | Required if `LLM_PROVIDER=openai` |
| `ANTHROPIC_API_KEY` | Conditional | - | Required if `LLM_PROVIDER=anthropic` |
| `ALLOWED_ORIGINS` | No | `*` | CORS allowed origins (comma-separated) |
| `API_KEY` | No | - | Optional API key for request authentication |

## Architecture

### File Structure
```
app/
├── main.py                 # FastAPI application factory
├── orchestrator/           # Intake and slot filling system
│   ├── routes.py          # API endpoints
│   ├── slots.py           # Slot management logic
│   ├── generator.py       # PRD and contract generation
│   └── llm/               # LLM integration layer
├── backend/               # Core API implementation
│   ├── routes_drafts.py   # Draft CRUD endpoints
│   ├── models.py          # SQLAlchemy models
│   └── deps.py            # Dependencies
├── db/                    # Database configuration
│   └── base.py            # SQLAlchemy setup
├── qa/                    # Test suite
│   ├── test_drafts.py     # Draft API tests
│   └── test_contracts.py  # Contract validation tests
└── devops/                # Operations
    └── health.py          # Health check endpoints

contracts/
└── api.yaml               # OpenAPI specification (source of truth)

docs/
├── prds/                  # Generated PRDs
└── templates/             # Document templates

alembic/                   # Database migrations
├── env.py
├── script.py.mako
└── versions/
```

### Database Schema

**Truth Ledger Tables**:
- `conversations` - Intake conversations
- `slots` - Slot filling data
- `features` - Feature definitions
- `artifacts` - Generated artifacts (PRDs, contracts)
- `events` - System events
- `approvals` - Approval workflows
- `policies` - System policies

**Demo Tables**:
- `drafts` - Sample CRUD resource

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest app/qa/ -v

# Run specific test file
pytest app/qa/test_drafts.py -v

# Run with coverage
pytest app/qa/ --cov=app --cov-report=html
```

### OpenAPI Contract Validation

```bash
# Validate contract syntax
python -c "
from openapi_spec_validator.readers import read_from_filename
from openapi_spec_validator import validate_spec
spec_dict, spec_url = read_from_filename('contracts/api.yaml')
validate_spec(spec_dict)
print('Contract is valid!')
"

# Check contract parity with served API
python -c "
import yaml
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
with open('contracts/api.yaml') as f:
    contract = yaml.safe_load(f)
served = client.get('/openapi.json').json()
# Add your parity checks here
"
```

### Adding New Endpoints

1. **Update the contract** (`contracts/api.yaml`)
2. **Implement the endpoint** (in appropriate router)
3. **Add tests** (`app/qa/`)
4. **Run validation** to ensure parity

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## CI/CD

The project includes GitHub Actions CI that:
- Validates OpenAPI contracts
- Runs the full test suite
- Checks contract parity with served API
- Supports PostgreSQL testing

Deployment to Heroku happens automatically via GitHub integration when you push to the connected branch.

## Troubleshooting

### Common Issues

**Migration Errors**:
```bash
# Check current migration status
alembic current

# Reset migrations (development only)
alembic downgrade base
alembic upgrade head
```

**Database Connection Issues**:
```bash
# Test database connectivity
python -c "
from app.db.base import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connected successfully!')
"
```

**Heroku Deployment Issues**:
```bash
# View Heroku logs
heroku logs --tail --app your-app-name

# Check config vars
heroku config --app your-app-name

# Restart dynos
heroku restart --app your-app-name
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Link to Devin run**: https://app.devin.ai/sessions/7fa0435d5d0f45cea0fa553913eab54a
**Requested by**: @Auranaux
