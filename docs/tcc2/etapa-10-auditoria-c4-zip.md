
# TCC2 — Etapa 10: auditoria do C4 multinó virtual (E10-C4)

**Data:** 15/11/2026. **Branch:** tcc2/desenvolvimento. **Natureza:** auditoria independente do artefato experimental recebido; não é nova execução no ambiente Windows nem medição de desempenho.

## 1. Proveniência, integridade e hashes

- **Arquivo bruto recebido e inspecionado:** c4-e10-i02-v1.zip; o original permanece anexado à conversa e no computador do acadêmico, não no GitHub.
- **ZIP C4:** 36.370 bytes; SHA-256 recalculado **8f77d981abb6977890f948168924b594398828ef3d843d7f38baf66d09acca7c**. Corresponde ao SHA-256 informado pelo runner e ao valor mostrado pelo Get-FileHash independente no PowerShell.
- **Conteúdo externo:** 16/16 nomes únicos, sem erro CRC. A lista checksums.sha256 cobre todas as outras 15 entradas; **15/15 hashes corretos**.
- **ZIP interno da fixture:** fixture.zip com 27.505 bytes, SHA-256 recalculado **21dcdc0239bb51d41e4148b8834e626c32dd5ac355f7fe4ba78a245dc3dfe2be**. Possui 28/28 entradas únicas, sem erro CRC. A lista interna checksums.sha256 cobre as outras 27 entradas; **27/27 hashes corretos**.
- **Verificações adicionais executadas na auditoria do ZIP, sem rede Kubernetes:** **48/48 PASS**. São checagens do conteúdo armazenado (integridade, metadados, imagens, estado inicial/final, topologia, snapshots, sequência, respostas HTTP, oráculo e causalidade), e não 48 novas rodadas experimentais.
- Git SHA da execução registrado nos manifestos: **f84c8384f33168219213757f9b2027216a2511e4**. Python host 3.13.9, Windows-10-10.0.19045-SP0, seed 20260501, run_id c4-e10-i02-v1, contexto kind-tcc2-pon, namespace tcc2-pon-c4.

## 2. Imagem, isolamento e topologia comprovada

A execução confirmou, em seu preflight, a imagem aprovada em C2: tag tcc2-pon:c2-e08-dbefcd2cf3d2, ID Docker **sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a** e revisão OCI **dbefcd2cf3d2fbf220cff8eda34d52189e08192a**. Os três Pods reportaram o mesmo imageID de runtime containerd **docker.io/library/import-2026-11-15@sha256:c05bd0d752e95c71f1f4996cbc569e82d1a6c714fe4746aa295058bf355f99ba**. O identificador containerd **não deve ser confundido** com o ID da imagem local nem com digest remoto de registro.

| Papel | Pod | Nó Kubernetes | IP do Pod | Restarts |
|---|---|---|---|---:|
| attribute-source | attribute-source-6dcf9b667c-xrlmh | tcc2-pon-worker | 10.244.1.6 | 0 |
| logic-engine | logic-engine-76576f4f8f-p29qz | tcc2-pon-control-plane | 10.244.0.5 | 0 |
| rule-executor | rule-executor-7b49cf69fb-rfngp | tcc2-pon-worker | 10.244.1.5 | 0 |

Três UIDs de Pods e três IDs containerd distintos, dois nós Ready, três Services ClusterIP com endereços diferentes. As identidades dos Pods e o número de restarts permaneceram estáveis entre as quatro capturas topológicas (antes/depois do snapshot e antes/depois da fixture). **Não houve migração, reinício ou escala horizontal durante a rodada.** C3 foi verificado separadamente pela saída Windows: os seus três Pods continuavam Running, 1/1, restarts=0.

O fluxo lógico attribute-source (worker) -> logic-engine (control-plane) -> rule-executor (worker) **atravessa nós Kubernetes virtuais nas duas ligações**. O cruzamento é inferido conjuntamente do posicionamento dos Pods, dos Services e da igualdade dos registros de envio/recebimento; não se fez captura de pacotes de rede. **Ambos os nós kind residem no mesmo host físico**, não representando dois computadores independentes.

## 3. Snapshot único e execução da fixture

- Antes do snapshot, os três estados eram frios (ready=false, run_id=null); logs sem mutações. As chamadas DNS internas de /health/live responderam HTTP 200 e as /health/ready responderam HTTP 503.
- Snapshot exclusivo C4 enviado uma vez (run_id c4-e10-i02-v1), HTTP 200, duplicate=false, snapshot_version=c4-e10-i02-v1:snapshot:0. Três estados funcionais prontos, marcadores de sequência zero, condition=false, approved=false, sem efeitos; logs demonstraram exatamente um POST de inicialização em cada papel. O status FAIL em preflight.json é **o estado provisório do relatório antes do primeiro POST**, não falha do preflight: a saída real e validation-c4.json reportam PASS.
- Sete passos da fixture original, apenas rebase do run_id; seed **20260501** preservada. Houve sete intenções BEFORE_POST, sete respostas HTTP 200, nenhuma duplicata de request_id.
- Passos **1 e 4** com valor inalterado, sem AttributeChanged; **2, 3, 5, 6, 7** com mudança efetiva. Resultaram **5 notificações de atributo** recebidas pelo avaliador com payload idêntico ao enviado e em igual ordem.
- O avaliador emitiu **3 notificações de condição**, nos passos 3 (false->true), 6 (true->false) e 7 (false->true); todas chegaram ao executor em ordem, com IDs iguais e HTTP 200.
- O executor registrou **2 efeitos** nos passos 3 e 7, nessa ordem: passo 3 causado por c4-e10-i02-v1:cn1:1 (AttributeChanged c4-e10-i02-v1:atB:1), passo 7 por c4-e10-i02-v1:cn1:3 (AttributeChanged c4-e10-i02-v1:atB:3). Estado final: atA=6, atB=1; sequências de atributos (2,3), condition_sequence=3, condição e aprovação verdadeiras, sem falhas ou envio pendente.
- Comparação **exata de objetos JSON ordenados**: effects.jsonl == expected-c3.jsonl == oracle-independente.jsonl == c0-effects.jsonl. A auditoria também calculou **novamente** os dois efeitos diretamente da fixture por máquina de estados booleana independente do runtime distribuído.
- validation.json da fixture: PASS com **14/14** checks internos. validation-c4.json: PASS, snapshot iniciado, alterações iniciadas, 14/14 checks da fixture, sem erro.

