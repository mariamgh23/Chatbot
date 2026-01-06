# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8501

# Create a script to start Ollama and then the Streamlit app
RUN echo '#!/bin/bash\n\
ollama serve > /dev/null 2>&1 &\n\
sleep 5\n\
ollama pull llama3\n\
streamlit run chatbot_app.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Run the start script
CMD ["/app/start.sh"]
