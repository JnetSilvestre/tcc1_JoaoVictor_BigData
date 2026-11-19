"""Diagramas documentais da arquitetura; não executa Docker, Kubernetes ou HTTP."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'figuras'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'pdf.fonttype': 42})
BLUE, GREEN, ORANGE, GREY = '#e9f0f7', '#e8f2ed', '#fff0df', '#f2f3f5'

def canvas(h):
    fig, ax = plt.subplots(figsize=(7.1, h))
    ax.set(xlim=(0, 100), ylim=(0, h*14))
    ax.axis('off')
    fig.subplots_adjust(left=.015, right=.985, bottom=.02, top=.98)
    return fig, ax

def box(ax, x, y, w, h, text='', color=BLUE, size=10, bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.35,rounding_size=1',
                               facecolor=color,edgecolor='#415366',linewidth=1))
    if text:
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,
                weight='bold' if bold else 'normal',linespacing=1.45)

def arrow(ax, a, b, label='', offset=(0,0)):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'-|>','color':'#334155','lw':1.2})
    if label:
        ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,
                ha='center',va='center',fontsize=9,backgroundcolor='white')

def save(fig, name):
    fig.savefig(OUT/name,metadata={'CreationDate':None,'ModDate':None},bbox_inches='tight')
    plt.close(fig)

def architecture():
    fig, ax=canvas(5.5)
    box(ax,2,59,96,15,'Núcleo Python de referência\nAttribute → Premise → Condition → Rule → Action → Instigation',GREY)
    arrow(ax,(50,59),(50,54))
    ax.text(50,51,'Adaptação: fronteiras de processo e estado explícitas',ha='center',weight='bold')
    box(ax,2,30,29,16,'attribute-source\nValores autoritativos\nSequência por atributo',BLUE)
    box(ax,36,30,29,16,'logic-engine\nAtributos espelhados\nPremissas e condição',GREEN)
    box(ax,70,30,28,16,'rule-executor\nCondição remota\nRegra, ação e efeitos',ORANGE)
    arrow(ax,(31,38),(36,38)); arrow(ax,(65,38),(70,38))
    ax.text(34,26,'AttributeChanged',ha='center',fontsize=9)
    ax.text(69,22,'ConditionChanged',ha='center',fontsize=9)
    box(ax,2,3,96,13,'HTTP/JSON síncrono nas duas fronteiras\nrun_id · event_id · sequence · caused_by\nEstado e registros de deduplicação em memória; uma réplica por papel',GREY,9.5)
    save(fig,'tcc2-arquitetura-servicos.pdf')

def sequence():
    fig, ax=canvas(6.2)
    xs=[10,36,63,90]
    for x,title in zip(xs,['Cliente','attribute-\nsource','logic-\nengine','rule-\nexecutor']):
        box(ax,x-9,75,18,9,title,GREY,9)
        ax.plot([x,x],[7,74],color='#a0a7b0',ls='--',lw=.8)
    steps=[(10,36,69,'Inicializar rodada'),(36,63,61,'Snapshot de atributos'),
           (63,90,53,'Snapshot de condição'),(90,10,45,'Confirmações de inicialização'),
           (10,36,34,'POST de mudança'),(36,63,26,'AttributeChanged'),
           (63,90,18,'ConditionChanged'),(90,10,9,'Respostas síncronas até o cliente')]
    for a,b,y,t in steps:
        arrow(ax,(a,y),(b,y)); ax.text((a+b)/2,y+2,t,ha='center',fontsize=9,backgroundcolor='white')
    ax.text(50,40,'Exemplo: mudança que torna a condição verdadeira',ha='center',weight='bold',fontsize=9)
    save(fig,'tcc2-sequencia-notificacoes.pdf')

def topology():
    fig, ax=canvas(6.6)
    box(ax,1,1,98,89,color=GREY)
    ax.text(50,86,'UM COMPUTADOR FÍSICO · Windows / WSL2 / Docker Desktop',ha='center',weight='bold',fontsize=9)
    box(ax,4,61,92,20,color='white')
    ax.text(7,77,'C2 · rede Docker bridge interna',weight='bold',fontsize=10)
    for x,t in [(7,'Cliente'),(29,'Atributos'),(51,'Lógica'),(73,'Executor')]: box(ax,x,64,19,8,t,BLUE,9)
    for x in [26,48,70]: arrow(ax,(x,68),(x+3,68))
    box(ax,4,34,92,23,color='white')
    ax.text(7,53,'C3 · cluster kind',weight='bold')
    box(ax,7,37,24,11,'control-plane\nControle do cluster',GREY,8.5)
    box(ax,35,37,58,11,'worker\nCliente → Atributos → Lógica → Executor',GREEN,9)
    box(ax,4,5,92,25,color='white')
    ax.text(7,26,'C4 · mesmo cluster kind',weight='bold')
    box(ax,7,9,29,12,'control-plane\nControle + Lógica',ORANGE,9)
    box(ax,55,9,38,12,'worker\nCliente → Atributos\nExecutor',GREEN,9)
    arrow(ax,(55,18),(36,18),'atributos',offset=(0,3))
    arrow(ax,(36,11),(55,11),'condição',offset=(0,-3))
    save(fig,'tcc2-topologias-c2-c3-c4.pdf')

def environment():
    fig,ax=canvas(5.2)
    box(ax,1,1,98,70,color=GREY)
    ax.text(50,66,'Host físico · i5-9300H · 4 núcleos / 8 processadores lógicos',ha='center',weight='bold',fontsize=9)
    box(ax,5,5,90,55,color='white')
    ax.text(50,55,'Windows 10 → WSL2 → Docker Desktop / Engine Linux',ha='center',weight='bold',fontsize=9)
    box(ax,9,11,28,36,color=BLUE)
    ax.text(23,42,'Bancada C2',ha='center',weight='bold')
    box(ax,12,15,22,21,'3 serviços\n+ cliente\n\nRede bridge', 'white',9)
    box(ax,43,11,48,36,color=GREEN)
    ax.text(67,42,'Cluster kind · C3 ou C4',ha='center',weight='bold',fontsize=9)
    box(ax,46,15,20,21,'Nó-contêiner\ncontrol-plane\n\nPods', 'white',9)
    box(ax,69,15,19,21,'Nó-contêiner\nworker\n\nPods','white',9)
    ax.text(50,0,'As camadas e os nós compartilham CPU, RAM e o host físico.',ha='center',fontsize=9)
    save(fig,'tcc2-camadas-ambiente.pdf')

def lifecycle():
    fig,ax=canvas(6.0)
    stages=[('1 · Plano e verificações','Código, imagem, capacidade e exclusividade'),
            ('2 · Bancada nova','IDs/UIDs, cotas e estado frio'),
            ('3 · Inicialização','Snapshot único confirmado pelos serviços'),
            ('4 · Janela temporal','1.000 POSTs seriais · sem coleta CPU/RAM'),
            ('5 · Validação e arquivo','Oráculo, logs, ZIP, hashes e backup'),
            ('6 · Encerramento controlado','Revisão de identidade e consentimento')]
    for i,(a,b) in enumerate(stages):
        y=69-i*12
        box(ax,3,y,64,10,a+'\n'+b,BLUE if i!=3 else GREEN,9.5)
        if i<5: arrow(ax,(35,y),(35,y-2))
    box(ax,75,29,22,24,'Falha em\nqualquer etapa\n\nInterromper e\npreservar\nevidências',ORANGE,9)
    ax.plot([71,71],[8,74],color='#7f8995',lw=1)
    for i in range(6): ax.plot([67,71],[74-i*12]*2,color='#7f8995',lw=1)
    arrow(ax,(71,41),(75,41))
    ax.text(35,2,'Avançar para o próximo cenário/bloco após o encerramento',ha='center',fontsize=8.5)
    save(fig,'tcc2-ciclo-rodada.pdf')

def evidence():
    fig,ax=canvas(4.9)
    box(ax,2,49,43,17,'Evidências originais\n30 ZIPs + 60 journals\nEntradas, logs, estado e topologia',BLUE,9.5)
    box(ax,55,49,43,17,'Cópias de preservação\n30 backups com SHA-256 igual\nVolumes C: e D:',GREY,9.5)
    arrow(ax,(45,57),(55,57),'hash',offset=(0,3))
    box(ax,23,26,54,15,'Extração verificada · pacote derivado\ninventario.json · rodadas.csv\nrequisicoes.csv · checksums.sha256',GREEN,9.5)
    arrow(ax,(24,49),(37,41));arrow(ax,(76,49),(63,41))
    box(ax,2,3,43,14,'Síntese por rodada\n30 linhas de métricas\nPareamento por bloco',BLUE,9.5)
    box(ax,55,3,43,14,'Monografia\nTabelas e gráficos reproduzíveis\nAfirmações com escopo delimitado',ORANGE,9.5)
    arrow(ax,(40,26),(24,17));arrow(ax,(45,10),(55,10))
    save(fig,'tcc2-rastreabilidade.pdf')

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for f in (architecture,sequence,topology,environment,lifecycle,evidence): f()
    print('6 diagramas documentais gerados; nenhuma execução experimental.')
