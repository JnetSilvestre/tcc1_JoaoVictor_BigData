# TCC2 — Etapa 11 / E11-D02 — Auditoria da sondagem instrumental

Data: 15/11/2026. Fonte: captura de tela do PowerShell enviada pelo acadêmico (sem leitura do TXT bruto ou recálculo do hash exibido).
Status: descoberta de instrumentos APROVADA; sem benchmark, sem série científica, sem alteração de Pods C3/C4.

## Git
Mensagem vermelha git : From https://... classificada como saída informativa enviada pelo Git ao stderr e rotulada NativeCommandError pelo pipeline PowerShell. O pull avançou por fast-forward de f84c8384 a 72957299 e exibiu HEAD 72957299fe9dbffb66c9f99681a54c5787459919 e STATUS LIMPO.

## Kubelet Summary API
Endpoint /api/v1/nodes/<node>/proxy/stats/summary disponível em ambos os nós. Worker: cinco Pods dos namespaces C3/C4; control-plane: um Pod C4. Seis contêineres informaram CPU_COUNTER=True para cpu.usageCoreNanoSeconds e MEMORY=True para memory.workingSetBytes; timestamps presentes.
A existência dos campos não prova frequência de atualização, precisão nem granularidade suficiente para benchmark. Exige validação em instrumento e bancadas novos.
NETWORK=False é inconclusivo: o script consultou $pod.network.interface.rxBytes, enquanto a estrutura de NetworkStats documenta rxBytes no nível de network e interfaces (plural). Essa consulta gera falso negativo quando a propriedade singular não existe; corrigir no novo coletor.
Fonte: https://kubernetes.io/docs/reference/kubelet-api/stats.v1alpha1/

## Cgroups v2
Nos dois contêineres de nó kind foram legíveis cgroup.controllers, cpu.stat, memory.current, memory.peak; DOCKER_EXEC_EXIT=0. Os arquivos na raiz do nó kind não são por si medidas de serviço individual.

## Encaminhamento
Recomendação: Kubelet Summary API como primeira fonte candidata de CPU cumulativa por contêiner e working set amostrado, sem instalar Metrics Server ou Prometheus neste momento. Próximo incremento implementa sondagem de amostras sequenciais, identificação de Pod UID/container, janela de coleta, handling de reinício e ausência de dados, cliente persistente e verificação funcional por oráculo.
Preservar namespaces C3/C4. Não repetir E11-D02 por causa da cor vermelha. Não usar timestamps, uptime ou duração da coleta como dados científicos.
