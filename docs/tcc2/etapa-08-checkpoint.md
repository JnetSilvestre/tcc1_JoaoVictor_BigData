# Checkpoint compacto — Etapa 08 (13/11/2026)

## Situação comprovada
- Branch `tcc2/desenvolvimento`, `master` preservada.
- E08-I01 diagnóstico Git/Docker/WSL2 aprovado, conforme `docs/tcc2/etapa-08-diagnostico-rede.md`.
- E08-I02 parametrização mínima de host HTTP no commit `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91` aprovada no Windows: `Ran 42 tests in 11.564s`, OK, compilação 0, testes 0, Git limpo.
- Capturas E08-D04a/b e SHA-256 no diagnóstico; imagens originais ainda não versionadas.
- C0/C1 funcionalmente aprovados nos casos ensaiados, dois efeitos nos passos 3 e 7; referência `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f` intocada.

## Próximo incremento E08-I03
E08-D05 aprovado: imagem `python:3.13-slim` Linux/amd64, Python 3.13.18, digest `sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`; print `image(20261113-201558).png`, SHA-256 `39a2f3eb7a4b57cb4b9e9138b42b544984ffdc2a73a081856413d0a6da8173ef`. `prova-conceito/Dockerfile` e `.dockerignore` publicados, ainda não executados no Windows. **E08-D06 falhou:** `docker build` retornou 1, sem criar imagem; resolução do digest em `FROM ...@sha256:e48f59...` recebeu `not found`. Evidência PNG original `image(20261113-203658).png`, SHA-256 `93822efcdbd3fc2aa816ed6aae7592e63b25606b42d7005430f2aa21a4fe03cd`. Próximo: inspecionar manifestos remotos via `docker buildx imagetools inspect`, comparar com imagem local, corrigir somente referência de base após confirmação; repetir build e smoke test.

## Limites
Os 42 testes incluem mock de DNS; não comprovam C2. Não houve build Docker PON, rede Docker PON, equivalência C2, Kubernetes da aplicação, medições de desempenho ou arquivamento dos PNGs originais.
Não modificar `master`, não limpar o kind ou executar `docker system prune`. Figuras e monografia somente com resultados reais.
