# Pixelebbe

Pixelebbe is like Pixelflut, but slower.
Get your hacker friends together and fill the canvas with color!
Submit your pixel change requests via word-of-mouth, Eventphone DECT Call, a phone tree or fax.
We also accept ChaosPost!

## Features (not fully implemented)

- Multiple Events
- a very simple to use API to set pixels
- a beatuiful color palette
- Adjustable canvas sizes per event
- Pixel history tracking
- Rate limiting to prevent troll abuse

## Current State of the codebase

The codebase currently implements:

- Basic Flask application setup with SQLAlchemy and migrations
- A predefined color palette with 32 colors (for now)

Still in development:
- Event management system for handling multiple canvases
- Admin interface for event configuration
- API endpoints for pixel manipulation
- Rate limiting implementation
- User authentication system
- Pixel history visualization

## Requirements

- Python 3.6+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Pillow (Python Imaging Library)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pixelebbe.git
cd pixelebbe
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example configuration file and modify it:
```bash
cp config.py.example config.py
```

5. Initialize the database:
```bash
python setup.py
```

## Configuration

Modify your config.py file to suit your needs.

## Running the Application

To start the development server:

```bash
FLASK_DEBUG=1 flask run
```

The application will be available at `http://localhost:5000`

## Database Migrations

When you make changes to the database models in `database.py`, you need to create and apply migrations:

1. Create a new migration:
```bash
flask db migrate -m "Description of your changes"
```

2. Review the generated migration file in the `migrations/versions` directory

3. Apply the migration:
```bash
flask db upgrade
```
