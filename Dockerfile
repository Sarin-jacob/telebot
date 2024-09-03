FROM python:3.10-slim
# Copy the requirements file into the container
COPY libs.txt ./
COPY ./start.sh /start.sh
# Install any needed packages specified in libs.txt
RUN pip install --no-cache-dir -r libs.txt
# Install additional dependencies
RUN apt-get update && \
    apt-get install -y unar unzip ffmpeg git gnupg curl sudo lsb-release && \
    curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/cloudflare-client.list && \
    apt-get update && \
    apt-get install -y cloudflare-warp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    git config --global --add safe.directory /usr/src/app && \
    useradd -m -s /bin/bash warp && \
    chmod a+x /start.sh && \
    mkdir -p /home/warp/.local/share/warp && \
    echo -n 'yes' > /home/warp/.local/share/warp/accepted-tos.txt && \
    echo "warp ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/warp
ENV DOCKERVERSION=27.2.0
RUN curl -fsSLO https://download.docker.com/linux/static/stable/${uname -m}/docker-${DOCKERVERSION}.tgz \
    && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 \
                    -C /usr/local/bin docker/docker \
    && rm docker-${DOCKERVERSION}.tgz
    
USER warp
# Set the working directory in the container
WORKDIR /usr/src/app
# Set ENTRYPOINT to run your Python script
ENTRYPOINT ["/start.sh"]