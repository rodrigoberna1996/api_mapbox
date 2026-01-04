FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 1) Instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 2) Crear usuario no-root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# 3) Copiar código con ownership correcto
COPY --chown=appuser:appgroup app /app/app
COPY --chown=appuser:appgroup alembic /app/alembic
COPY --chown=appuser:appgroup alembic.ini /app/alembic.ini

USER appuser

EXPOSE 8000

CMD ["gunicorn","app.main:app","-k","uvicorn.workers.UvicornWorker","-w","2","--timeout","120","--keep-alive","5","-b","0.0.0.0:8000","--access-logfile","-","--error-logfile","-"]