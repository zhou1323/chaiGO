# ChaiGO

Backend service for ChaiGO, a personal finance management website. The service is built with Python and uses FastAPI framework.

## Technology Stack

- **FastAPI**: Python framework for building APIs.
- **SQLModel**: ORM for simplifying database operations.
- **PostgreSQL**: Database for storing financial data.
- **Redis**: In-memory data structure store for high-performance data access.
- **Celery**: Distributed task queue for executing background tasks.
- **Traefik**: Reverse proxy for managing API routes.
- **Sentry**: Error tracking and logging.
- **OpenAI**: AI services for generating recommendations and insights.
- **AWS CloudFront**: CDN for serving static assets and improving performance.
- **AWS S3**: Object storage for storing static assets.
- **Docker**: Simplifies deployment and consistency across environments.
- **GitHub Actions**: Integrations with GitHub Actions for automated testing and deployments.

## Key Features

- **Expense Tracking**: Automatically extracts information from receipts and credit card statements.
- **Spending Analysis**: Analyzes spending patterns and provides budget warnings.
- **Discount Recommendations**: Lists discounted items and suggests purchases based on remaining budget.

## Project wikis

[Here](https://chai-go.notion.site/ChaiGO-Frontend-944924824444444444444444444) is the link to the project wiki.

## Project Structure

```bash
backend/
├── app/
│   ├── api/                      # API endpoints
│   │   ├── admin/                # Admin API endpoints
│   │   │   ├── crud/             # CRUD operations
│   │   │   ├── model/            # Data models
│   │   │   ├── routes/           # API routes
│   │   │   └── service/          # API services
│   │   ├── ...                   # Other API endpoints
│   │   └── utils/                # Utility functions
│   ├── common/                   # Shared components and utilities.
│   ├── core/                     # Core application configurations and setup
│   ├── middleware/               # Custom middleware for the application
│   ├── tests/                    # Test cases
│   ├── utils/                    # Utility functions
│   └── *.py                      # Other scripts files
└── scripts/                      # Helper shell scripts    
```

## Configuration

When developing locally, create a `.env` file in the root directory and set the following environment variables. To integrate with GitHub Actions, use the secrets in the repository settings.

### Environment Variables
- `DOMAIN`: The domain name of the application (e.g., localhost for development)
- `ENVIRONMENT`: The current environment (local, staging, production)
- `PROJECT_NAME`: The name of the project
- `STACK_NAME`: The name of the stack

### Backend Configuration
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins
- `SECRET_KEY`: Secret key for the application
- `FIRST_SUPERUSER`: Email of the first superuser
- `FIRST_SUPERUSER_PASSWORD`: Password for the first superuser
- `USERS_OPEN_REGISTRATION`: Whether to allow open user registration

### Email Configuration
- `SMTP_HOST`: SMTP server host
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `EMAILS_FROM_NAME`: Name to use in the "From" field of emails
- `EMAILS_FROM_EMAIL`: Email address to use in the "From" field
- `EMAIL_TEST_USER`: Email address for testing
- `SMTP_TLS`: Whether to use TLS
- `SMTP_SSL`: Whether to use SSL
- `SMTP_PORT`: SMTP server port

### Database Configuration
- `POSTGRES_SERVER`: PostgreSQL server address
- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_PORT`: PostgreSQL server port
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password

### Redis Configuration
- `REDIS_HOST`: Redis server host
- `REDIS_PORT`: Redis server port
- `REDIS_PASSWORD`: Redis password
- `REDIS_DATABASE`: Redis database number

### AWS Configuration
- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key
- `AWS_REGION_NAME`: AWS region
- `AWS_BUCKET_NAME`: AWS S3 bucket name

### CloudFront Configuration
- `CLOUDFRONT_DISTRIBUTION_DOMAIN`: CloudFront distribution domain
- `CLOUDFRONT_KEY_ID`: CloudFront key ID
- `CLOUDFRONT_PRIVATE_KEY_STRING`: CloudFront private key (as a base64 encoded string)

### OpenAI Configuration
- `OPENAI_KEY`: OpenAI API key

### Sentry Configuration
- `SENTRY_DSN`: Sentry DSN for error tracking

### Docker Configuration
- `DOCKER_IMAGE_BACKEND`: Docker image name for the backend
- `DOCKER_IMAGE_FRONTEND`: Docker image name for the frontend

## How to run

### Local development with Docker Compose
```bash
docker compose up -d
```

### Or run the backend service directly

```bash
# Add this configuration in .vscode/launch.json
{
    "name": "Debug FastAPI Project backend: Python Debugger",
    "type": "debugpy",
    "request": "launch",
    "module": "uvicorn",
    "args": ["app.main:app", "--reload"],
    "cwd": "${workspaceFolder}/backend",
    "jinja": true,
    "envFile": "${workspaceFolder}/.env"
}
```

