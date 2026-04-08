# Sử dụng Python 3.11 làm base
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết cho Playwright và Sherlock
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    git \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt cho Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy mã nguồn
COPY . .

# Expose port
EXPOSE 8000

# Chạy backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
