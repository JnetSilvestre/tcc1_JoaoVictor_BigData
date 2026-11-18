# E11-M00H — Qualificação sacrificial C4-S01 preparada após C3

**Data documental:** 18/11/2026 (America/Sao_Paulo). **Situação:** `C4_S01_PROCEDURE_PREPARED_NOT_EXECUTED`; `E11_M01_MAIN_SERIES_BLOCKED`.

## 1. Pré-requisito operacional de exclusividade

O cenário C3-S01 real foi qualificado com `PASS` no SHA `f797ea94673429ead627e939ddfce38ef0191c45` em 18/11/2026 e deixou **namespace novo `tcc2-pon-e11-c3-m01-s01`**, UID `41fa5e1b-1de5-40da-b72a-e051742788c1`, ainda existente ao final. Seus ZIP original e backup em C/D têm SHA reportado `463f56042536c95874a4f36dadfd5fd211fec18325132704c9f585d2ec6e80c8`. **Não executar C4 enquanto o namespace C3-S01 estiver presente**.

O módulo `benchmark/retirement_execute_c3_s01.py` oferece consulta somente leitura por padrão e retirada mutante por **UID preconditionado** somente após verificação de ZIP, cópia em D, labels/UIDs de Pods e Namespace, inventário sem terceiros, regressão sintética e aceite específico. **O UID é congelado, o nome sozinho não autoriza DELETE**.

## 2. Script de qualificação C4-S01

`prova-conceito/scripts/e11_m00h_qualificacao_c4.ps1` foi criado pela especialização do fluxo C3 já comprovado, com estas diferenças prospectivas:
- exige journal de desmobilização **C3-S01** no volume D terminando com `stage=COMPLETE`, `status=C3_S01_RETIREMENT_COMPLETE` e ambos os ZIPs C3 com SHA correto;
- usa `scenario=C4`, `label=m01-s01`, `run_id=e11-c4-m01-s01`, namespace **novo** `tcc2-pon-e11-c4-m01-s01`;
- gera manifesto C4, valida dry-run e, **somente após autorização interativa** `AUTORIZO_EXECUTAR_QUALIFICACAO_C4_S01`, aplica manifesto no namespace novo;
- exige imagem SHA aprovado, dois nós kind Ready, RAM Windows >=3 GiB, C/D >=15 GiB, Git limpo e fixture canônica;
- respeita o placement previamente definido: serviços source/executor e cliente no nó worker virtual; logic-engine no control-plane virtual (a conferência final é de `benchmark.runner`), mesmo host físico;
- executa **uma única vez** snapshot e 1.000 POSTs no `timing_only`, após preflight frio/ownership/cgroup/exclusividade do executor; em `PASS`, valida ZIP com `audit_archive`, copia para D e testa CRC+SHA e volumes distintos, preservando namespace;
- cria journal em `D:\TCC2-Backup\E11-M00H\C4-m01-s01-journal.jsonl`; original em `C:\Users\<perfil>\TCC2-Evidencias\E11-M00H\C4-m01-s01\resultado.zip`, backup em `D:\TCC2-Backup\E11-M00H\C4-m01-s01.zip`.

**Proteção:** não inicia se houver outros objetos `m...`, incluindo Docker parado ou namespace C3 ainda existente. Não contém `kubectl delete`, `docker rm`, prune ou restart. Qualquer erro posterior ao apply **preserva namespace e artefatos e impede repetição automática**.

## 3. Gate científico

Se C4-S01 terminar `PASS`, terá qualificação técnica separada do conjunto de 30 rodadas. A próxima etapa será elaborar/aprovar retirada com UID exclusivo desse namespace (ainda desconhecido prospectivamente), auditar e registrar ZIP e backup, e transformar os procedimentos validados C2/C3/C4 em um ciclo de vida geral por rodada inédita, com fail-closed e exclusividade real antes de B01.

**Código/testes após C3-S01 ainda não foram executados no host**, e não existem resultados C4-S01 observados. `118/118 PASS` é válido apenas para o SHA da qualificação C3 anterior; agora 10 novos testes sintéticos de retirada C3 preveem `128/128` após validação Windows. Não declarar `GO` de E11-M01 antes da qualificação e ciclo de vida corretos.
