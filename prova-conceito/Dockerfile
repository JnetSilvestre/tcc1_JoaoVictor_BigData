# TCC2 / C2 - imagem de execucao compartilhada pelos tres papeis.
# Digest obtido no Docker Desktop do academico em E08-D05, linux/amd64.
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG VCS_REF=unrecorded
LABEL org.opencontainers.image.title="TCC2 PON C2" \
      org.opencontainers.image.revision="${VCS_REF}"

# Somente os modulos exigidos pela execucao HTTP; o oraculo C0 fica fora.
COPY --chown=10001:10001 pon/ ./pon/
COPY --chown=10001:10001 c1/__init__.py c1/client.py c1/protocol.py c1/state.py c1/service.py ./c1/

USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "-m", "c1.service"]
