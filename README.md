# YouClone - Django YouTube Clone

YouClone is a YouTube-inspired video sharing platform built with Django.  
It allows users to upload videos, watch content, interact through comments, and subscribe to channels.

This project demonstrates a real-world backend architecture using Django models, class-based views, authentication, and relational database design.

---

## Features

- User authentication system
- Upload and watch videos
- Video thumbnails
- Video views counter
- Comment system
- Like / Dislike reactions
- Subscribe / Unsubscribe channels
- View history tracking
- Pagination for video feed
- Responsive YouTube-style UI

---

## Tech Stack

Backend:
- Django
- Python
- MySQL

Frontend:
- HTML
- CSS
- Bootstrap / Tailwind CSS

Other Tools:
- Git
- GitHub

---

## Project Structure
YouClone/
│
├── users/ # Custom user system
├── videos/ # Video upload & playback
├── comments/ # Comment system
├── subscriptions/ # Channel subscriptions
│
├── templates/
├── static/
├── media/
│
└── manage.py


---

## Installation

Clone the repository:
git clone https://github.com/yourusername/youclone.git

cd youclone


Create virtual environment:
python -m venv venv


Activate environment:

Windows
venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt

Run migrations:
python manage.py migrate


Create superuser:
python manage.py createsuperuser


Run development server:
python manage.py runserver


Open browser:
http://127.0.0.1:8000/


---

## Key Learning Concepts

This project demonstrates:

- Django class-based views
- Database relationships
- User authentication
- File uploads
- Model design for scalable applications
- Real-world backend architecture

---

## Future Improvements

- Video streaming optimization
- Channel pages
- Notifications
- Search functionality
- Recommendation system
- REST API with Django REST Framework

---

## License

This project is built for learning and portfolio purposes.

