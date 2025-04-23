# Image base
FROM python:3.11

# Set environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working dir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz && tar -xzvf dockerize-linux-amd64-v0.6.1.tar.gz && mv dockerize /usr/local/bin/

# Command to run
CMD ["gunicorn", "rental.wsgi:application", "--bind", "0.0.0.0:8000"]
