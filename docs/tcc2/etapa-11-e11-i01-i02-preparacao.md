# TCC2 — Etapa 11 / E11-I01-I02: preparacao de instrumentos

**Estado:** scripts preparados na branch tcc2/desenvolvimento, SEM execucao dos testes no Windows, SEM criacao de nova bancada e SEM benchmark. Nao promover codigo escrito a teste aprovado.

## Componentes e decisoes
- prova-conceito/benchmark/fixtures.py: cargas 100, 1000, 10000; seeds 20260501/20260502/20260503; padrao de oito passos com dois efeitos por ciclo completo e valor alto de atA variando deterministicamente. As cargas ainda nao estao congeladas como serie definitiva.
- benchmark/client.py: processo persistente serial, um lote de POSTs, tempo monotônico por request e lote; o servico original usa HTTP/1.0, logo nao supor conexao TCP persistente.
- benchmark/collector.py: Kubelet Summary API, contador acumulado CPU por container, workingSetBytes amostrado por container e rede por Pod; qualidade de amostras validada por timestamp.
- benchmark/evidence.py: valida respostas, oraculo e estado final; gera SHA-256 e ZIP imutavel.
- benchmark/prepare.py: derivacao de YAML para novo namespace E11 e Pod cliente (mesma imagem C2); **apenas gera arquivo, nunca aplica**.
- benchmark/runner.py: valida namespace isolado e estado frio; sem flag --execute imprime plano; com flag **MUTANTE**, faz um snapshot, um lote com uma invocacao remota de processo e evidencia; nao repetir apos falha.
- tests/test_benchmark.py: testes sintéticos de reprodutibilidade, isolamento, métricas e oráculo, sem Kubernetes ou rede.

## Pendencias antes do piloto
1. Sincronizar o Git local e executar python -m compileall / unittest no Windows; relatar saídas. Nenhuma execucao de scripts novos foi comprovada ate agora.
2. Gerar fixtures e YAML em resultados-locais, conferir hashes e verificar kubectl apply --dry-run=client sem aplicar manifestos.
3. Ajustar timeouts, validar codigo e aceitar metodo de amostragem. Incluir C2 com cliente em rede Docker antes da bateria principal.
4. Definir a posicao do cliente gerador (worker para C3 e C4), carga do Pod cliente no host e efeito na comparabilidade; medir C2 com gerador similar.
5. Quando aprovado, criar uma bancada nova por piloto. Nao reutilizar tcc2-pon e tcc2-pon-c4; nao reiniciar, escalar, excluir ou reenviar evento para Pods existentes.
6. Depois do piloto, auditar os dados reais e apenas entao congelar protocolo, repeticoes e serie cientifica.

## Comandos somente de validacao (na raiz do repositorio, PowerShell)

~~~powershell
git branch --show-current
git status --short
git pull --ff-only --quiet origin tcc2/desenvolvimento
Set-Location prova-conceito
python -m compileall -q benchmark tests/test_benchmark.py
python -m unittest discover -s tests -p 'test_benchmark.py' -v
python -m benchmark.fixtures --output resultados-locais/e11-fixtures
python -m benchmark.prepare --scenario C3 --label p01 --output resultados-locais/e11-c3-p01.yaml
python -m benchmark.prepare --scenario C4 --label p01 --output resultados-locais/e11-c4-p01.yaml
python -m benchmark.runner --scenario C3 --label p01 --run-id e11-c3-p01 --fixture resultados-locais/e11-fixtures/s100/inputs.jsonl --output resultados-locais/e11-plan
~~~

**ATENCAO:** os comandos acima nao incluem --execute nem kubectl apply, nao criam Pods e nao executam benchmark. Nao os repetir com diretorios de saida existentes sem preservar dados.

## Divisao de responsabilidades
Perplexity pesquisara apenas lacunas metodologicas selecionadas, com fontes verificaveis, sem inventar DOI. ChatGPT avalia codigo/instrumentacao e integra relatos; o host Windows executa testes e medicoes. Work/Overleaf entram na construcao e auditoria final do LaTeX apos os resultados da Etapa 12.
