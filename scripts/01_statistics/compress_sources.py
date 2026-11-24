#!/usr/bin/env python3
"""Copy the per-month VioGén table excerpts into the package, losslessly compacted.
usage: compress_sources.py <out_dir>/sources <repository_root>/sources/01_statistics/bulletins [YYYY-MM ...]"""
import sys, glob, os
from pathlib import Path
import pymupdf

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
only = set(sys.argv[3:])
for f in sorted(src.glob('*.pdf')):
    ym = f.name[:7]
    if only and ym not in only:
        continue
    for old in dst.glob(f'{ym}_*.pdf'):
        old.unlink()
    d = pymupdf.open(f)
    d.subset_fonts()
    d.save(dst / f.name, garbage=4, deflate=True, clean=True)
total = sum(p.stat().st_size for p in dst.glob('*.pdf'))
print(len(list(dst.glob('*.pdf'))), 'excerpts,', round(total / 1e6, 1), 'MB')
