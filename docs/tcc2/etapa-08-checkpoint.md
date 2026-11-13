# Checkpoint compacto — Etapa 08 (13/11/2026)

## Situação comprovada
- Branch `tcc2/desenvolvimento`, `master` preservada.
- E08-I01 diagnóstico Git/Docker/WSL2 aprovado, conforme `docs/tcc2/etapa-08-diagnostico-rede.md`.
- E08-I02 parametrização mínima de host HTTP no commit `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91` aprovada no Windows: `Ran 42 tests in 11.564s`, OK, compilação 0, testes 0, Git limpo.
- Capturas E08-D04a/b e SHA-256 no diagnóstico; imagens originais ainda não versionadas.
- C0/C1 funcionalmente aprovados nos casos ensaiados, dois efeitos nos passos 3 e 7; referência `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f` intocada.

## Próximo incremento E08-I03
Obter no Windows digest e versão exata de `python:3.13-slim` para `linux/amd64`, identificar ID e plataforma, antes de criar Dockerfile(s) e `.dockerignore`. Depois construir/testar imagens dos serviços e registrar IDs/digests reais.

## Limites
Os 42 testes incluem mock de DNS; não comprovam C2. Não houve build Docker PON, rede Docker PON, equivalência C2, Kubernetes da aplicação, medições de desempenho ou arquivamento dos PNGs originais.
Não modificar `master`, não limpar o kind ou executar `docker system prune`. Figuras e monografia somente com resultados reais.
