# TCC2 / C2 - imagem de execucao compartilhada pelos tres papeis.
# Digest de manifesto linux/amd64 listado no registro em E08-D07.
# E08-D08 deve confirmar a resolucao direta antes de aprovar o build.
FROM python:3.13-slim@sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20

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
