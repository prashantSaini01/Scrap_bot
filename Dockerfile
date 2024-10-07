# ARG for the port
ARG PORT=5000

# Use Cypress browsers as the base image
FROM cypress/browsers:latest

# Install Python 3 and pip with additional fixes
RUN apt-get update && apt-get install -y python3 python3-pip --fix-missing \
    && apt-get clean

# Set the user base directory for pip installations
RUN echo $(python3 -m site --user-base)

# Copy the requirements file
COPY requirements.txt .

# Set environment variables to ensure Python binaries are in PATH
ENV PATH=/home/root/.local/bin:$PATH

# Install Python dependencies separately for better error visibility
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port that the app will run on
EXPOSE $PORT

# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]

 