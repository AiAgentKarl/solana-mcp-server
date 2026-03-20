FROM python:3.12-slim

LABEL maintainer="AiAgentKarl"
LABEL description="Solana MCP Server — Blockchain-Daten, DeFi-Yields, Token-Sicherheit"

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

# Standardmaessig SSE-Transport fuer Docker-Nutzung
ENV MCP_TRANSPORT=sse
ENV MCP_PORT=8000

CMD ["python", "-m", "src.server"]
