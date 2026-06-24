FROM node:20-alpine AS web-build
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

COPY apps/agent-api/requirements.txt apps/agent-api/requirements.txt
RUN pip install --no-cache-dir -r apps/agent-api/requirements.txt

COPY apps/agent-api ./apps/agent-api
COPY --from=web-build /web/out ./apps/web/out

WORKDIR /app/apps/agent-api
ENV PORT=8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
