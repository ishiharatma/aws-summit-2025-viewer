FROM ubuntu:22.04

# 追加パッケージをインストール
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    python3 \
    python3-pip \
    python3-pygame \
    curl \
    unzip \
    fontconfig \
    fonts-dejavu-core \
    graphviz \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# vscodeユーザーを作成し、sudoersに追加
RUN useradd -m vscode -s /bin/bash && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode && \
    chmod 0440 /etc/sudoers.d/vscode

# vscodeユーザーに切り替え
USER vscode
WORKDIR /home/vscode

# Amazon Q CLIをvscodeユーザーとしてインストール
RUN curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux-musl.zip" -o "/tmp/q.zip" && \
    cd /tmp && \
    unzip q.zip && \
    cd q && \
    ./install.sh --no-confirm&& \
    cd / && \
    sudo rm -rf /tmp/q && \
    sudo rm -f /tmp/q.zip

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# add .local/bin to PATH
ENV PATH="/home/vscode/.local/bin:${PATH}"
