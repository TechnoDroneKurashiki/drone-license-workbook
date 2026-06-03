# -*- coding: utf-8 -*-
"""成果物一式をzip化する（元資料・PDFは除外）。リポジトリ直下で実行する。"""
import zipfile, os

inc_files = ['README.md', '.gitignore', 'index.html', '二等ドローン学科クイズ.html']
inc_dirs = ['data', 'workbook', 'scripts']
PREFIX = 'drone-license-workbook/'

with zipfile.ZipFile('drone-license-workbook.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in inc_files:
        if os.path.exists(f):
            z.write(f, PREFIX + f)
    for d in inc_dirs:
        for root, _, files in os.walk(d):
            for fn in files:
                p = os.path.join(root, fn)
                arc = PREFIX + p.replace(os.sep, '/')
                z.write(p, arc)

names = zipfile.ZipFile('drone-license-workbook.zip').namelist()
print('zip entries:', len(names))
print('size:', os.path.getsize('drone-license-workbook.zip'), 'B')
