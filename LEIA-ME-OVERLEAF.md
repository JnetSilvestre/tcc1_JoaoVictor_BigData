# Monografia TCC2 — compilação e revisão

O documento principal é **main.tex**. A classe institucional `utfpr.cls`, o estilo `abntex2-alf.bst`, os capítulos, a bibliografia e as figuras estão no projeto original. A implementação e as evidências derivadas acompanham o repositório.

## 1. Importar no Overleaf

1. Baixe o ZIP da branch **master** ou utilize `output/overleaf/TCC2-Overleaf.zip`, que contém os arquivos necessários à compilação.
2. No Overleaf da universidade, crie um projeto com **Upload Project** e selecione o ZIP. Para substituir um projeto existente, mantenha uma cópia da versão anterior.
3. Defina **main.tex** como documento principal e **pdfLaTeX** como compilador.
4. Compile. Caso a plataforma mantenha auxiliares antigos, utilize **Recompile from scratch**.
5. Confira sumário, listas, referências e as páginas finais. Nenhum comando de Docker/Kubernetes ou benchmark é necessário para compilar.

## 2. Arquivos principais

| Conteúdo | Local |
| --- | --- |
| Identificação, título e orientador | `variaveis.tex` |
| Resumo, abstract e agradecimentos | `PreTexto/` |
| Introdução, fundamentação e proposta preservada | `capitulos/` |
| Implementação e ambiente | `capitulos/cap-implementacao-tcc2.tex` |
| Metodologia, resultados e conclusões | `capitulos/cap-metodologia-tcc2.tex`, `capitulos/cap-resultados.tex`, `capitulos/cap-conclusoes.tex` |
| Figuras e gráficos | `figuras/` |
| Tabelas reproduzíveis | `capitulos/dados-e11-m01/` |
| Bibliografia efetiva | `main.bib` |
| Trechos originais e proveniência | `docs/tcc2/codigo-original/` |
| Procedimentos e rastreabilidade | `PosTexto/apendice-*.tex` |
| PDF compilado para revisão | `output/pdf/TCC2-monografia.pdf` |

## 3. Pendências acadêmicas

- Revisão pelo orientador e confirmação da redação final.
- Revisão pessoal dos agradecimentos pelo autor. Não foi mantida a declaração genérica de financiamento CAPES do template, pois não há comprovação desse financiamento para este trabalho.
- Inserção da folha oficial de aprovação após sua emissão. O arquivo de exemplo `PreTexto/folha-aprovacao.pdf` **não está incluído** no documento. Não habilitar o exemplo como se fosse aprovação real.
- Conferência institucional final dos requisitos de depósito e PDF/A. A compilação com o pacote `pdfx` não substitui uma validação formal de conformidade.

## 4. Reproduzir os resultados publicados sem novos experimentos

Com Python 3.13 e Matplotlib 3.10.7, a partir da raiz do repositório completo:

```powershell
python -B prova-conceito/benchmark/m01_analyze.py E11-M01-auditoria-extracao.zip
python -B prova-conceito/benchmark/m01_publication.py
python -B docs/tcc2/gerar_ilustracoes_monografia.py
```

O pacote compacto para Overleaf contém os resultados e os trechos de código usados pela monografia. O repositório completo contém também o pacote derivado e os scripts de reprodução. Os ZIPs brutos e os journals experimentais permanecem no acervo original de evidências.
