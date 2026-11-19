# Etapa 14 técnica — revisão e consolidação da monografia

Atividade iniciada em 18/11/2026, horário de São Paulo. Escopo autorizado: ampliar a monografia, integrar os materiais ao template UTFPR e publicar na branch master, preservando objetivos e evidências.

## 1. Planejamento efetivamente disponível

Foram consultados o final de `STATUS_ATUAL_TCC2.md`, o laudo da Etapa 12, o diagnóstico da Etapa 11, o pré-registro E11-M00-v1 e a auditoria seletiva da pesquisa metodológica. A seção 10 do diagnóstico da Etapa 11 situa as Etapas 12–15 no tratamento dos resultados e na construção/revisão do LaTeX. O status diferencia a Etapa 12 técnica da Etapa 12 do macroplanejamento (defesa).

`CONTEXTO_MESTRE_TCC2.md` e `Planejamento TCC2.txt` não foram encontrados no clone nem nas buscas específicas acessíveis. Não foi possível confirmar uma primeira atividade formalmente numerada como Etapa 14 no macroplanejamento. A primeira atividade operacional desta etapa foi o diagnóstico da integração existente, seguido da revisão editorial solicitada pelo acadêmico. Não se atribuiu ao planejamento ausente uma decisão presumida nem se iniciou a preparação de slides.

## 2. Base e preservação

- Clone inicial: `tcc2/desenvolvimento`, HEAD `ac674ebe18c522235be0b7875bff7b9cb193d3a7`, com mudanças locais das Etapas 12 e 13, ainda não publicadas.
- Master consultada: `05ed7d674ca34cd22e2434e4db19e9402b9c23d6`. A comparação remota confirmou que esse commit é ancestral de desenvolvimento, sem divergência, com 378 commits à frente no desenvolvimento antes desta edição.
- O PDF final aprovado do TCC1 não foi localizado. A preservação foi conferida contra os arquivos versionados da master indicada; isso não substitui conferência futura com o PDF aprovado.
- A fundamentação não foi editada nesta atividade. Em relação à master do TCC1, desenvolvimento contém 27 linhas acrescentadas anteriormente e nenhuma linha removida nesse capítulo. Os objetivos aprovados foram preservados; apenas a descrição da estrutura foi atualizada na introdução.
- Não foram executados benchmarks, POSTs, reinicializações ou operações Docker/Kubernetes. A análise leu o pacote derivado. Um recorte de topologia foi extraído para documentação de um ZIP original em modo de leitura.

## 3. Conteúdo acrescentado e organização

- Novo capítulo de implementação: origem do núcleo Python, trechos originais, ajustes funcionais, cadeia lógica, divisão de estado, snapshot, identidade de mensagens, limites de deduplicação e evolução C0–C4.
- Seis diagramas vetoriais em `figuras/`: arquitetura, sequência, camadas do ambiente, topologias C2/C3/C4, ciclo de rodada e rastreabilidade. O gerador é `gerar_ilustracoes_monografia.py`. São diagramas documentais; não são screenshots de execuções.
- Quatro listagens: dois trechos originais, um trecho da adaptação e a configuração kind. Os três arquivos originais recuperados têm SHA de blob Git idêntico à revisão de origem; ver `codigo-original/PROVENIENCIA.md`.
- Metodologia ampliada: ambiente, recursos, carga, unidade experimental, blocos, pontos de medição, inicialização fria, auditoria e limites inferenciais.
- Resultados com tabelas em tamanho legível, sem redução global por `resizebox`: resumos por cenário, tempos por bloco, diferenças e razões em apresentações separadas. Novo gráfico de diferenças pareadas; todos os blocos mantidos.
- Conclusões em cinco seções: resposta à pesquisa, objetivos/contribuições, avaliação temporal, limitações e trabalhos futuros.
- Agradecimentos propostos para revisão pessoal; declaração genérica CAPES removida por ausência de evidência de financiamento. Lista de siglas, lista de códigos e dois apêndices incorporados.
- Recorte real C4/B10: `e11-m01-exemplo-c4-b10-topology-end.json`, extraído de ZIP SHA-256 `a21bd54e385d70923ed2e6b84e7be6a46a41a592fdd5257cdf5385927978b24d`. CRC e hash interno do arquivo conferidos. A tabela documental utiliza somente campos efetivamente arquivados.

## 4. Bibliografia e apresentação

Foram integradas seletivamente quatro fontes científicas da pesquisa metodológica: Papadopoulos et al. (2021), Maricq et al. (2018), Duplyakin et al. (2023) e Kalibera e Jones (2013). Metadados e pertinência foram conferidos em IEEE/MDU, USENIX e no repositório da Universidade de Kent. O ano 2021 corresponde à edição final do artigo de Papadopoulos, cujo DOI contém 2019. Foi incluída a documentação oficial kind e uma referência versionada ao código original. Não foram inseridas as fontes de telemetria sem aplicação direta ao texto final.

`main.bib` contém 303 chaves distintas após a integração, sem duplicação de chaves. As novas entradas foram confrontadas com as existentes por título/DOI. O estilo `abntex2-alf.bst` e a classe UTFPR foram mantidos. Os ajustes de compatibilidade das Etapas 12/13 foram preservados; a edição acrescentou correção da largura do quadro de licença, remoção do número da versão do template na capa e ajustes de listas. A fonte vetorial da licença passou a ter cópia PDF, evitando conversão EPS no Overleaf.

## 5. Validação e situação de publicação

A validação final, os hashes de entrega e a situação remota são registrados no checkpoint ao final de `STATUS_ATUAL_TCC2.md`. O relatório `etapa-14-validacao.json` registra os controles automáticos da entrega. Compilar com `pdfx` não certifica conformidade PDF/A por si só; não foi emitido um laudo formal de PDF/A.

A tentativa de acesso ao Overleaf pela interface foi interrompida pela ferramenta porque ela não conseguiu verificar a URL do navegador com segurança. Nenhum projeto foi alterado no Overleaf. A compilação foi realizada localmente com pdfLaTeX/BibTeX; o pacote compacto foi preparado para importação. `LEIA-ME-OVERLEAF.md` documenta os passos.

## 6. Validação acadêmica pendente

Revisão do orientador; conferência com o PDF final do TCC1 quando disponível; aceite pessoal dos agradecimentos; emissão/inclusão da folha oficial de aprovação; validação institucional dos requisitos de depósito e PDF/A. A ausência de CPU/RAM durante lotes, a serialidade, o host físico único e a análise descritiva permanecem explícitos. Nenhuma aprovação acadêmica foi presumida.
