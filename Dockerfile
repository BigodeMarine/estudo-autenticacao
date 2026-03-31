FROM python:3.13-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Adiciona poetry ao PATH
ENV PATH="/root/.local/bin:$PATH"

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY pyproject.toml poetry.lock* ./

# Configura poetry (sem criar virtualenv)
RUN poetry config virtualenvs.create false

# Instala dependências
RUN poetry install --no-root

# Copia restante do projeto
COPY . .

# Porta da API
EXPOSE 8000

# Comando para rodar API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]