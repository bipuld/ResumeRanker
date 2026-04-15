# ATS Resume Screening and Recruitment Management System

A Django-based Applicant Tracking System (ATS) designed to support end-to-end recruitment workflows, including candidate onboarding, resume screening, ATS scoring, and recruiter-side ranking.

This README is derived from the project developer documentation and adapted to the current repository structure.

## Project Overview

The system is intended to support two primary actors:
- Recruiters: create jobs, review candidates, and manage hiring status.
- Candidates: register, upload resumes, and apply for jobs.

Planned ATS workflow:
1. Recruiter publishes a job with requirements.
2. Candidate uploads a resume and applies.
3. Resume content is parsed and normalized.
4. ATS scoring computes relevance (for example, TF-IDF plus skill match).
5. Recruiters review ranked applicants and update application status.

## Current Repository Status

The current codebase includes:
- Core Django project setup
- PostgreSQL-backed configuration
- Custom user model and session tracking
- JWT authentication configuration
- Admin stack and API documentation dependencies

Some modules described in the full documentation (for example dedicated jobs, resumes, applications, and scoring apps) appear to be planned/partial and are not fully present in this snapshot.

## Technology Stack

- Python 3.x
- Django 6
- Django REST Framework
- SimpleJWT
- PostgreSQL
- drf-spectacular (OpenAPI/Swagger)
- django-filter
- django-cors-headers
- django-jazzmin
- django-ckeditor-5

## Key Architecture Notes

- Custom user model: configured via `AUTH_USER_MODEL = "user.User"`
- Database: PostgreSQL via environment-driven settings
- Authentication: JWT (access and refresh tokens)
- Pagination and filtering: global DRF defaults enabled
- API schema generation: drf-spectacular configured
- Static/media handling configured for development

## Project Structure

- `ResumeRanker/` - project configuration and settings
- `ResumeRanker/settings/` - base settings and Jazzmin settings
- `user/` - custom user domain (model, manager, migrations)
- `utils/` - shared base/utility models
- `static/` - local static assets
- `staticfiles/` - collected/generated static assets
- `manage.py` - Django management entry point

## Quick Start

### 1. Clone and enter project

```bash
git clone <your-repository-url>
cd ResumeRanker
```

### 2. Create and activate virtual environment

Windows (CMD):

```bat
python -m venv .venv
.venv\Scripts\activate
```

Alternative in this repository:

```bat
activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the repository root.

Suggested variables:

```env
DEBUG=True
SECRET_KEY=change-me
DB_NAME=ats_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
ACCESS_TOKEN_LIFETIME_MINUTES=5
REFRESH_TOKEN_LIFETIME_MINUTES=15
APP_DOMAIN=http://localhost:8000
```

Note: `SECRET_KEY` is required by JWT signing settings.

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start development server

```bash
python manage.py runserver
```

Admin panel:
- `http://127.0.0.1:8000/admin/`

## API and Documentation

The current root URL configuration exposes the admin route. API app routing may be added as modules are integrated.

When DRF routes are added, drf-spectacular is already available in dependencies/settings to support OpenAPI schema and Swagger UI wiring.

## Security and Validation Principles

Based on the developer documentation direction:
- Use UUID primary keys for non-enumerable identifiers
- Validate uploaded resume files at multiple layers
- Standardize API error response formats
- Apply strict permission checks by role
- Avoid trusting client-side file metadata

## Testing

Run tests with:

```bash
python manage.py test
```

As the domain apps expand, add focused tests for:
- authentication and permission boundaries
- file upload validation
- ATS scoring consistency
- recruiter applicant ranking behavior

## Deployment Direction

The developer documentation references Docker-based deployment (`Dockerfile` and `docker-compose.yml`) as the target production path.

For production hardening:
- set `DEBUG=False`
- configure strict `ALLOWED_HOSTS`
- secure secret management
- apply HTTPS and reverse proxy best practices
- configure static/media serving strategy

## Roadmap (Documentation-Aligned)

- Complete jobs, resumes, applications, and scoring modules
- Expose versioned API endpoints (for example `/api/v1/`)
- Implement end-to-end ATS scoring pipeline
- Add recruiter dashboards and ranked applicant views
- Expand automated test coverage and CI checks

## License

Add your project license here.

## Contact

Add maintainer/team contact details here.
