# NASA Space Explorer

A comprehensive web application that allows users to explore various aspects of space through NASA's APIs. The application features:

- Astronomy Picture of the Day (APOD)
- Mars Rover Photo Explorer
- Near Earth Object (NEO) Tracker
- Earth Observation Dashboard
- International Space Station (ISS) Tracker

## Features

- User authentication system
- Responsive and modern UI design
- Real-time data from NASA APIs
- Interactive visualizations
- Favorite content saving
- Detailed information about space objects

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- NASA API key (get one at https://api.nasa.gov)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nasa-space-explorer.git
cd nasa-space-explorer
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your NASA API key:
```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
NASA_API_KEY=your-nasa-api-key-here
DATABASE_URL=sqlite:///nasa_explorer.db
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
nasa-space-explorer/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── apod.py
│   │   ├── mars.py
│   │   ├── neo.py
│   │   ├── earth.py
│   │   └── iss.py
│   ├── services/
│   │   └── nasa_api.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── base.html
│       └── components/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA for providing the APIs
- Bootstrap for the UI framework
- Font Awesome for the icons 