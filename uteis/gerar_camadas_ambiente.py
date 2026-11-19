"""Diagramas documentais da arquitetura; não executa Docker, Kubernetes ou HTTP."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
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

def environment():
    fig,ax=canvas(5.2)
    box(ax,1,1,98,70,color=GREY)
    ax.text(50,66,'Host físico · i5-9300H · 4 núcleos / 8 processadores lógicos',ha='center',weight='bold',fontsize=9)
    box(ax,5,9,90,51,color='white')
    ax.text(50,55,'Windows 10 → WSL2 → Docker Desktop / Engine Linux',ha='center',weight='bold',fontsize=9)
    box(ax,9,11,28,36,color=BLUE)
    ax.text(23,42,'Bancada C2',ha='center',weight='bold')
    box(ax,12,15,22,21,'3 serviços\n+ cliente\n\nRede bridge', 'white',9)
    box(ax,43,11,48,36,color=GREEN)
    ax.text(67,42,'Cluster kind · C3 ou C4',ha='center',weight='bold',fontsize=9)
    box(ax,46,15,20,21,'Nó-contêiner\ncontrol-plane\n\nPods', 'white',9)
    box(ax,69,15,19,21,'Nó-contêiner\nworker\n\nPods','white',9)
    ax.text(50,4,'As camadas e os nós compartilham CPU, RAM e o host físico.',ha='center',fontsize=9)
    save(fig,'tcc2-camadas-ambiente.pdf')


if __name__ == '__main__':
    environment()
