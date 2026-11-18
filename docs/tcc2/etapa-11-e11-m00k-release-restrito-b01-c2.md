# E11-M00K — Liberação de código limitada à primeira rodada E11-M01: B01/C2

**Data:** 18/11/2026, America/Sao_Paulo. **Tipo:** decisão operacional prospectiva, não relatório de execução. **Fonte:** pré-registro E11-M00-v1, 3 qualificações sacrificiais C2/C3/C4 com backup e encerramento, e saídas PowerShell fornecidas pelo acadêmico. **Escopo do release:** exclusivamente `e11-c2-m01-b01` (B01/C2), primeiro de **30 slots fixos**.

## 1. Evidência comprovada anterior à liberação

No Git HEAD `f5a9b824fe9f7ebe7f3ab34de3fbfd6ba6e98a2a` o acadêmico executou **`Ran 178 tests in 0.471s`, `OK`, `REGRESSAO: 178/178 PASS`**, após compilação sem erro. O planejamento real de `--position 1 --stage plan` também resultou em **`PLANO B01/C2: PASS`**, com `M01_SLOT_PLAN_ONLY`, primeira identidade `e11-c2-m01-b01`, `start_authorized=false`, `commands=[]`. **Nenhuma das 30 rodadas foi executada.** C2/C3/C4 `m01-s01` são qualificações sacrificiais já arquivadas/desmobilizadas e não entram na amostra.

## 2. Mudança de código para liberar APENAS B01/C2

Em `benchmark/m01_lifecycle.py`:
- `MAIN_CAMPAIGN_ENABLED = False` **permanece**: o modo geral de 30 rodadas ainda não está habilitado.
- `RELEASED_OPERATIONS = frozenset({(1, "RUN"), (1, "RETIRE")})`: exceção de escopo estrito para o **slot 1, cenário C2**.
- `require_stage_release` é chamada tanto na CLI antes do prompt quanto nas funções mutantes. Ela bloqueia os slots **2 a 30**, mesmo que tenham nomes formalmente válidos, e bloqueia etapas desconhecidas.
- A permissão de código para `RETIRE` **não concede consentimento** nem executa retirada durante `RUN`. O comando `--stage retire` terá aceite separado `AUTORIZO_RETIRE_E11_C2_M01_B01`, e só poderá passar após ZIP/backup/journal PASS, captura de IDs completos originais no ZIP e comprovação de exclusividade sem terceiros. Nenhum encerramento acompanha automaticamente `RUN`.
- Os três cenários permanecem com mesma imagem aprovada, fixture SHA `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, 1000 POSTs seriados, seed `20260502`, `timing_only`, sem CPU/RAM de lote ou retry.
- Ao contrário de `MAIN_CAMPAIGN_ENABLED=True`, este release não permite executar futuramente B01/C3, B01/C4 ou os B02–B10 sem **nova revisão e autorização de código**.

## 3. Gates que permanecem obrigatórios na execução real B01/C2

Antes da criação, `--stage run --position 1` exigirá:
1. Checkout `tcc2/desenvolvimento` **limpo** com HEAD exato passado em `--approved-head`; compilação, regressão e plano read-only devem ser aprovados novamente **após esta mudança de código**.
2. Ordem congelada: nenhuma rodada anterior incompleta/futura com artefatos, ausência de qualquer outra bancada M01 em Docker `ps -a`, redes ou namespaces; históricos não são alvo.
3. ZIPs/backup D/journals das qualificações sacrificiais C2/C3/C4 preservados, SHA fixture canônica e imagem Docker ID aprovado, estado de host, RAM Windows livre >=3 GiB e disco do projeto >=15 GiB.
4. Diretório `D:\TCC2-Backup\E11-M01` criado de modo controlado, em **volume filesystem diferente de C:** com **>=15 GiB livres** ANTES de criar a bancada. Nada será sobrescrito. No primeiro slot, esse diretório deve estar vazio.
5. Aceite **digitado pelo operador** no PowerShell: `AUTORIZO_RUN_E11_C2_M01_B01`. Qualquer outra entrada cancela; o bloco de execução deve interromper ao receber código de saída diferente de 0.
6. Journal de execução exclusivo `D:\TCC2-Backup\E11-M01\e11-c2-m01-b01-run.jsonl` criado antes do runner; bancada Docker nova isolada `tcc2-pon-e11-c2-m01-b01` com 4 contêineres e rede própria; 1 snapshot e 1000 POSTs sequenciais sem repetição. A PoC funcional e os serviços históricos **não são alterados**.
7. `benchmark.lifecycle_audit.audit_archive` audita CRC, todos os checksums, preflight frio, cgroup efetivo e PASS funcional; backup imutável em `D:\TCC2-Backup\E11-M01\e11-c2-m01-b01.zip` confere SHA/CRC e outro volume; journal final deve ser `COMPLETE/M01_RUN_PASS_BACKED_UP`.
8. Depois de `RUN PASS`, **não retirar a bancada ainda**: revisar ZIP, backup, journal, tempos e IDs Docker originais. `RETIRE` será um comando distinto/consentimento separado, não embutido no bloco de execução.

Em qualquer falha após criação de journal, preservar contêineres/rede, ZIP parcial e journal `INTERRUPTED_DO_NOT_RETRY`; não executar `docker prune`, `docker rm` manual, retry nem avançar B01/C3 automaticamente. Uma falha operacional em B01/C2 não é um valor de tempo aprovado e exige decisão documental antes de substituição/continuação.

## 4. Regressão e liberação condicionada

Foi incluído **1 teste novo de escopo da liberação** ao conjunto de 178 testes antes comprovados: total esperado **179/179**, **ainda não executados no Windows** sob este novo HEAD. Esse teste percorre posições 2–30 e rejeita `RUN` e `RETIRE` nelas, enquanto libera o slot 1 para ambos os fluxos sob aceites distintos; os testes sintéticos anteriores permanecem intactos, com ajuste de nomenclatura para as posições proibidas.

**Nenhuma aprovação do operador foi recebida nesta preparação**, e `RUN B01/C2` não foi executado. A execução depende de `179/179 PASS` e novo planejamento read-only aprovado no host, seguida da frase de consentimento exclusiva. **Decisão:** `E11_M00K_B01_C2_SCOPED_RELEASE_PREPARED_PENDING_LOCAL_TEST_AND_INTERACTIVE_APPROVAL / E11_M01_MAIN_SERIES_0_OF_30`. Os demais 29 slots permanecem bloqueados.
