# Etapa 12 — Auditoria e extração da campanha E11-M01

## Escopo e documentação

Abertura da Etapa 12 técnica em 18/11/2026, no horário de São Paulo. A auditoria encerra a pendência E11-A01 e entrega os insumos para tratamento dos dados e análise crítica, conforme a [Etapa 05](etapa-05-protocolo-experimental.md) e o [planejamento técnico da Etapa 11](etapa-11-diagnostico-plano.md). O checkpoint de encerramento registra que o macroplanejamento também usa «Etapa 12» para preparação da defesa. Essa referência foi preservada. `CONTEXTO_MESTRE_TCC2.md` e `Planejamento TCC2.txt` não estavam acessíveis no clone, na árvore remota consultada ou na busca local em Documentos e Downloads. A conversa de origem confirma a nomenclatura técnica.

O clone local foi sincronizado por avanço direto com `origin/tcc2/desenvolvimento` em `ac674ebe18c522235be0b7875bff7b9cb193d3a7` para consultar o [status de encerramento](../../STATUS_ATUAL_TCC2.md), o [pré-registro E11-M00-v1](etapa-11-e11-m00-v1-pre-registro-e-gates-m01.md) e a [orquestração integral](etapa-11-e11-m01-orquestracao-integral.md). Os módulos preexistentes de benchmark usados na extração coincidem com a árvore do commit `24740e922181dace018a26938b353f10d952da06`.

## Inventário verificado

- Originais acessíveis em `C:\Users\João Victor\TCC2-Evidencias\E11-M01` e cópias/journals em `D:\TCC2-Backup\E11-M01`. Os 30 ZIPs originais passaram CRC, cobertura integral de 770 SHA-256 internos e correspondência dos 800 membros com as pastas locais. Os 30 backups têm o mesmo SHA-256 dos respectivos originais, com 30 hashes distintos. As letras C: e D: identificam volumes.
- Os 60 journals têm identidade, sequência temporal e hash final conciliados com os ZIPs. Cada rodada registra uma entrada de início de snapshot/lote, uma conclusão RUN e uma conclusão RETIRE. Os 150 IDs/UIDs de rede/contêineres ou namespace/Pods são distintos entre as bancadas e conferem com o início autorizado de cada retirada. As topologias de serviço mantiveram identidade e zero reinícios. C3 registra os serviços no worker. C4 registra o `logic-engine` no control-plane e os demais no worker, dois nós kind virtuais no mesmo host físico.
- A ordem observada nos timestamps dos lotes coincide com a agenda B01–B10. B01/C2 tem SHA de execução `eecc15e3bb1c36c9ee51b3165f882d76a0c6ed9b`, conforme o registro da execução anterior. O journal contém uma tentativa e antecede a desmobilização no SHA do controlador. Esse conjunto corrobora a retomada sem novos POSTs descrita no status. As demais 29 rodadas registram o SHA do controlador na execução.
- Foram conciliados por rodada 1.000 entradas, 1.000 HTTP 200 em CSV e JSONL, 874 mudanças, 126 no-ops, 874 notificações de atributo, 500 de condição e 250 efeitos iguais ao oráculo regenerado. As 30.000 requisições têm IDs únicos. Todas as rodadas registram `timing_only`. O caminho da fixture pré-registrada contém `s01` por origem histórica. Foram usados somente a entrada canônica e seu oráculo, conferidos pelos SHA-256 pré-registrados. A amostra contém exclusivamente os 30 IDs B01–B10.
- Os 30 `REVIEW_READONLY_PASS` e o marcador `all_30_completed=true` são registrados no status histórico. A transcrição integral do controlador não foi localizada nas raízes de evidência consultadas. A auditoria direta verificou os arquivos, checkpoints de identidade e os 30 journals de retirada. A estabilidade dos três Pods de serviço está nos snapshots kind. O UID do cliente consta da propriedade inicial e do journal de retirada.

## Extração e transferência única

