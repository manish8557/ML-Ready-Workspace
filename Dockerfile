FROM continuumio/miniconda3:latest

# Install system dependencies including network tools
RUN apt-get update && apt-get install -y \
        protobuf-compiler \
        sudo \
        git \
        wget \
        curl \
        vim \
        nano \
        htop \
        build-essential \
        net-tools \
        iproute2 \
        procps \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install conda environment
COPY environment.yml /tmp/
RUN conda env create -f /tmp/environment.yml \
    && conda clean -afy \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    && rm /tmp/environment.yml

# Create user with configurable arguments
ARG username=mluser
ARG userid=1000
ARG home=/home/${username}
ARG workdir=${home}/ml-project

RUN adduser ${username} --uid ${userid} --gecos '' --disabled-password \
    && echo "${username} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${username} \
    && chmod 0440 /etc/sudoers.d/${username}

WORKDIR ${workdir}
RUN chown ${username}:${username} ${workdir}

USER ${username}
WORKDIR ${workdir}

ENV PATH /opt/conda/envs/ml-env/bin:$PATH

# Configure notebook diffing
RUN git-nbdiffdriver config --enable --global
RUN git config --global diff.jupyternotebook.command 'git-nbdiffdriver diff --ignore-details'

# Set up bash environment
COPY docker/bashrc.bash /tmp/
RUN cat /tmp/bashrc.bash >> ${home}/.bashrc \
    && echo "export PATH=\"${workdir}/docker/bin:$PATH\"" >> ${home}/.bashrc \
    && sudo rm /tmp/bashrc.bash

# Copy Jupyter configuration
COPY docker/jupyter_notebook_config.py /tmp/
RUN mkdir -p ${home}/.jupyter && \
    cp /tmp/jupyter_notebook_config.py ${home}/.jupyter/ && \
    sudo rm /tmp/jupyter_notebook_config.py

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create logs directory for TensorBoard
RUN mkdir -p ${workdir}/logs

# Create startup script for TensorBoard and Jupyter WITH git config
RUN echo '#!/bin/bash' > ${home}/start-services.sh && \
    echo '# Set up git config from environment variables' >> ${home}/start-services.sh && \
    echo 'if [ ! -z "$GIT_USER_NAME" ]; then' >> ${home}/start-services.sh && \
    echo '    git config --global user.name "$GIT_USER_NAME"' >> ${home}/start-services.sh && \
    echo '    echo "Git user.name set to: $GIT_USER_NAME"' >> ${home}/start-services.sh && \
    echo 'fi' >> ${home}/start-services.sh && \
    echo 'if [ ! -z "$GIT_USER_EMAIL" ]; then' >> ${home}/start-services.sh && \
    echo '    git config --global user.email "$GIT_USER_EMAIL"' >> ${home}/start-services.sh && \
    echo '    echo "Git user.email set to: $GIT_USER_EMAIL"' >> ${home}/start-services.sh && \
    echo 'fi' >> ${home}/start-services.sh && \
    echo '' >> ${home}/start-services.sh && \
    echo '# Start TensorBoard in background' >> ${home}/start-services.sh && \
    echo 'echo "Starting TensorBoard on port 6006..."' >> ${home}/start-services.sh && \
    echo 'tensorboard --logdir=${HOME}/ml-project/logs --host=0.0.0.0 --port=6006 --reload_interval 5 > ${HOME}/ml-project/tensorboard.log 2>&1 &' >> ${home}/start-services.sh && \
    echo '' >> ${home}/start-services.sh && \
    echo '# Wait a moment for TensorBoard to start' >> ${home}/start-services.sh && \
    echo 'sleep 2' >> ${home}/start-services.sh && \
    echo '' >> ${home}/start-services.sh && \
    echo '# Check if TensorBoard started successfully' >> ${home}/start-services.sh && \
    echo 'if ps aux | grep -q "[t]ensorboard"; then' >> ${home}/start-services.sh && \
    echo '    echo "TensorBoard started successfully"' >> ${home}/start-services.sh && \
    echo 'else' >> ${home}/start-services.sh && \
    echo '    echo "Warning: TensorBoard may not have started properly"' >> ${home}/start-services.sh && \
    echo 'fi' >> ${home}/start-services.sh && \
    echo '' >> ${home}/start-services.sh && \
    echo '# Start Jupyter Lab in foreground' >> ${home}/start-services.sh && \
    echo 'echo "Starting Jupyter Lab on port 8888..."' >> ${home}/start-services.sh && \
    echo 'echo "Access Jupyter at: http://localhost:8888"' >> ${home}/start-services.sh && \
    echo 'echo "Access TensorBoard at: http://localhost:6006"' >> ${home}/start-services.sh && \
    echo 'exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root' >> ${home}/start-services.sh && \
    chmod +x ${home}/start-services.sh

EXPOSE 8888 6006

# Use the startup script that launches both TensorBoard and Jupyter
CMD ["/home/mluser/start-services.sh"]