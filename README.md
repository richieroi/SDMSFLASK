# School Management CRUD Application

A simple CRUD application built with Flask and Microsoft SQL Server.

## Features

- Create, read, update, and delete student records
- Responsive web interface
- Data stored in Microsoft SQL Server

## Prerequisites

- Python 3.8+
- Microsoft SQL Server
- ODBC Driver for SQL Server

## Installation

1. Clone this repository
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Make sure your SQL Server is running and accessible:
   - Server: DESKTOP-170MKOG
   - Database: School_Management_198
   - Authentication: Windows Authentication

## Running the Application

1. Start the Flask development server:

```
python app.py
```

2. Open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

## Database Configuration

The application is configured to connect to SQL Server using:
- Windows Authentication
- Database name: School_Management_198
- Server: DESKTOP-170MKOG

If you need to modify these settings, please update them in the `config.py` file.
