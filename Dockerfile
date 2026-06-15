# 日本立直麻将识别系统 - Docker 训练环境
# 基于 NVIDIA CUDA 12.4 + cuDNN

FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python 3.11 为默认
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# 升级 pip
RUN python -m pip install --upgrade pip

# 安装 Python 依赖
COPY requirements-train.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# 创建工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 创建数据目录（会被 volume 覆盖）
RUN mkdir -p data/yolo_dataset data/datasets runs

# 设置入口点
ENTRYPOINT ["python"]

# 默认命令（可以被 docker-compose 覆盖）
CMD ["scripts/train_yolo.py", "--help"]