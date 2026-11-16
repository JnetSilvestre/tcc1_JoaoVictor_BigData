# TCC2 — Etapa 11: triagem editorial crítica da pesquisa Perplexity

**Data de triagem:** 15/11/2026. **Originais recebidos:** `pesquisa_metodologica_e11_perplexity.md` (dossiê em português, 586 linhas) e `referencias_e11_perplexity.bib` (14 entradas F01–F14). **Natureza:** pesquisa auxiliar, NÃO texto pronto para a monografia. Nenhum dado experimental da literatura substitui nossas medições reais.

## 1. Regra editorial vinculante

- Redigir a monografia **em português técnico-científico natural**, com síntese crítica autoral, citações indiretas e rastreabilidade; não colar nem traduzir literalmente parágrafos do Perplexity.
- Aceitar como leitura e base apenas obras disponíveis em **português, inglês ou espanhol**. Os artigos centrais selecionados estão em inglês; nomes de autores com diacríticos não significam que o artigo está escrito em outra língua.
- Não usar todas as 14 referências por obrigação. Seleção determinada por uma função explícita de cada fonte, evitando citações decorativas e repetição de ideias.
- Conservar o texto original aprovado do TCC1, principalmente trechos do orientador. Escrever/editar a metodologia no LaTeX existente somente após revisar capítulo atual, e sem substituições automáticas.
- O dossiê foi dirigido por perguntas; **não** é uma revisão sistemática exaustiva. Não alegar busca/exaustividade que ele não demonstrou.

## 2. Núcleo de quatro publicações científicas a citar seletivamente

| ID | Fonte principal (idioma) | Função permitida no TCC | Verificação independente |
|---|---|---|---|
| F01 | Papadopoulos et al. (2021), *Methodological Principles for Reproducible Performance Evaluation in Cloud Computing* (inglês) | Base central para descrição do ambiente, validade, reprodutibilidade, métricas e divulgação de dados | IEEE TSE 47(8), 1528–1543, DOI 10.1109/TSE.2019.2927908; https://ieeexplore.ieee.org/document/8758926/ |
| F02 | Maricq et al. (2018), *Taming Performance Variability* (inglês) | Justificar medições repetidas, variabilidade e cautela sobre número fixo de repetições | USENIX OSDI 2018, pp. 409–425; https://www.usenix.org/conference/osdi18/presentation/maricq |
| F03 | Duplyakin et al. (2023), *Avoiding the Ordering Trap in Systems Performance Measurement* (inglês) | Justificar blocos e alternância/randomização de ordem para mitigar efeito de execução anterior | USENIX ATC 2023, pp. 373–386; https://www.usenix.org/conference/atc23/presentation/duplyakin |
| F05 | Kalibera e Jones (2013), *Rigorous Benchmarking in Reasonable Time* (inglês) | Fundamentar unidade experimental, hierarquia de variabilidade e intervalos de incerteza versus orçamento | Registro institucional, DOI 10.1145/2464157.2464160; https://kar.kent.ac.uk/33611/ |

**Limite explícito:** nenhum desses artigos prescreve 100/1000/10000 requisições, dez repetições universalmente suficientes, warmup fixo, nem prova que kind ganha desempenho. São fundamentos para **decisões do nosso protocolo**, não resultados medidos na PoC.

## 3. Fontes técnicas oficiais sob demanda, não todas num único parágrafo

| ID | Documento | Usar exatamente quando |
|---|---|---|
| F09 | Linux Kernel, *Control Group v2* | Definir `cpu.stat`, `usage_usec`, `memory.current`, `memory.peak`, hierarquia de cgroups; https://docs.kernel.org/admin-guide/cgroup-v2.html |
| F10 | Kubernetes, *Node metrics data* | Descrever a origem e o acesso da kubelet Summary API e a diferença frente à metrics.k8s.io; https://kubernetes.io/docs/reference/instrumentation/node-metrics/ |
| F11 | Kubernetes, *Kubelet Summary API (v1alpha1)* | Explicar campos `usageCoreNanoSeconds`, `workingSetBytes` e timestamps de atualização; preferir a documentação oficial https://kubernetes.io/docs/reference/kubelet-api/stats.v1alpha1/ ao link de versão não correspondente no pkg.go.dev |
| F13 | kind, documentação oficial | Sustentar que nós kind são contêineres e que o cluster da PoC não é distribuição entre computadores físicos; https://kind.sigs.k8s.io/ |

F12 (Docker stats) e F14 (requests/limits) são **reservadas para trechos específicos de instrumentação/controle de recursos**, não inclusão automática. A documentação geral de Docker/Kubernetes já aparece com registros semelhantes no `main.bib`, então evitar multiplicar entradas genéricas.

## 4. Referências que NÃO entram automaticamente

- **F04 Laaber et al. (2019):** estudo real e interessante, mas sobre microbenchmarks Java/Go em clouds públicas; útil apenas se precisarmos discutir microbenchmark/variabilidade de ambientes distintos. Não transferir seus percentuais ou estratégias de exclusão de outliers para esta PoC.
- **F06 Mytkowicz et al. (2009):** acesso pelo Perplexity limitado ao resumo; alerta histórico sobre vieses, mas redundante para nosso texto em relação a F01/F03. Não usar para alegações detalhadas sem leitura integral.
- **F07 Henning et al. (2021):** artigo curto/proposta com Kubernetes Operator Pattern; não justifica instalar Operator, Prometheus ou Grafana. Usar como referência temática eventual, não como regra experimental.
- **F08 Henning e Hasselbring (2021):** discute escalabilidade de stream processing e configuração de instâncias. Nosso ensaio inicial é **serial e com réplicas fixas**. Não inferir escalabilidade horizontal do TCC. Texto editor disponibiliza introdução e metodologia, mas não há justificativa para citá-lo como fonte central.
- **F12 e F14:** fontes oficiais pertinentes, mas a necessidade concreta deve ser determinada após definir a instrumentação equivalente de C2 e os recursos finais. Não inserir títulos só para aumentar a bibliografia.

