# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY libs.txt ./

# Install any needed packages specified in libs.txt
RUN pip install --no-cache-dir -r libs.txt

# Install additional dependencies
RUN apt-get update && \
    apt-get install -y unar unzip ffmpeg git gnupg curl lsb-release && \
    curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/cloudflare-client.list && \
    apt-get update && \
    apt-get install -y cloudflare-warp && \
    warp-cli register && \
    warp-cli connect && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Run the application
ENTRYPOINT ["python", "bot.py"]