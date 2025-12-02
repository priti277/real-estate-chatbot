# 🏢 Real Estate Analysis Chatbot

A full-stack web application that analyzes real estate data through a conversational AI interface. Built with React frontend and Django backend.


##  Features

- **Chat Interface**: Natural language queries about real estate
- **Data Analysis**: Process Excel datasets for real estate insights
- **Visualizations**: Interactive charts (price trends, demand analysis)
- **Smart Summaries**: AI-powered natural language summaries
- **File Upload**: Upload custom Excel data files
- **Comparison Tool**: Compare multiple areas side-by-side

##  Tech Stack

### Frontend
- React.js
- Bootstrap 5
- Chart.js
- Axios

### Backend
- Django 5.0
- Django REST Framework
- Pandas (Excel processing)
- SQLite

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip and npm

### Backend Setup
```bash
# Clone repository
git clone https://github.com/priti277/real-estate-chatbot
cd real-estate-chatbot

# Install Python dependencies
pip install django djangorestframework django-cors-headers pandas openpyxl

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start Django server
python manage.py runserver
