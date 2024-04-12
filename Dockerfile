# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variable to avoid buffering Python output
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /home/app

# Copy requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /home/app
COPY . .

# Run database migrations
RUN python manage.py migrate

# Command to run the Django development server
CMD ["gunicorn", "config.wsgi"]