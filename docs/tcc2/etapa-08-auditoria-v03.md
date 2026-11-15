# TCC2 — Etapa 08: auditoria independente das evidências V03 (E08-D16)

**Data da auditoria:** 15/11/2026. **Cenário:** C2 / V03, serviços frios (antes de snapshot), bancada Docker separada.  
**Resultado:** **APROVADO** na integridade binária e na consistência dos dez testes HTTP inválidos, **somente no escopo ensaiado**.

## 1. Proveniência e identificação

| Elemento | Resultado real |
|---|---|
| ZIP original enviado pelo acadêmico | `c2-v03-r2-20261115-140543.zip` |
| Tamanho do ZIP | **4.489 bytes** |
| SHA-256 do ZIP, recalculado sobre o upload | `718213c176dbb7dbf7982f9615d5f31b5955739b992edb8e1326cdac4749ab9c` |
| Captura PowerShell de arquivamento | `image(20261115-172900).png`, 93.370 bytes |
| SHA-256 da captura, recalculado sobre o upload | `f324e12b8fe9f8ac1bc6fc639e2a6720ff68013f83b207990dd52b300ada2d86` |
| Repositório / branch | `JnetSilvestre/tcc1_JoaoVictor_BigData` / `tcc2/desenvolvimento` |
| Commit declarado no manifesto da rodada | `66dfef80d7c9bf17e4343d6087c8d51e397ae523` |
| Imagem Docker declarada | `tcc2-pon:c2-e08-dbefcd2cf3d2` |
| SHA de revisão da imagem declarado | `dbefcd2cf3d2fbf220cff8eda34d52189e08192a` |
| Rede declarada | `tcc2-pon-c2-v03`, `internal=true` |
| Três contêineres declarados | `tcc2-v03-attribute-source`, `tcc2-v03-logic-engine`, `tcc2-v03-rule-executor`; IDs distintos |

O ZIP e o PNG originais foram recebidos nesta conversa e inspecionados diretamente. **O ZIP original não foi incorporado como binário ao GitHub**; este relatório registra apenas o identificador criptográfico e os resultados conferidos.

## 2. Integridade e inventário de arquivos

