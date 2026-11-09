#!/usr/bin/env python3
"""Static scientific figure of the deterministic derivative, without a fitted law."""
import argparse
import csv
import os
from pathlib import Path
import tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'round6-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main(bundle):
    rows=list(csv.DictReader((bundle/'coefficients.csv').open()))
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.1),layout='constrained')
    ax=axes[0];small=[r for r in rows if r['gap_rational']]
    x=[int(r['n']) for r in small];y=[float(r['gap_sweeps']) for r in small]
    ax.bar(x,y,color=['#b74132' if v>0 else '#24738b' for v in y],width=.7)
    ax.axhline(0,color='#555555',lw=.8);ax.set_xticks(x)
    ax.set(xlabel='n',ylabel='Gap derivative Aₙ (sweeps per unit p)',title='Exact rational calculation')
    ax=axes[1]
    for parity,color,label in [(0,'#24738b','Even n'),(1,'#b74132','Odd n')]:
        chosen=[r for r in rows if int(r['n'])%2==parity]
        ax.plot([int(r['n']) for r in chosen],
                [float(r['gap_sweeps'])/int(r['n']) for r in chosen],
                'o-',ms=3,color=color,label=label)
    xx=np.geomspace(3,1025,200)
    ax.plot(xx,-.5*np.log(xx),'--',lw=1.2,color='#555555',label='−½ log n (reference, not fit)')
    ax.set_xscale('log');ax.set(xlabel='n (log scale)',ylabel='Aₙ / n',title='Candidate leading term; parity affects O(n)')
    ax.legend(frameon=False,fontsize=8,loc='lower left')
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('T=3 minus T=2 supplied-corner completion time',fontsize=12)
    fig.savefig(bundle/'scaling.png',dpi=180,metadata={'Software':'round6 deterministic coefficient plot'})
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    main(p.parse_args().bundle)
