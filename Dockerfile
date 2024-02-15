# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-bullseye

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

RUN pip install --upgrade pip setuptools

# RUN apt-get update && apt-get install -y libpq-dev

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000


# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
