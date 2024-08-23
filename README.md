# Social Networking Application API

## Overview

This project is a social networking application API built with Django and Django REST Framework. It includes
functionalities for user authentication, managing friend requests, and retrieving friend-related data.

## Features

- User authentication (login/signup using email)
- Send, accept, and reject friend requests
- List friends (users who have accepted friend requests)
- List pending friend requests (received but not yet responded to)
- Rate limit for sending friend requests (maximum 3 requests per minute)

# Setup

### Prerequisites

- Python 3.10
- Django 5.x
- Django REST Framework 3.x
- Django REST Framework JWT (or similar JWT library)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/azharajmeri/accuknox-social-networking-application.git
   cd accuknox-social-networking-application
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
   
4. **Run Migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
   
5. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```
   