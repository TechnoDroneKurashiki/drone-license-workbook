# -*- coding: utf-8 -*-
"""4バッチのmarkdownを科目（章）ごとにまとめて1ファイルへ統合し、
全200問の論点重複を検査する。問題番号は元のまま保持する。"""
import re, glob
from collections import Counter

files = sorted(set(glob.glob('二等学科対策問題集_0*.md') + glob.glob('二等学科対策問題集_1*.md')))

records = {}
for f in files:
    lines = open(f, encoding='utf-8').read().split('\n')
    cur_chap = None
    i = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r'^## (第\d章.*)', l)
        if m:
            cur_chap = m.group(1).strip()
        mq = re.match(r'^### 問題(\d+)', l)
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
            records[qn] = {'chap': cur_chap, 'stem': stem, 'opts': opts,
                           'ans': ans, 'expl': expl}
        i += 1

# ---- 統合markdownの生成（章ごと・番号は保持） ----
chap_order = ['第1章　無人航空機に関する規則', '第2章　無人航空機のシステム',
              '第3章　無人航空機の操縦者及び運航体制', '第4章　運航上のリスク管理']
out = []
out.append('# 二等無人航空機操縦士 学科試験対策問題集（オリジナル・全200問）')
out.append('')
out.append('> 国家試験対策用のオリジナル問題集です。三肢択一式・各セット完結型（問題／選択肢／正解／解説）で構成しています。')
out.append('> 対象：二等無人航空機操縦士 学科試験')
out.append('> 出題範囲：①無人航空機に関する規則 ②無人航空機のシステム ③無人航空機の操縦者及び運航体制 ④運航上のリスク管理')
out.append('> 全200問を科目ごとに整理しています（問題番号は作成時の通し番号を維持）。')
out.append('> ※本問題集は学習用に独自作成したものであり、実際の試験問題とは異なります。')
out.append('')
out.append('---')
out.append('')

for chap in chap_order:
    qns = sorted([q for q, r in records.items() if r['chap'] == chap])
    out.append('## {}（{}問）'.format(chap, len(qns)))
    out.append('')
    for q in qns:
        r = records[q]
        out.append('### 問題{}'.format(q))
        out.append(r['stem'])
        out.append('')
        for idx, o in enumerate(r['opts'], 1):
            out.append('{}. {}'.format(idx, o))
        out.append('')
        out.append('**正解：{}**'.format(r['ans']))
        out.append('')
        out.append(r['expl'])
        out.append('')
        out.append('---')
        out.append('')

open('二等学科対策問題集_全200問_統合版.md', 'w', encoding='utf-8').write('\n'.join(out))
print('統合markdown生成: 二等学科対策問題集_全200問_統合版.md')

# ---- 論点重複の検査（文字bi-gram Jaccard） ----
def norm(s):
    return re.sub(r'[\s、。「」（）()・/／,.]', '', s)

def bigrams(s):
    s = norm(s)
    return set(s[i:i+2] for i in range(len(s)-1))

# 比較対象は「問題文＋選択肢＋解説」を結合したテキスト
texts = {q: bigrams(r['stem'] + ''.join(r['opts']) + r['expl'])
         for q, r in records.items()}
qs = sorted(records)
pairs = []
for a in range(len(qs)):
    for b in range(a+1, len(qs)):
        qa, qb = qs[a], qs[b]
        s1, s2 = texts[qa], texts[qb]
        if not s1 or not s2:
            continue
        j = len(s1 & s2) / len(s1 | s2)
        if j >= 0.45:
            pairs.append((j, qa, qb))
pairs.sort(reverse=True)
print('\n=== 類似度0.45以上のペア（論点重複の疑い） ===')
if not pairs:
    print('該当なし')
for j, qa, qb in pairs[:40]:
    print('  {:.2f}  問{:>3} × 問{:<3}  [{}] / [{}]'.format(
        j, qa, qb, records[qa]['stem'][:24], records[qb]['stem'][:24]))
