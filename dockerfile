FROM python:3.11-slim

# Install required Python packages
RUN pip install requests

# Set working directory
WORKDIR /app

# Copy script
COPY upload_fhir.py /app/upload_fhir.py

# Set the entrypoint to the Python script
ENTRYPOINT []
# Default command to pull in ENV vars as arguments
CMD ["sh", "-c", "python upload_fhir.py \"$TGZ_FILE_URL\" \"$SERVER_URL\""]