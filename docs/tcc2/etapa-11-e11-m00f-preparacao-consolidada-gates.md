# E11-M00F — Preparação consolidada pré-campanha (um bloco PowerShell)

**Data:** 17/11/2026 (America/Sao_Paulo). **Código:** `prova-conceito/scripts/e11_m00f_preparacao_consolidada.ps1`. **Status:** implementado, **sem execução no Windows**; validação real é obrigatória.

## Escopo e garantias

O acadêmico solicitou evitar sucessivos blocos de preparação antes da execução real. Foi preparado um script único que: (1) confirma branch Git limpa e SHA; (2) compila e roda **116 testes sintéticos esperados** (106 antes confirmados + 10 adicionados no executor de encerramento C2-S01); (3) confere contexto Docker, cgroup v2, imagem imutável, dois nós kind Ready e RAM física/discos acima dos limiares; (4) verifica hashes do ZIP C2-S01 original, backup em D e fixture; (5) repete a prévia segura de desmobilização; (6) produz YAML **novos C3/C4** com label `m01-s01` **sem aplicar**, e roda `kubectl apply --dry-run=client --validate=strict`; (7) solicita **aprovação interativa explícita** antes de desmobilizar **somente quatro contêineres novos e rede C2-S01** pelos **cinco IDs imutáveis já auditados**; (8) confere journal `COMPLETE`, inventário histórico Docker/Kube inalterado, ausência de recursos novos residuais e integridade preservada dos dois ZIPs.

**NENHUM comando do script aplica manifestos Kubernetes, executa snapshot/POST, inicia C3/C4, ou inicia as 30 medições B01–B10.** Isso é deliberado: a primeira operação mutante do executor C2-S01 **ainda não foi validada no Windows** e exige consentimento e inspeção do retorno. Não declarar E11-M01 liberado apenas porque YAML fez dry-run. C3/C4 ainda exigem qualificação operacional real e fluxo de backup + desmobilização com UID/allowlist; campanha de 30 ainda requer mecanismo generalizado e testado de encerramento por rodada.

## Segurança operacional

- A tentativa de retire C2-S01 é **a única parte mutante de recursos Docker/Kubernetes**, e só ocorre após todas as verificações precedentes e digitação de `AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C2_M01_S01` em `Read-Host`.
- Sem a frase, o script encerra **sem retirar C2-S01**; sem compilação, regressão, prévia, capacidade, backup, imagem ou dry-run válido, para antes da autorização.
- O executor subjacente `benchmark.retirement_execute_c2_s01` recusa divergências de IDs/labels, ZIP, outra bancada nova, falta de journal exclusivo, SHA do HEAD testado, Git sujo e reexecuções após falha. Para cada comando autorizado grava BEFORE/AFTER em `D:\TCC2-Backup\E11-M00E\C2-m01-s01-retirement.jsonl` com `fsync`, recusa `docker rm -f` e `prune`. Não toca nos históricos.
- Após retirada, o script compara inventário de nomes/IDs de todos os **recursos históricos** no Docker e namespace names/UIDs Kubernetes. Isso não garante equivalência de todo estado volátil, mas detecta uma mudança inesperada de identidade. Nunca reiniciar históricos.
- Manifestos C3/C4 são gerados em `$env:USERPROFILE\TCC2-Evidencias\E11-M00F\dry-run-<sha12>`, fora do repositório. O dry-run é de **cliente** porque o Namespace inexistente no momento da validação não persiste em server-side dry-run para ConfigMap/Deployments posteriores no mesmo arquivo.
- A prévia em modo read-only da retirada C2-S01 foi previamente observada PASS e contém somente **quatro contêineres, uma rede**, sem namespaces novos.
- **Não repetir automaticamente** uma tentativa com falha parcial; o journal preservado impede nova execução no mesmo estado. O arquivo ZIP original e o backup permanecem intocados.

## Próximas fases após conclusão comprovada

1. Inspecionar retorno `RESULTADO: E11_M00F_C2_CLOSED_READY_FOR_KUBE_QUALIFICATION` e o journal persistido. Se o usuário não autorizar, permanece bloqueado sem mutações.
2. Qualificar C3 e C4 em namespaces inéditos, com execução real de 1000 POSTs **sacrificiais**, independente da série, gates de CPU/memória/UID reais, ZIP/backup em D e programa de encerramento de namespace por UID com aprovação específica.
3. Aprovar ferramenta geral de criação/arquivamento/retirada **uma bancada por vez**, preservando todos os históricos e cenário de falha, para os 30 lotes predefinidos. Não inferir comparabilidade física do cluster multinó kind.
4. Revalidar RAM Windows >=3 GiB, disco >=15 GiB e quotas antes da **primeira rodada principal**; só então emitir liberação científica condicional documentada da E11-M01.

**Estado presente:** `E11_M00F_CONSOLIDATED_PREPARATION_SCRIPT_UNTESTED / E11_M01_BLOCKED`. O script foi versionado no GitHub, mas **não executado** no Windows pelo assistente e não é evidência de sucesso ou autorização de exclusão de recursos.
