FROM python:3.10
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Создание рабочей директории
WORKDIR /app

# Копирование файла зависимостей
COPY requirements.txt /app/

# Обновление pip и установка виртуального окружения
RUN python -m pip install --upgrade pip \
    && python -m venv /venv \
    && /venv/bin/pip install --upgrade pip setuptools wheel

# Установка зависимостей в виртуальное окружение
RUN /venv/bin/pip install -r requirements.txt

# Копирование оставшихся файлов
COPY . .

# Установка переменной окружения для использования виртуального окружения
ENV PATH="/venv/bin:$PATH"
