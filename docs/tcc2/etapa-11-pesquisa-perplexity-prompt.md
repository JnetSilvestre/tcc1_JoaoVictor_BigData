# TCC2 — Etapa 11: prompt para pesquisa bibliográfica no Perplexity

Você atuará como pesquisador técnico-científico em Engenharia da Computação, com foco em metodologia experimental e revisão bibliográfica. Não escreva uma monografia pronta; prepare um dossiê de evidências verificáveis para análise crítica e posterior redação autoral em LaTeX conforme modelo UTFPR e referências ABNT/BibTeX.

CONTEXTO RIGOROSO DO ESTUDO
Investigação da viabilidade de distribuição de uma prova de conceito Python inspirada no Paradigma Orientado a Notificações (PON) em um cluster Kubernetes. Cenários: C0 núcleo Python local (sem transporte), C1 três processos HTTP/JSON em host local, C2 três contêineres Docker, C3 três Pods Kubernetes no mesmo worker virtual, C4 três Pods em dois nós kind virtuais, ambos em um ÚNICO computador físico Windows 10 com Docker Desktop/WSL2. A prova de conceito NÃO equivale à implementação completa do NOP Query em C++; NÃO houve demonstração de distribuição entre computadores físicos. A comunicação da aplicação é HTTP/JSON síncrona e atualmente serial. Os primeiros pilotos C3 e C4 com 100 requisições foram funcionalmente aprovados, mas NÃO constituem série estatística e NÃO permitem afirmar ganhos de desempenho.

PERGUNTAS DE PESQUISA
1. Como planejar comparações reproduzíveis entre execução local, Docker e Kubernetes controlando transporte, sistema operacional, limites de CPU/memória, posicionamento, aquecimento, carga e variáveis de confusão?
2. Como medir corretamente RTT/latência por operação, duração de lote, throughput de requisições, notificações e efeitos, diferenciando GET, no-op e alteração com encadeamento de mensagens?
3. Como medir tempo de CPU cumulativo e working set por contêiner usando cgroup v2, kubelet Summary API ou ferramentas Docker? Quais diferenças de definição, frequência de atualização, granularidade temporal, overhead e precisão? Qual é a cautela necessária ao usar usageCoreNanoSeconds, workingSetBytes, cpu.stat, memory.current e memory.peak? Procure documentação primária.
4. Qual é o desenho estatístico defensável para 100, 1000 e 10000 requisições, alvo inicial de 10 repetições independentes por cenário/carga, ordem de execução balanceada, tratamento de falhas, distribuição assimétrica, mediana, dispersão, intervalos de confiança e tamanho de efeito? Explique limitações de potência e pseudorreplicação.
5. Quais limitações científicas existem quando dois nós kind compartilham o mesmo host físico e o mesmo orçamento Docker/WSL2? Como relatar viabilidade funcional versus custo/overhead, sem extrapolar para escala física?

ESCOPO E FONTES
Priorize de 8 a 12 trabalhos científicos relevantes, publicados preferencialmente entre 2018 e novembro de 2026, admitindo anteriores que sejam fundamentos metodológicos. Separe-os de 3 a 6 documentos técnicos primários oficiais (Kubernetes, Linux kernel/cgroup v2, Docker, Python, NIST se pertinente). Priorize artigos revisados por pares, livros acadêmicos de métodos e documentação oficial. Preprints, posts e benchmarks comerciais devem ser identificados como evidência inferior. Evite estudos que não testem cenários comparáveis, e explicite diferenças de linguagem, protocolo e hardware. Não invente autor, DOI, editora, data, URL, resultado, página ou citação.

ENTREGÁVEIS — EM PORTUGUÊS DO BRASIL
A. Síntese executiva de até 600 palavras: o que a literatura realmente sustenta, pontos controvertidos e lacunas aplicáveis.
B. Matriz de evidências em tabela Markdown, uma linha por fonte: ID [F01...], referência completa, ano, tipo (artigo/doc oficial/preprint), DOI quando existente, URL primária acessível, estudo e ambiente, métricas, método estatístico, achado relevante sem extrapolação, limitação, seção/página ou trecho verificável.
C. Recomendações metodológicas para o nosso E11, separadas em ESSENCIAL, DESEJÁVEL e NÃO JUSTIFICADO; para cada recomendação, cite IDs da matriz de evidências e indique se é proposta sua ou se é orientação explícita da fonte.
D. Matriz de rastreabilidade associando às hipóteses e métricas: RTT, throughput, CPU cumulativa, memória/working set, correção por oráculo, custos de rede/virtualização, warmup, repetições e ameaças à validade.
E. Indique exatamente como comparar C2/C3/C4 e quais fatores impedem tratar C0/C1 como contrastes causais isolados do Kubernetes.
F. Bibliografia em BibTeX em bloco de código, um registro por fonte, com chave estável F01 etc, DOI e URL verificados. Não gere BibTeX quando a verificação da fonte for impossível: marque PENDENTE e explique.
G. Uma lista de no máximo 8 perguntas de revisão para o orientador e um checklist de decisões instrumentais pendentes antes de congelar V12.

REGRAS DE VERIFICABILIDADE
Para cada afirmação substantiva inclua o ID [Fxx] que lhe dá suporte; distingua claramente achados documentados, inferências e recomendações. Forneça link para publicação oficial ou DOI que realmente resolva, não apenas resultados de busca. Não crie citações literais longas; caso cite, use uma expressão breve com página/seção confirmada. Para qualquer documento ao qual não tenha acesso integral, informe que leu somente o resumo ou metadados. Não atribua conclusões específicas a um artigo sem ler a parte relevante. Não apresente números de ganho/overhead do nosso projeto, nem invente benchmarks. Se não encontrar fontes adequadas, informe a lacuna.

FORMATO PARA REUSO NO CHATGPT
Produza o material como Markdown estruturado, de preferência um único arquivo chamado pesquisa_metodologica_e11_perplexity.md; se for possível, também entregue referencias_e11_perplexity.bib com os BibTeX verificados. Comece com data de pesquisa e fontes pesquisadas, mantenha as etiquetas [F01...] consistentes entre tabela, texto e BibTeX. Não substitua referências por links não resolvíveis. A redação final será feita posteriormente pelo ChatGPT sob revisão do acadêmico, preservando evidências, ABNT e o projeto LaTeX UTFPR.
