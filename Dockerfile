FROM python:3.10-slim
# Set the working directory in the container
WORKDIR /usr/src/app
# Copy the requirements file into the container
RUN useradd -m -s /bin/bash warp && \
    mkdir -p /home/warp/.local/share/warp && \
    echo -n 'yes' > /home/warp/.local/share/warp/accepted-tos.txt && \
    chown -R warp:warp /usr/src/app /home/warp
USER warp
COPY libs.txt ./
COPY ./start.sh /usr/src/app/
# Install any needed packages specified in libs.txt
RUN pip install --no-cache-dir -r libs.txt
# Install additional dependencies
RUN apt-get update && \
    apt-get install -y unar unzip ffmpeg git gnupg curl lsb-release && \
    curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/cloudflare-client.list && \
    apt-get update && \
    apt-get install -y cloudflare-warp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Start the Cloudflare WARP service
RUN git config --global --add safe.directory /usr/src/app && \
    chmod +x /usr/src/app/start.sh 
    # echo "warp ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/warp && \
# Set ENTRYPOINT to run your Python script
ENTRYPOINT ["./start.sh"]