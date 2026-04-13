FROM python:3.12-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY logos/ logos/

# Install with HTTP extras (includes mcp, uvicorn, starlette)
RUN pip install --no-cache-dir -e ".[http]"

EXPOSE 8000

CMD ["python", "-m", "logos.mcp_server_http"]