- ZIP aberto com `zipfile` e verificação de CRC `testzip()`: **nenhum arquivo corrompido**.
- **9/9 entradas de arquivo**, únicas, sob um diretório de rodada. Caminhos internos utilizam o separador `\` gerado pelo Windows.
- Conteúdo: `attribute-source.jsonl`, `checksums.sha256`, `http-cases.json`, `logic-engine.jsonl`, `manifest.json`, `rule-executor.jsonl`, `states-after.json`, `states-before.json`, `validation.json`.
- Manifesto `checksums.sha256`: **8 hashes** de conteúdo válidos, um por arquivo de dados, sem duplicações ou ausências; hashes recalculados diretamente sobre os arquivos ZIP **8/8 idênticos**.
- Hash SHA-256 de `http-cases.json`: `95cd9cc95a4dd03bd83113cd6380f4897bb64fd989bc2850791190389a050113`, idêntico ao apresentado no comando Windows E08-D15.
- Hash dos **dois arquivos de estado**: `b666d8dd890bcc7e2befdd2264c1573b95e1ec0f1a6aa10c3412e846d049a663`, confirmando igualdade byte a byte entre `states-before.json` e `states-after.json`.
- Todos os documentos JSON/JSONL foram abertos e analisados sem erro de sintaxe.

## 3. Auditoria dos casos HTTP V03

Foram lidos diretamente os **10** registros do `http-cases.json`:

| Caso | Serviço | HTTP esperado/obtido | Preservação de estado reportada |
|---|---|---|---|
| S01 | attribute-source | 422 / 422 | true |
| S02 | attribute-source | 422 / 422 | true |
| S03 | attribute-source | 422 / 422 | true |
| S04 | attribute-source | 400 / 400 | true |
| S05 | attribute-source | 415 / 415 | true |
| S06 | attribute-source | 422 / 422 | true |
| S07 | attribute-source | 422 / 422 | true |
| S08 | logic-engine | 422 / 422 | true |
| S09 | rule-executor | 422 / 422 | true |
| S10 | attribute-source | 404 / 404 | true |

- Todos os registros estão ordenados de S01 a S10 e contêm corpo de erro não vazio. `validation.json` informa `scenario=C2`, `criterion=V03`, `phase=cold`, `status=PASS`, `cases_completed=10`, `cases_planned=10`.
- **Estados inicial e final conferidos independentemente**: JSONs iguais e bytes idênticos; `ready=false`, `run_id=null`, `snapshot_version=null`, sequências 0, nenhuma notificação recebida, nenhum efeito. O produtor tinha `atA=0,atB=0`, avaliador `attributes=null`, `condition=null` e executor `approved=null`, coerentes com o estado frio implementado.
- Logs: `attribute-source.jsonl` tem **8 eventos** (1 `listening` e 7 respostas 4xx registradas como `mutation` pelo logger HTTP); `logic-engine.jsonl` tem **2** (1 `listening` e 1 rejeição 422); `rule-executor.jsonl` tem **2** (1 `listening` e 1 rejeição 422). Os **9 registros de rejeição capturados pelos logs** foram comparados por serviço, caminho, status e corpo de resposta, em ordem, com S01–S09 e coincidiram.
- S10 é `/rota-desconhecida`, status 404, **sem evento `mutation` no log**, coerente com rota não tratada; é visível no transcript HTTP. O termo `mutation` nos logs indica uma tentativa de requisição, **não comprova mutação de estado**.
- **Limitação importante:** `state_unchanged=true` em cada caso deriva da checagem em memória do próprio executor experimental; o ZIP não contém uma cópia completa dos três estados antes e após **cada** caso. A auditoria independente confirma os estados globais antes/depois e a consistência das respostas/logs, mas não reexecuta o processamento no Docker.

## 4. Histórico de bloqueios e resolução

- **E08-D16-R1:** os oito hashes locais passaram; o PowerShell interrompeu a criação do ZIP devido ao modo de interpretar o array de `ConvertFrom-Json` (`Relatorio ou quantidade de casos divergente`).
- **E08-D16-R2:** execução não produziu ZIP; comando `python -c $codigo` enviou aspas incorretamente, resultando em `SyntaxError` na linha `print(===`. Não foi um defeito da aplicação.
- **E08-D16-R3:** usado somente PowerShell com `Compress-Archive` e `System.IO.Compression`; ZIP criado. Comprovado no Windows, nove hashes originais vs. nove entradas ZIP iguais, SHA-256 do ZIP exibido; pacote então enviado para esta auditoria direta.
- Nenhum desses três procedimentos enviou mensagens HTTP, reiniciou contêineres, construiu imagens ou alterou a prova de conceito.

## 5. Conclusão e próximos passos

**E08-D16 APROVADO:** evidências V03 em estado frio **íntegras, legíveis e coerentes**, com 10/10 respostas HTTP esperadas, estado final igual ao inicial e logs compatíveis. **Não concluir V03 globalmente**: falta cobertura com snapshot já instalado e outras entradas. Também permanecem pendentes V05 (deduplicação), V06 (sequência/lacunas) e avaliação complementar de V07 (ACK/snapshot).

**Próximo incremento E08-D17:** preparar uma nova sessão de ensaio controlada V05 e V06, idealmente com isolamento de IDs, logs e snapshots específicos, sem reutilizar de maneira insegura a rodada V03 e sem tocar no cluster kind. O protocolo da Etapa 05 e os contratos HTTP devem guiar os casos e seus resultados esperados.

**Fora de escopo:** desempenho, tolerância a falhas/recovery F1/V10, aplicação Kubernetes e multinó físico. O cluster kind existente não equivale à implantação dos serviços PON.