A partir de `prova-conceito`, executar com Python 3.13 e indicar um novo ZIP de saída fora das evidências.

```powershell
$e = 'C:\Users\João Victor\TCC2-Evidencias'
python -B -m benchmark.m01_extract `
  --originals "$e\E11-M01" `
  --backups 'D:\TCC2-Backup\E11-M01' `
  --fixture "$e\E11-M00E\fixture-1000-s01\s1000\inputs.jsonl" `
  --output '..\E11-M01-auditoria-extracao.zip'
```

O [script](../../prova-conceito/benchmark/m01_extract.py) abre as evidências para leitura, reaproveita a agenda, a auditoria de ZIP e a validação funcional existentes e interrompe na primeira divergência. A saída consolida:

| Arquivo | Conteúdo |
| --- | --- |
| `inventario.json` | 30 registros com caminho relativo, SHA-256 dos ZIPs, membros e journals, identidade da bancada, bloco, ordem, revisões Git, contagens e horários |
| `rodadas.csv` | Uma linha por rodada, com duração de lote em ns do relógio monotônico do cliente |
| `requisicoes.csv` | Uma linha por requisição, com rodada, bloco, ordem, ID, passo, RTT em ns, status HTTP e indicador de mudança |
| `checksums.sha256` | SHA-256 dos três arquivos derivados |

A execução real produziu `E11-M01-auditoria-extracao.zip` com 331.311 bytes e SHA-256 `66d115c77f7b22819cc43ad84e11ccd43759ca319ac5ef26c3f23e2af8645329`. Uma leitura independente confirmou CRC, hashes internos, 30 rodadas, distribuição 10/10/10, 1.000 requisições por ID e unicidade global. A suíte existente de benchmark passou 179/179 testes. Para receber em outro ambiente, basta transferir esse ZIP e conferir o SHA-256 externo e os checksums internos. Os originais permanecem disponíveis no host para repetir a auditoria ou rastrear uma linha pelos identificadores do inventário.

## Tratamento posterior

Usar a rodada como unidade experimental e o bloco como unidade do pareamento. Derivar tempo total de lote, vazão de 1.000 requisições por duração monotônica e resumos de RTT dentro de cada rodada, em unidades documentadas. Consolidar valores por cenário e diferenças/razões por bloco conforme a [matriz quantitativa](etapa-11-e11-m00a-matriz-quantitativa.md). Os horários UTC servem à rastreabilidade e à ordem. CPU e RAM ficam fora das métricas de lote. Comparações, gráficos, interpretação e redação científica ficam para a atividade de análise.

## Análise descritiva e integração com a monografia

A análise foi executada a partir do pacote verificado acima. A partir da raiz do repositório, com Python 3.13 e Matplotlib 3.10.7, reproduza as três tabelas LaTeX, as duas figuras vetoriais usadas no capítulo de resultados e o [CSV das métricas por rodada](e11-m01-metricas-por-rodada.csv).

```powershell
python -B prova-conceito/benchmark/m01_analyze.py E11-M01-auditoria-extracao.zip
```

O script verifica os checksums dos dados derivados, a grade completa com 30 combinações bloco/cenário, HTTP 200, IDs únicos e 1.000 RTTs por rodada. Calcula primeiro métricas de cada rodada. Depois compara C3/C2, C4/C2 e C4/C3 por bloco e sintetiza cada cenário por mediana, quartis inclusivos interpolados e extremos. Os percentis por rodada usam a posição inteira superior da série ordenada. Nenhum bloco foi removido.

A mediana dos tempos de lote foi de 18,09 s (C2), 18,35 s (C3) e 19,03 s (C4). As diferenças pareadas medianas foram, respectivamente, 0,57 s (C3 menos C2), 1,04 s (C4 menos C2) e 0,81 s (C4 menos C3). A descrição desses contrastes, a comparação de caudas e as limitações constam no [capítulo de resultados](../../capitulos/cap-resultados.tex). A interpretação se restringe ao ensaio em host único e à carga serial auditada.