**Observação de nomes:** o arquivo expected-c3.jsonl dentro do ZIP de C4 foi herdado do nome usado pelo runner C3, mas seu conteúdo registra scenario/run_id C4 e foi conferido. Isso não equivale a ter usado estado ou Pods do C3 na rodada C4.

## 4. Verificações adicionais da auditoria (48/48)

Checagens executadas sobre bytes recebidos:
1. Tamanho e hash ZIP externo; contagem de entradas e CRC; cobertura dos hashes externos; validade dos hashes externos.
2. Hash ZIP interno; contagem de entradas e CRC; cobertura dos hashes internos; validade dos hashes internos.
3. Metadados run_id, scenario e Git; 14 checks dos relatórios externo e interno; coerência de status provisório do preflight; snapshot único com resposta esperada.
4. Dois nós distintos de fato; três UIDs/contêineres distintos; dois nós Ready; imagem comum/restarts zero; estabilidade das identidades; três Services distintos.
5. Estados frios; estados prontos; consistência entre após snapshot e antes da fixture; snapshot único nos logs de cada papel; ausência de mudanças prévias.
6. Sete passos em ordem e seed fixa; identidade semântica da fixture original; equivalência do oráculo/manual/C0/efeitos; rebase coerente de IDs.
7. Cálculo independente dos efeitos; valores e sequências finais; efeitos e readiness finais; sete respostas HTTP 200; sete intenções BEFORE_POST; cinco respostas com changed=true e nenhuma duplicata.
8. Cinco envios e recebimentos de atributo iguais; três envios e recebimentos de condição iguais; dois logs de efeito idênticos; mutações com HTTP 200; transições nos passos 3,6,7; relações causa/atributo; logs de snapshot; diferença de nós mantida no fim; contagens por HTTP 200; IDs não duplicados; identidade de serviço dos logs; hashes dos fixtures registrados no manifesto.

Todas aprovadas. A verificação é interna a esse caso de teste e não comprova comportamento sob falhas, paralelismo/concorrência geral, recuperação, carga ou desempenho.

## 5. Matriz de aceitação e próximos passos

| Critério | Classificação e escopo |
|---|---|
| V01 | Aprovado para fixture C4 mínima (valores repetidos e duas ativações) |
| V02 | Aprovado no C4 mínimo por igualdade com C0, esperado manual e oráculo |
| V04 | Aprovado no C4 mínimo: cinco AttributeChanged e três ConditionChanged correlacionados entre Pods distintos |
| V07 | Parcial globalmente: snapshot e watermarks coerentes, sem corrida de alteração durante inicialização C4 |
| V08 | Aprovado no C4 funcional mínimo: Services, Pods, probes, snapshot e fixture completos |
| **V09** | **APROVADO em distribuição entre dois nós Kubernetes virtuais**, com notificações comprovadas entre eles |
| V10 | Não executado: sem reinício/replay ou recuperação automática |
| V11 | Parcial globalmente: ZIP, manifestos, logs e comandos preservados, mas nenhuma reprodução independente por terceiro em ambiente novo |
| V12 | Não executado: sem benchmark comparativo ou métricas CPU/RAM/vazão/latência |

**Decisão:** considerar a **Etapa 10 concluída funcionalmente para C4 multinó virtual mínimo**, preservando o limite de host físico único. Não transformar dois nós kind em afirmação de distribuição entre máquinas físicas; não afirmar ganho de desempenho, alta disponibilidade ou escalabilidade. O código Python prova de conceito não deve ser equiparado automaticamente ao sistema C++ NOP Query.

**Preservação:** não reenviar snapshot, refazer os sete passos, reiniciar ou escalar os Pods stateful C3/C4 já exercitados. Conservar ambos os ZIPs brutos (C3/C4) fora do GitHub e seus hashes. Não há exigência de repetir testes C0/C1/C2 ou de instalar Metrics Server para esta auditoria.

**Próxima etapa:** Etapa 11, planejamento e pré-validação de métricas/gerador de carga por cenário C0/C3/C4, com novas rodadas e namespaces para testes quantitativos, fixação de SHA/fixtures/recursos e separação entre tempo de testes funcionais e medições. Qualquer comparação exige protocolo, instrumentos e dados brutos reais; nenhuma medida foi coletada nesta Etapa 10.
