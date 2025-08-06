# College News Portal

A professional Django-based news management system for educational institutions. This platform allows users to create, manage, and publish news articles with a modern, responsive interface.

## Features

- **Article Management**: Create, edit, and delete articles with rich text editing
- **Category System**: Organize articles by categories
- **User Authentication**: Secure login/logout system
- **Comment System**: Allow readers to comment on articles
- **Search Functionality**: Search articles by title, content, or excerpt
- **Responsive Design**: Mobile-friendly interface
- **Admin Dashboard**: User-friendly dashboard for content management
- **Image Upload**: Support for featured images on articles

## Technology Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Image Processing**: Pillow
- **Rich Text Editor**: CKEditor
- **Caching**: Redis
- **Task Queue**: Celery

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd college-news-portal
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
college_news_portal/
├── college_news/          # Main project settings
├── news/                  # News application
│   ├── models.py         # Database models
│   ├── views.py          # View logic
│   ├── forms.py          # Form definitions
│   ├── urls.py           # URL routing
│   └── templates/        # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded files
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── README.md            # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string
- `EMAIL_*`: Email configuration
- `REDIS_URL`: Redis connection string (for caching)

### Database Configuration

The project supports multiple database backends:

- **SQLite** (default for development)
- **PostgreSQL** (recommended for production)

### Static Files

Static files are served using WhiteNoise in production. Configure your web server to serve static files from the `staticfiles` directory.

## Usage

### Creating Articles

1. Log in to your account
2. Navigate to the dashboard
3. Click "Create Article"
4. Fill in the article details
5. Set the status to "Published" to make it public

### Managing Categories

1. Access the category management section
2. Create, edit, or delete categories as needed
3. Assign articles to appropriate categories

### User Management

- Use Django admin panel for user management
- Regular users can create and manage their own articles
- Superusers have access to all features

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy

### Recommended Deployment Options

- **Heroku**: Easy deployment with PostgreSQL add-on
- **DigitalOcean**: App Platform or Droplet with Docker
- **AWS**: Elastic Beanstalk or EC2
- **Google Cloud**: App Engine or Compute Engine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Contact the development team
- Check the documentation

## Changelog

### Version 1.0.0
- Initial release
- Basic article management
- User authentication
- Category system
- Comment functionality 