"""Tabelas legíveis e gráfico de contrastes; lê somente o pacote derivado."""
import csv
import io
import json
from pathlib import Path
from statistics import median, quantiles
from zipfile import ZipFile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from m01_analyze import read_package, br, summarize

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'capitulos/dados-e11-m01'

def write(name, rows):
    (OUT/name).write_text('\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n'+r'\bottomrule'+'\n',encoding='utf-8')

def main():
    runs,requests=read_package(ROOT/'E11-M01-auditoria-extracao.zip')
    assert len(runs)==30 and len(requests)==30000
    rows=list(csv.DictReader((ROOT/'docs/tcc2/e11-m01-metricas-por-rodada.csv').open(encoding='utf-8')))
    indexed={(r['block'],r['scenario']):r for r in rows}
    blocks=[f'B{i:02d}' for i in range(1,11)]
    assert set(indexed)=={(b,s) for b in blocks for s in ('C2','C3','C4')}
    for r in runs:
        assert abs(float(indexed[r['block'],r['scenario']]['batch_s'])-int(r['batch_elapsed_ns'])/1e9)<1e-8
    metrics=[('batch_s','Lote (s)'),('requests_s','Vazão (req/s)'),('rtt_median_ms','RTT mediano (ms)'),
             ('rtt_p95_ms','RTT p95 (ms)'),('rtt_p99_ms','RTT p99 (ms)'),('rtt_range_ms','Amplitude RTT (ms)')]
    for part in (0,1):
        table=[]
        for key,label in metrics[part*3:part*3+3]:
            for s in ('C2','C3','C4'):
                stats=summarize([float(indexed[b,s][key]) for b in blocks])
                table.append((label,s,*map(br,stats)))
        write(f'publicacao-resumo-{part+1}.tex',table)
    write('publicacao-tempos.tex',[(b,'/'.join(sorted(('C2','C3','C4'),key=lambda s:int(indexed[b,s]['position']))),
                                  *(br(float(indexed[b,s]['batch_s'])) for s in ('C2','C3','C4'))) for b in blocks])
    contrasts=[]
    details=[]
    for a,z in [('C3','C2'),('C4','C2'),('C4','C3')]:
        delta=[float(indexed[b,a]['batch_s'])-float(indexed[b,z]['batch_s']) for b in blocks]
        ratio=[float(indexed[b,a]['batch_s'])/float(indexed[b,z]['batch_s']) for b in blocks]
        for label,data in [('Diferença (s)',delta),('Razão',ratio)]:
            contrasts.append((f'{a}/{z}',label,*[br(x,3 if label=='Razão' else 2) for x in summarize(data)]))
        details.append((a,z,delta,ratio))
    write('publicacao-contrastes.tex',contrasts)
    write('publicacao-diferencas.tex',[(b,*[br(d[2][i]) for d in details]) for i,b in enumerate(blocks)])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'pdf.fonttype':42})
    fig,axes=plt.subplots(3,1,figsize=(7,6),sharex=True,layout='constrained')
    for ax,(a,z,delta,_),color in zip(axes,details,['#235789','#ac4619','#207259']):
        ax.axhline(0,color='#555',lw=.8)
        ax.plot(blocks,delta,marker='o',color=color)
        ax.set_ylabel(f'{a} − {z}\n(s)')
        ax.grid(axis='y',alpha=.25)
    axes[-1].set_xlabel('Bloco (todos preservados)')
    fig.savefig(ROOT/'figuras/e11-m01-contrastes-pareados.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)
    print('5 tabelas de apresentação e 1 gráfico pareado gerados a partir dos dados auditados.')

if __name__=='__main__': main()
