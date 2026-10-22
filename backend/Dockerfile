# Use a lightweight official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (app.py and model file)
COPY app.py .
COPY superkart_model.joblib .

# Expose port 7860 which is the standard port for Hugging Face Spaces / custom apps
EXPOSE 7860

# Command to run the Flask application
CMD ["python", "app.py"]