## 5. Regras de integração ao LaTeX e bibliografia

- A bibliografia original `main.bib` já contém cerca de 295 chaves registradas e referências gerais sobre Docker/Kubernetes; nenhuma das quatro DOIs acadêmicas acima foi encontrada pelo texto exato do DOI. **Não foi comprovada ausência de duplicações semânticas por título em todas as 295 entradas**, portanto verificar antes de inserir.
- O projeto usa `abntex2-alf.bst`, `main.bib` e macros de citação existentes, inclusive `\citeonline` em `configuracoes.tex`. **Não trocar estilo nem preâmbulo por sugestão externa**.
- Nunca colar 14 registros F01–F14 diretamente no `main.bib`. Arquivo separado `docs/tcc2/etapa-11-referencias-curadas-candidatas.bib` guarda apenas 8 registros candidatos com chaves descritivas; nenhum foi inserido na bibliografia efetiva ainda.
- Bibliografia do Perplexity foi conferida por inspeção, com 14 chaves distintas. BibTeX tem autoria/títulos sem duplicação de chaves no material importado. Compilação com BibTeX/Overleaf e validação editorial ABNT ainda **não executadas**.
- Para documentos vivos, não inventar ano da edição. Usar identificação oficial/URL e data de acesso. Para artigos, ano da edição final (F01: 2021) não muda porque o DOI menciona 2019.

## 6. Recomendações do estudo a manter, sem inflar o método

1. **Desfecho primário:** duração monotônica por lote correto; vazão `N/T` é derivada, não segunda evidência independente.
2. **Unidade de repetição:** uma bancada/rodada preparada com estado novo, não cada POST individual; manter todas as rodadas, inclusive falhas.
3. **Comparações primárias:** C2 versus C3 e C3 versus C4 por blocos; C0/C1 são referências arquiteturais. Nenhum contraste isola sozinho Kubernetes ou uma rede física.
4. **Ordem:** distribuir os cenários entre blocos com ordem permutada e registrada; não medir todo C2, depois todo C3, depois todo C4 sem mitigação de deriva.
5. **Recursos:** mesma imagem/versões/requisições/política de timeout/limites quando possível, e explicitar assimetrias Docker–kind e competição do control-plane.
6. **Telemetria:** separar CPU cumulativa de CPU%, working set de RSS/memory.current, e pico de memória de máximo amostrado. Se timestamp/atualização não delimitar o lote, não rotular CPU como tempo exato.
7. **Dez repetições:** manter como orçamento inicial sob avaliação de variabilidade; não dizer que n=10 garante poder estatístico. Se carga curta produzir telemetria ruim, ajustar instrumentos ou duração **antes de congelar o plano**.
8. **Aquecimento:** só declarar que houve aquecimento das rotas mutantes se isso for realmente possível sem perder a independência do estado; GET de readiness não substitui warmup do caminho crítico.

## 7. Onde e quanto citar na monografia

- **Fundamentação:** no máximo 1 parágrafo de contextualização sobre avaliação de desempenho/reprodutibilidade, caso ainda não esteja explicado; não repetir Docker/Kubernetes aprovados no TCC1.
- **Metodologia TCC2:** cerca de 2–3 parágrafos bem articulados para (i) escolhas de métricas e validade (F01), (ii) repetições e incerteza (F02/F05), (iii) blocos e ordem (F03). Especificação da fonte técnica somente junto à definição concreta de CPU/memória (F09/F10/F11), e limitação kind (F13). Quantidade exata de parágrafos depende da revisão do capítulo atual.
- **Resultados:** gráficos, tabelas e medidas vêm dos **ZIPs experimentais reais**, não do Perplexity. Citações só para interpretar metodologia e ameaças à validade, sem atribuir nossos resultados aos artigos.
- **Conclusão:** não acrescentar referência nova de último momento; sintetizar o que nossos dados permitirem.

## 8. Pendências e rastreabilidade

- Inspecionar capítulo `capitulos/cap-metodologia-tcc2.tex` antes da escrita final; preservar trechos aprovados do TCC1.
- Verificar metadados/links da seleção diretamente na editora/repositório e normalização dos nomes no BibTeX. As páginas IEEE/USENIX/Kent/Kubernetes/Linux/kind foram consultadas na triagem; os PDFs completos não foram relidos integralmente nesta etapa.
- Atribuir citações apenas às alegações sustentadas. Referências em inglês serão lidas no original, mas todo texto do TCC será em português brasileiro, com paráfrases originais e vocabulário técnico adequado.
- Submeter ao orientador decisões de comparabilidade, controle de carga e unidade experimental antes de V12. Nenhuma alteração de código, métricas, resultados ou texto da monografia foi executada nesta triagem.

**Decisão editorial:** USAR SELETIVAMENTE — 4 fontes científicas centrais e documentação técnica diretamente necessária. Manter os demais materiais para consulta, não como obrigação de citação.
