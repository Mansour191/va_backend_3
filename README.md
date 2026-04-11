# VynilArt Backend

Django GraphQL API backend with WebSockets support.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Start development server:
```bash
python manage.py runserver
```

## Features

- GraphQL API with GraphiQL interface at `/graphql/`
- Django admin at `/admin/`
- CORS support for frontend development
- WebSockets support via Channels
- Redis for channel layers

## Environment Variables

Copy `.env` file and configure as needed for production.

## GraphQL

Access GraphiQL interface: http://localhost:8000/graphql/

## Development

The project uses:
- Django 6.0.3
- Graphene for GraphQL
- Channels for WebSockets
- Redis for background processing
