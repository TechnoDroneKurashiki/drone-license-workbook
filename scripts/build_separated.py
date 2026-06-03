# -*- coding: utf-8 -*-
"""解答分離型を生成する。
問題1〜200を番号順に並べ（選択肢のみ）、末尾に『解答・解説』を集約する。"""
import re, glob

files = [f for f in sorted(set(glob.glob('二等学科対策問題集_0*.md') +
                               glob.glob('二等学科対策問題集_1*.md'))) if '統合' not in f and '解答分離' not in f]

records = {}
for f in files:
    lines = open(f, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        mq = re.match(r'^### 問題(\d+)', lines[i])
        if mq:
            qn = int(mq.group(1))
            stem = lines[i + 1].strip()
            opts = []
            j = i + 2
            ans = None
            while j < len(lines):
                mo = re.match(r'^([123])\. (.*)', lines[j])
                if mo:
                    opts.append(mo.group(2))
                if lines[j].startswith('**正解'):
                    ans = re.search(r'([123])', lines[j]).group(1)
                    break
                j += 1
            k = j + 1
            expl = ''
            while k < len(lines):
                if lines[k].startswith('---'):
                    break
                if lines[k].strip():
                    expl = lines[k].strip()
                    break
                k += 1
            records[qn] = {'stem': stem, 'opts': opts, 'ans': ans, 'expl': expl}
        i += 1

out = []
out.append('# 二等無人航空機操縦士 学科試験対策問題集（オリジナル・全200問／解答分離型）')
out.append('')
out.append('> 国家試験対策用のオリジナル問題集です。三肢択一式・解答分離型（問題1〜200のあとに「解答・解説」をまとめて掲載）。')
out.append('> 対象：二等無人航空機操縦士 学科試験')
out.append('> 出題範囲：①無人航空機に関する規則 ②無人航空機のシステム ③無人航空機の操縦者及び運航体制 ④運航上のリスク管理')
out.append('> ※本問題集は学習用に独自作成したものであり、実際の試験問題とは異なります。')
out.append('')
out.append('---')
out.append('')
out.append('## 問題')
out.append('')

for q in range(1, 201):
    r = records[q]
    out.append('### 問題{}'.format(q))
    out.append(r['stem'])
    out.append('')
    for idx, o in enumerate(r['opts'], 1):
        out.append('{}. {}'.format(idx, o))
    out.append('')

out.append('---')
out.append('')
out.append('## 解答・解説')
out.append('')
for q in range(1, 201):
    r = records[q]
    out.append('**問題{}：正解{}**'.format(q, r['ans']))
    out.append(r['expl'])
    out.append('')

open('二等学科対策問題集_全200問_解答分離型.md', 'w', encoding='utf-8').write('\n'.join(out))
print('生成:', len(records), '問')
