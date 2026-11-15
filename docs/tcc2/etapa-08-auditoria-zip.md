# TCC2 — Etapa 08: auditoria independente dos artefatos C2 (E08-D12)

**Data da auditoria:** 15/11/2026. **Cenário:** C2, três contêineres Docker no mesmo host, sem Kubernetes da aplicação.  
**Resultado:** **APROVADO** para integridade do pacote e equivalência funcional da fixture determinística.  
**Base do exame:** ZIP original enviado pelo acadêmico nesta conversa; inspeção dos bytes com biblioteca padrão Python (ZIP, JSON e SHA-256), sem executar novamente a aplicação.

## 1. Identificação e proveniência do pacote

| Campo | Valor |
|---|---|
| Nome original | `c2-20261113-182248.zip` |
| Tamanho | **7.417 bytes** |
| SHA-256 do ZIP | `e90a3b1741b6b68d89ca0ea3fecb1583ab869e8cdfca0938db8bceeb8567de6e` |
| Estrutura interna | Diretório único `c2-20261113-182248`, 14 entradas de arquivo (nomes Windows com separador `\`) |
| Integridade ZIP | 14 entradas únicas, sem erros de CRC (teste completo do ZIP) |
| Manifesto de integridade | `checksums.sha256`, com 13 pares arquivo/hash |
| Conferência SHA-256 | **13/13 válidos**, sem duplicações, sem arquivos ausentes ou extras |
| Arquivos JSON/JSONL | Todos legíveis, sintaxe analisada sem erros |
| Rodada registrada no ZIP | `c0-minimo-v1` |
| Commit do executor (manifesto) | `5eee8e7a7c931491d3668cc9472a46191de6180c` |
| Commit do runtime (manifesto) | `dbefcd2cf3d2fbf220cff8eda34d52189e08192a` |
| Imagem (manifesto) | `tcc2-pon:c2-e08-dbefcd2cf3d2`, ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a` |
| Rede (manifesto) | `tcc2-pon-c2`, `internal=true` |
| Identificadores | Três IDs Docker distintos e mesmo ID de imagem para todos os papéis |

**Guarda do original:** o ZIP foi anexado à conversa e a pasta fonte foi gerada em `prova-conceito/resultados-locais/c2-20261113-182248` no Windows do acadêmico. **O arquivo ZIP original NÃO foi adicionado a este commit/repositório.** O SHA-256 acima identifica exatamente o pacote auditado.

## 2. Inventário verificado

`attribute-source.jsonl`, `c0-effects.jsonl`, `effects.jsonl`, `expected.jsonl`, `fixture.jsonl`, `http.jsonl`, `logic-engine.jsonl`, `manifest.json`, `oracle_independente.jsonl`, `rule-executor.jsonl`, `states-final.json`, `states-initial.json`, `validation.json` e `checksums.sha256`.

Os 13 arquivos de dados são precisamente os 13 listados no manifesto de checksums. Os 14 conteúdos foram lidos diretamente do ZIP sem extrair os arquivos para a árvore do repositório.

## 3. Verificações funcionais independentes

1. `fixture.jsonl` tem **7 passos numerados de 1 a 7**, `seed=20260501` e `run_id=c0-minimo-v1`; `http.jsonl` tem **7 requisições/respostas**, na mesma ordem e com `request_id` correspondente.
2. Recomposição **independente** do comportamento a partir da fixture, com atributos iniciais `atA=0, atB=0`, regra `atA >= 5 && atB == 1` e emissão de efeitos só nas transições de falso para verdadeiro: **5** alterações efetivas de atributo, **3** transições de condição e **2** efeitos, nos passos **3** e **7**.
3. O conteúdo estruturado e a ordem dos efeitos em `effects.jsonl`, `expected.jsonl`, `c0-effects.jsonl` e `oracle_independente.jsonl` são **exatamente iguais** ao resultado recalculado, incluindo identificadores, sequências, `caused_by`, `attribute_event_id` e passos.
4. Os logs dos serviços contêm, respectivamente, **21** registros (`attribute-source`), **15** (`logic-engine`) e **7** (`rule-executor`). Entre eles, **7** mutações `/attributes/change` com HTTP 200, **5** notificações de atributo enviadas/confirmadas/recebidas e **3** notificações de condição enviadas/confirmadas/recebidas com payloads iguais e na mesma ordem. Há **2** registros de efeito iguais a `effects.jsonl`.
5. `states-initial.json` comprova snapshot previamente inicializado, `ready=true`, atributos/sequências 0 e sem efeitos. `states-final.json` apresenta `atA=6`, `atB=1`, sequências `atA=2`, `atB=3`; condição e regra aprovadas (`true`), sequência de condição **3**, registros de IDs recebidos consistentes, efeitos **2**, sem estado `faulted` e sem requisição pendente no produtor.
6. `validation.json` registra `scenario=C2`, `status=PASS`, `started_changes=true` e **11/11** verificações `true`. As conferências de bytes, transições e relações causais acima **não dependem apenas desse PASS declarado**.
7. Os SHA-256 de `fixture.jsonl` e `expected.jsonl` conferem com `manifest.json` e `checksums.sha256`. Os respectivos conteúdos também foram comparados com `prova-conceito/fixtures/c0_minimo.jsonl` e `c0_esperado.jsonl` na branch `tcc2/desenvolvimento`: **igualdade exata após normalizar CRLF (ZIP/Windows) para LF (GitHub)**. Os hashes dos bytes sem normalização diferem por essa quebra de linha (7 e 2 ocorrências, respectivamente), não por alteração de dados.

### Efeitos auditados

| Passo | Atributo causador | Condição causadora | Efeito |
|---:|---|---|---|
| 3 | `c0-minimo-v1:atB:1` | `c0-minimo-v1:cn1:1` | `c0-minimo-v1:rl1:1` |
| 7 | `c0-minimo-v1:atB:3` | `c0-minimo-v1:cn1:3` | `c0-minimo-v1:rl1:2` |

No passo 6, a condição torna-se falsa e ocorre `cn1:2` sem um novo efeito, conforme a semântica implementada e o oráculo.

## 4. Captura complementar do Docker Desktop

- Captura fornecida: `image(20261115-142514).png`, **227.077 bytes**, SHA-256 `9ff6d97de22ea9693b1dc1056b46813f2bae156f4863352cfc277816280f26fe`.
- A interface exibe os três contêineres C2 com estado visual de execução, utilizando a mesma tag de imagem; também exibe os nós `tcc2-pon-control-plane` e `tcc2-pon-worker` pertencentes ao kind e o contêiner antigo de validação Python parado.
- Valores instantâneos/agregados de CPU e memória no painel **NÃO** são usados como benchmark C2, pois incluem outros contêineres e não derivam do protocolo de medição isolada.
- A interface mostra que os três C2 haviam sido iniciados recentemente em relação à captura; **não se pode presumir que o estado em memória observado em 13/11 persista em 15/11**. Antes de ensaios adicionais, verificar o estado atual por `GET /state` e não repetir a fixture cegamente.

## 5. Limitações e pendências

- **Aprovado:** integridade do ZIP, identificação dos bytes auditados, propagação das notificações, sequência causal e equivalência funcional C2↔C0/fixture/oráculo **nos sete passos ensaiados**.
- **Não comprovado nesta auditoria:** autenticidade externa do arquivo anterior à entrega, experimentos de falha, perda e reordenação de mensagens em Docker, concorrência, persistência/recuperação após reinício, estabilidade sob carga, medições controladas de CPU/memória/latência e execução física em múltiplos hosts.
- O ZIP é preservado na conversa e na máquina do acadêmico; **a cópia binária em armazenamento permanente do GitHub ainda é pendente**. Não confundir este registro documental e seu SHA com arquivamento do próprio binário no repositório.
- O cluster kind visível na captura **não** significa que a aplicação tenha sido implantada nele. Kubernetes permanece exclusivamente nas Etapas 09–10.

## 6. Decisão e próximo incremento

**E08-D12: APROVADO** na auditoria independente do ZIP recebido.  
**Etapa 08: ainda não encerrada integralmente.** O próximo incremento deverá selecionar casos adversariais de C1/V01–V07 aplicáveis a C2, executar em rodada isolada e preservar evidências reais, sem reutilizar de forma insegura a rodada `c0-minimo-v1` já consumida. Antes de qualquer mutação, realizar diagnóstico somente leitura dos contêineres atuais.

Os dados documentados fornecem insumos para o diagrama da topologia C2, a tabela de equivalência funcional e os registros experimentais futuros da monografia; não constituem resultados de desempenho.
