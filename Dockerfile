# ARG for the port
ARG PORT=5000
 
# Use Cypress browsers as the base image
FROM cypress/browsers:latest
 
# Clean up duplicate Microsoft Edge source list to avoid conflict
RUN rm -f /etc/apt/sources.list.d/microsoft-edge-stable.list
 
# Install Python 3.6, wget, and curl (to fetch get-pip.py)
RUN apt-get update && apt-get install -y python3.6 wget curl --fix-missing \
&& apt-get clean
 
# Use curl to install pip for Python 3.6 in the user directory
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6 - --user
 
# Set environment variables to ensure the user's pip installation is accessible
ENV PATH=/root/.local/bin:$PATH
 
# Copy the requirements file
COPY requirements.txt .
 
# Install Python dependencies from requirements.txt using the user-installed pip
RUN /root/.local/bin/pip install --no-cache-dir -r requirements.txt
 
# Copy the entire application code into the container
COPY . .
 
# Expose the port that the app will run on
EXPOSE $PORT
 
# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]