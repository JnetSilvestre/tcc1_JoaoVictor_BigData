# TCC2 — E11-M00C — Auditoria de 65 testes e 3 inventários reais somente leitura

**Data da evidência:** 17/11/2026 (America/Sao_Paulo), conforme nome do arquivo temporário fornecido; **data da auditoria:** 17/11/2026.  
**Branch:** `tcc2/desenvolvimento`. **Base de prova:** texto integral de stdout/stderr do PowerShell enviado pelo acadêmico como `Texto colado(1).txt` nesta conversa. Não existe no repositório cópia binária desse TXT nem do JSON temporário. **Nenhum comando deste laudo foi executado pelo assistente.**

## 1. Identidade da revisão e regressão

- `git pull --ff-only origin tcc2/desenvolvimento`: fast-forward `4ba69a3...` para **`f8b12606616fd6e13249a730a0ef8dbad4508d80`**, conforme saída.
- `git rev-parse HEAD`: **`f8b12606616fd6e13249a730a0ef8dbad4508d80`**.
- `python -m compileall -q benchmark tests` seguido de guarda `$LASTEXITCODE`: **`COMPILACAO: PASS`**.
- `python -m unittest discover -s tests -p "test_benchmark*.py" -v`: **`Ran 65 tests in 0.311s`**, `OK`, `TESTES: PASS`; todos os 65 casos listados estão marcados `ok`.
- Os casos novos `test_actual_uninitialized_states_are_not_falsely_rejected` e `test_contract_using_real_c1_state_classes_no_network` aparecem explicitamente como `ok`. Isso supera a divergência de mock identificada no laudo anterior: `LogicEngine.attributes/condition=None` e `RuleExecutor.approved=None` antes de snapshot.
- `0.311s` é tempo da **suíte sintética**, NÃO de benchmark/lote e não é comparável com durações das cargas históricas.
- A saída final não exibe explicitamente o resultado de `git status --porcelain` (o comando estava no script). **Não inferir integridade da árvore a partir de ausência de linha no trecho final, embora não haja alteração local relatada.**

**Decisão:** `E11_M00C_65_UNIT_TESTS_PASS_FOR_SHA_f8b1260`.

## 2. Inventário read-only com ambiente real

Após a suíte, o script criou 3 chamadas a `capture_environment(cenario, run_id)` (para C2, C3, C4) **sem `--execute`** e reportou:

```text
C2: ENVIRONMENT_READ_ONLY_PASS
C3: ENVIRONMENT_READ_ONLY_PASS
C4: ENVIRONMENT_READ_ONLY_PASS
RAM_WINDOWS_LIVRE_BYTES: 2159898624
DISCO_LIVRE_BYTES: 72307068928
ARQUIVO: C:\Users\JOOVIC~1\AppData\Local\Temp\tcc2-m00c-ambiente-20261117-192218.json
```

- A RAM Windows disponível reportada nessa consulta foi **2.159.898.624 bytes = ~2,01 GiB**. Isso é uma leitura pontual e **não** implica insuficiência nem aprovação automática da capacidade de uma nova bancada.
- O espaço livre no volume que contém a pasta do projeto foi **72.307.068.928 bytes = ~67,34 GiB**, também instantâneo.
- Os resultados C3/C4 indicam que a função completou a consulta `kubectl ... get nodes` e o código registrou nodes Ready, mas **o conteúdo integral das seções JSON não foi exibido na transcrição**. Não declarar novos UIDs ou valores de `allocatable` comparativos além dos inventários anteriores documentados.
- `environment_snapshot.py` consulta Docker context, cgroup/CPU/RAM anunciado, ID da imagem e Git; no Windows usa `powershell.exe -NoProfile -NonInteractive` e `Get-CimInstance`. **Um PASS significa que as chamadas read-only do script concluíram**, não que as quotas cgroup dos novos contêineres foram demonstradas.
- O script emitiu checksum `SHA256 7962B6F10BE59D93989AB064BA58C1E1449AFB94BCF6BEF29C9728CE3C8B7F9D` para o arquivo JSON temporário acima. **Não foi possível recalcular esse SHA no ambiente do assistente**, pois os bytes do JSON local do usuário não foram enviados; registrar como SHA *reportado*.
- O caminho temporário é local do acadêmico, **não** equivale à cópia arquivada no GitHub/Overleaf. Preservar se for utilizar como evidência integral; o laudo registra seu hash para futura comparação.

## 3. Status dos gates e limitações de inferência

| Controle | Estado após esta evidência |
|---|---|
| Branch/HEAD e fast-forward | `PASS_REPORTED` — SHA f8b1260 |
| Compilação Python | `PASS` |
| 65/65 testes sintéticos incluindo 2 contratos reais | `PASS` |
| Inventário real read-only C2/C3/C4 | `PASS` |
| RAM host e disco disponíveis pontuais | `RECORDED` (~2,01 GiB/~67,34 GiB) |
| Conteúdo completo do JSON temporário | `NOT_UPLOADED` |
| Prova de quotas CPU/memória de novas bancadas e pressão durante lote | `NOT_CHECKED` |
| Criação, snapshot, POST, benchmark, modificação de Pods/contêineres | `NOT_EXECUTED` |
| Política aprovada para desativar/limpar APENAS recursos M01 | `PENDING` |
| Limiar/stop prospectivo, retenção, ordem de blocos e frozen E11-M00-v1 | `PENDING_FINAL_DECISION` |
| CPU/RAM comparativas | `NOT_APPROVED` |
| E11-M01 | **`BLOCKED`** |

## 4. Encaminhamento objetivo

- Reconhecer M00C como **VALIDADO NOS TESTES SINTÉTICOS E CONSULTAS REAIS READ-ONLY**, não como protocolo experimental congelado.
- Continuar o fechamento em **um único pacote**: regra de arquivamento de saída e backup, política/allowlist de ciclo de vida restrita às bancadas novas, pré-voo de quotas/identidade antes de primeiro POST, limiar operacional para STOP e congelamento prospectivo. Não requer repetir os 65 testes enquanto o código permanecer exatamente no mesmo SHA; se o harness mudar, repetir.
- Evitar sucessivos comandos fragmentados sem benefício metodológico; não propor `docker system prune`, `kubectl delete`, `docker rm`, reinício de qualquer histórico ou teste com POST.
- Preservar todos os laudos de pilotos E11-P04/P05/P06 e seus recursos históricos.

**Integridade:** este documento apenas transcreve/analisa a evidência recebida. Não foram executados testes, Docker, Kubernetes, snapshots ou experimentos pelo assistente para gerar este relatório.
