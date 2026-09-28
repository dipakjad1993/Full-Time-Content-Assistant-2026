FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn>=22.0.0
COPY . .
EXPOSE 5000
ENV HOST=0.0.0.0 PORT=5000 SERP_PROVIDER=ddg_fallback
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=4)"
CMD ["gunicorn", "-w", "2", "--threads", "8", "--timeout", "300", "-b", "0.0.0.0:5000", "wsgi:app"]
