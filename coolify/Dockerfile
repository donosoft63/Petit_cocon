FROM python:3.12-slim AS release
WORKDIR /build
COPY Petit-Cocon-serveur-3.0.0.zip coolify/prepare_release.py ./
RUN python -B prepare_release.py

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 COCON_DATA=/data COCON_PUBLIC=/app/public
WORKDIR /app
COPY --from=release /build/release/server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd -u 10001 -m cocon \
    && mkdir /data \
    && chown cocon /data
COPY --from=release /build/release/server/server.py /build/release/server/accounts.py ./
COPY --from=release /build/release/app/src/main/assets ./public
USER cocon
EXPOSE 8080
VOLUME ["/data"]
CMD ["python", "server.py"]
