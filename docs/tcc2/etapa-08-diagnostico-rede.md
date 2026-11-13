# TCC2 — Etapa 08: diagnóstico e parametrização da rede Docker

**Data de abertura:** 13/11/2026. **Branch de trabalho:** `tcc2/desenvolvimento`.  
**Referência C1 comprovada:** `be6b850d599504e9ea8166f02fd87b35313e5445`.  
**HEAD inicial da Etapa 08 após sincronização:** `3dadef829846fdf5f0bcf0c47c956b44eb89d821`.  
**Estado:** E08-I01 e E08-I02 aprovados no Windows; E08-I03 (imagens Docker) ainda em preparação. Nenhum build C2 executado.

## 1. Evidências reais recebidas

- **E08-D01:** PowerShell confirma branch `tcc2/desenvolvimento`, status limpo, Python 3.13.9, pip 25.2, Git 2.45.0.windows.1; HEAD local antes da sincronização `be6b850d599504e9ea8166f02fd87b35313e5445`, remoto `3dadef829846fdf5f0bcf0c47c956b44eb89d821`.
- **E08-D02:** Docker Desktop 4.99.0, Engine 29.9.3, contexto `desktop-linux`, 8 CPUs lógicas, 8.245.645.312 bytes configurados; WSL2 ativo; contêineres do kind preservados; `tcc2-python-validacao` parado com Exit 0; cluster `tcc2-pon` existente. Nenhuma limpeza executada.
- **E08-D03:** `git pull --ff-only` concluiu, apenas sete arquivos documentais diferiam desde C1; HEAD `3dadef829846fdf5f0bcf0c47c956b44eb89d821`; `compileall` exit 0; `unittest` **Ran 39 tests in 10.813s, OK, Testes: 0**; Git final limpo. A duração é da suíte, **não benchmark PON**.

## 2. Arquivos originais das capturas e hashes SHA-256

Os hashes abaixo foram calculados sobre os bytes dos PNGs recebidos nesta conversa. Os originais **não foram arquivados neste repositório**.

| ID | Arquivo | SHA-256 |
|---|---|---|
| E08-D03a | `image(20261113-195923).png` | `4227f659f596a4ec9b2622af141f6651afc22a72acbb83a6119f4b2702f96d72` |
| E08-D03b | `image(20261113-195935).png` | `33cdd6903b39bf3abeeaa136caa5f74511e9d9efb19567155fe5d82dea89c97b` |

## 3. Diagnóstico de C1 e decisão para E08-I02

- `c1/service.py` atende HTTP serial em `127.0.0.1` e propaga mensagens por porta numérica downstream.
- `c1/client.py` constrói URLs `http://127.0.0.1:<port>`; isso não atravessa contêineres separados.
- `c1/runner.py` e `c1/snapshot_race.py` devem conservar a operação local/localhost do C1 já validado.
- As classes de estado, contratos, fixture e oráculo permanecem sem alterações; a prova Python não equivale ao NOP Query C++ nem processa vídeos.
- Para C2, permitir `--listen-host 0.0.0.0` somente no contêiner, `--downstream-host` resolvido via DNS de rede Docker definida pelo projeto, e porta interna explícita (prevista: 8080). **Não publicar portas indiscriminadamente no host.**

## 4. Incremento E08-I02 — mudança sob validação

Arquivos: `prova-conceito/c1/client.py`, `c1/service.py`, `tests/test_c2_network_config.py`. Defaults C1 de `127.0.0.1` são mantidos. A única mudança é parametrização do endereço de escuta e do cliente; não modificar máquinas de estado nem payloads. Três novos testes isolados verificam URL, encaminhamento de snapshot via hostname e CLI (C1 padrão e C2 parametrizado).

**E08-I02 aprovado por evidência real:** HEAD `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`, compilação 0, 42 testes OK e `Testes: 0` no Windows. Ainda não houve execução de rede Docker.

## 5. Comando de validação local após atualizar a branch

```powershell
Set-Location "$HOME\tcc2\etapa07\tcc2-trabalho"
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\prova-conceito
python -m compileall -q pon c0 c1 tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
git status --short
```

## 6. Limites e próximo marco

Não afirmar que há rede Docker ou contêineres PON rodando neste marco. A próxima etapa após regressão é o desenho dos Dockerfiles e do processo de construção/rastreio de imagens; antes disso, arquivar a prova de regressão e investigar qualquer falha. Kubernetes e distribuição entre nós permanecem Etapas 09–10. Dados reais futuros deverão alimentar diagramas e tabelas da monografia na Etapa 13.

## 7. E08-D04 — regressão real no Windows (13/11/2026)

- Fast-forward até `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`, branch `tcc2/desenvolvimento`.
- `Compilacao: 0`; `Ran 42 tests in 11.564s`; `OK`; `Testes: 0`; Git final sem alterações.
- Três novos testes verificam configuração de hostname/CLI com mocks: aprovação funcional de parametrização, não prova de comunicação Docker.
- A duração 11,564 s é da suíte, não medição de desempenho PON.

| Evidência | PNG original | Bytes | SHA-256 calculado dos bytes recebidos |
|---|---|---:|---|
| E08-D04a | `image(20261113-200758).png` | 144367 | `a38669c521c23456f85d43356bfacab58646260b6a8d74c85b3f491d0dbd0d33` |
| E08-D04b | `image(20261113-200811).png` | 71318 | `f8a00645992c6e21a0fa7957f958a5778b293eae798a15c941bef7bef90875f3` |

PNG originais recebidos nesta conversa, ainda não publicados no repositório.

## 8. Próximo passo E08-I03 — procedência da imagem base

Consultar no Windows a versão Python, arquitetura, imagem ID e RepoDigests da imagem oficial `python:3.13-slim` após download com plataforma `linux/amd64`. Registrar digest obtido para então criar Dockerfile(s) com base congelada, `.dockerignore` e builds de serviço. Não utilizar Docker/Kubernetes como evidência de execução da aplicação até os testes efetivos de C2.
