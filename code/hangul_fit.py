"""Formal conditions of writing a language in Hangul — computation tool.
한글 표기의 형식 조건 — 계산 도구.

Reads pinned copies of PHOIBLE, WALS, Lexibank (lexibank-analysed), Glottolog and ABVD from a data folder
(--data, with subfolders phoible/ wals/ lexibank/ glottolog/ abvd/; see data/SOURCES.md) and writes the table.

  python hangul_fit.py run --data DATA --out OUT --version x1c     # exploratory edition 1
  python hangul_fit.py coverage --data DATA                        # symbol coverage only

Versions: v1, v2 = the two runs fixed in advance (they write fit-axes.tsv, bench.json, thresholds.json);
x1, x1a, x1b, x1c = revisions made after seeing results (they write explore-axes.tsv, explore-summary.json).
The site's "Record" page describes each. Earlier versions are kept so that their outputs can be rebuilt;
their consonant values contain a known defect (ç read as c), fixed from x1b on.

Standard library + numpy.
"""
import argparse, csv, io, json, math, os, sys, zipfile, unicodedata as ud
from collections import Counter, defaultdict

csv.field_size_limit(10**9)
SEED = 20261114
NBOOT = 2000
VERSION = 'v1'   # set by --version. v1, v2 = fixed in advance; x1 … x1c = revised after seeing results
X1 = ('x1', 'x1a', 'x1b', 'x1c')   # x1c = x1b + 방언 표시의 범위 · 수기 행의 표시
X1B = ('x1b', 'x1c')
V2P = ('v2',) + X1

# ---------------------------------------------------------------- 1. 자음 ----
# 세종 표기 판 3.2 대응표(mapping.csv)의 공통 행. 값은 2층 꼴(합류 판정용 열쇠).
CONS_FORM = {
    'p': 'ㅃ', 't': 'ㄸ', 'k': 'ㄲ', 'pʰ': 'ㅍ', 'tʰ': 'ㅌ', 'kʰ': 'ㅋ', 'b': 'ㅂ', 'd': 'ㄷ', 'ɡ': 'ㄱ',
    'f': 'ᅗ', 'v': 'ᄫ', 'β': 'ᄫ', 'θ': 'ᅊ', 'ð': 'ᅂ', 's': 'ㅅ', 'z': 'ᅀ', 'ʂ': 'ᄾ', 'ʃ': 'ᄾ',
    'ʐ': 'ᄿ', 'ʒ': 'ᄿ', 'ɕ': 'ㅅ', 'ts': 'ᅎ', 'tsʰ': 'ᅔ', 'dz': 'ᅏ', 'tʂ': 'ᅐ', 'tʂʰ': 'ᅕ',
    'tʃ': 'ㅉ', 'tɕ': 'ㅉ', 'tɕʰ': 'ㅊ', 'x': 'ᅘ', 'h': 'ㅎ', 'ɣ': 'ㄱ', 'm': 'ㅁ', 'n': 'ㄴ',
    'ɲ': 'ㄴ+ㅣ', 'ŋ': 'ᅌ', 'ɾ': 'ㄹ', 'r': 'ᄙ', 'l': 'ㄹㄹ', 'ʔ': 'ᅙ', 'j': '(ㅣ)', 'w': '(ㅜ)',
}
# 확장(현대 자모 근사 · 표기 변이). 새 배정이 아니라 「현대 한국어 ㅈ·ㅊ 계열이 포괄하는 소리」와 같은 표기 변이.
CONS_EXT = {
    'dʒ': 'ㅈ', 'dʑ': 'ㅈ', 'tʃʰ': 'ㅊ', 'ɥ': '(ㅟ)', 'ʎ': 'ㄹㄹ+ㅣ',
}
# 판 3 사이트의 언어별 행이 합류를 푼 선례(일관성 규칙 ①). 둘 다 있으면 앞의 것을 바꾼다.
RESOLVE = {('s', 'ɕ'): ('s', 'ᄼ')}
# 표기 변이 → 정규 기호
NOTATION = {'g': 'ɡ', 'ʈʂ': 'tʂ', 'ʈʂʰ': 'tʂʰ', 'cç': 'tɕ', 'cçʰ': 'tɕʰ', 'ɟʝ': 'dʑ', 'ʧ': 'tʃ',
            'ʤ': 'dʒ', 'ʦ': 'ts', 'ʣ': 'dz', 'ʨ': 'tɕ', 'ʥ': 'dʑ', 'ɡ̊': 'ɡ', 'ᴅ': 'd'}
# 표에 없는 기호의 가장 가까운 칸(대립이 없으면 손실 아님, 있으면 합류 = 손실)
NEAREST = {
    'ʈ': 't', 'ɖ': 'd', 'c': 'tɕ', 'ɟ': 'dʑ', 'q': 'k', 'ɢ': 'ɡ', 'ʡ': 'ʔ',
    'ɸ': 'f', 'ç': 'ɕ', 'ʝ': 'j', 'χ': 'x', 'ʁ': 'ɣ', 'ħ': 'h', 'ʕ': 'h', 'ʜ': 'h', 'ʢ': 'h', 'ɦ': 'h',
    'ʑ': 'ʒ', 'ɧ': 'ʃ', 'ɬ': 'l', 'ɮ': 'l', 'ʋ': 'v', 'ⱱ': 'v', 'ɹ': 'ɾ', 'ɻ': 'ɾ', 'ɽ': 'ɾ', 'ɺ': 'ɾ',
    'ʀ': 'r', 'ʙ': 'r', 'ɳ': 'n', 'ɴ': 'ŋ', 'ɭ': 'l', 'ʟ': 'l', 'ɰ': 'ɣ', 'ʍ': 'w',
    'ɓ': 'b', 'ɗ': 'd', 'ʄ': 'dʑ', 'ɠ': 'ɡ', 'ʛ': 'ɡ', 'kp': 'p', 'ɡb': 'b', 'ŋm': 'm',
    'ȶ': 'tɕ', 'ȡ': 'dʑ', 'ȵ': 'ɲ', 'ȴ': 'ʎ', 'ɫ': 'l', 'ɱ': 'm', 'bv': 'v', 'ps': 's', 'bz': 'z', 'tx': 'x',
    'ʆ': 'ʃ', 'tʆ': 'tʃ', 'ʓ': 'ʒ', 'dʓ': 'dʒ', 'tr': 't', 'dr': 'd', 'ʈr': 't', 'ɖr': 'd', 'tn': 't', 'dn': 'd',
    'tl': 't', 'dl': 'd',
    'pf': 'f', 'kx': 'x', 'tθ': 'θ', 'dð': 'ð', 'tɬ': 'l', 'dɮ': 'l', 'ɖʐ': 'dʐ', 'qχ': 'x',
}
CLICKS = set('ʘǀǃǂǁ‼')
STOP_BASES = {'p', 't', 'k', 'b', 'd', 'ɡ', 'ts', 'dz', 'tʂ', 'tʃ', 'dʒ', 'tɕ', 'dʑ'}
VOICED_OF = {'p': 'b', 't': 'd', 'k': 'ɡ', 'ts': 'dz', 'tʂ': 'dʐ', 'tʃ': 'dʒ', 'tɕ': 'dʑ'}
VOICELESS_OF = {v: k for k, v in VOICED_OF.items()}
IMPLOSIVE = {'ɓ': 'b', 'ɗ': 'd', 'ʄ': 'dʑ', 'ɠ': 'ɡ', 'ʛ': 'ɡ', 'ᶑ': 'd', 'ɠɓ': 'b'}
SONORANT = {'m', 'n', 'ɲ', 'ŋ', 'ɳ', 'ɴ', 'l', 'ɭ', 'ʎ', 'ʟ', 'r', 'ɾ', 'ɹ', 'ɻ', 'ɽ', 'ʀ', 'ɺ', 'j', 'w', 'ɥ', 'ɰ', 'ʋ', 'ʍ'}

IGNORE_MARKS = set('\u032A\u033A\u033B\u0320\u031F\u031A\u0339\u031C\u031D\u031E\u02D1\u0318\u0319\u0329\u030D\u0348\u0349\u0361\u035C\u0308\u033D\u0306\u0303')  # 위치·세부 부호(0303 은 자음에서만 무시)
FORTIS = {'\u02C0', '\u0348', '\u0349'}   # ˀ ͈ ͉
EJECT = '\u02BC'                           # ʼ
PRENASAL_SUP = set('ᵐⁿᵑᶬᶯᶮ')
NASAL_LETTERS = set('mnŋɲɱɳɴ')
OBSTRUENT_FRIC = {'f', 'v', 's', 'z', 'ʃ', 'ʒ', 'x', 'ɣ', 'θ', 'ð', 'β', 'ʂ', 'ʐ', 'ɕ', 'h'}


def parse_cons(seg):
    """자음 분절 → (기본 기호, 꼬리표 집합). 기본 기호는 NOTATION 정규화까지."""
    s = ud.normalize('NFD', seg.replace('|', ''))
    tags = set()
    if s and s[0] in PRENASAL_SUP:
        tags.add('prenasal'); s = s[1:]
    base = []
    for ch in s:
        if ch in FORTIS:
            tags.add('fortis')
        elif ch == EJECT:
            tags.add('ejective')
        elif ch == 'ʰ':
            tags.add('asp')
        elif ch in ('ʱ', '\u0324'):
            tags.add('breathy')
        elif ch in ('\u0325', '\u030A'):
            tags.add('voiceless_mark')
        elif ch == 'ʲ':
            tags.add('pal')
        elif ch == 'ʷ':
            tags.add('lab')
        elif ch == 'ᶣ':
            tags.update({'lab', 'pal'})
        elif ch == 'ɦ' and base:
            tags.add('breathy')
        elif ch == 'ˠ':
            tags.add('vel')
        elif ch == 'ˤ':
            tags.add('phar')
        elif ch == 'ː':
            tags.add('long')
        elif ch == '\u0330':
            tags.add('creaky')
        elif ch == '˞':
            tags.add('rhotic')
        elif ch == '\u0327' and VERSION in X1B and base and base[-1] == 'c':
            base[-1] = 'ç'           # x1b (1): NFD 가 c + 세디유로 나눈 ç 를 제 기호로 되돌린다
        elif ch in IGNORE_MARKS or ud.category(ch).startswith('M') or ch in 'ˑ':
            continue
        elif ch in 'ᵐⁿᵑ':
            tags.add('prenasal')
        else:
            base.append(ch)
    b = ''.join(base)
    # 같은 기호를 겹쳐 쓴 꼴(tt, tsts …) = 긴 자음
    h = len(b) // 2
    if len(b) >= 2 and len(b) % 2 == 0 and b[:h] == b[h:]:
        b = b[:h]; tags.add('long')
    # 앞비음 꼴(mb, nd, ŋɡ, ŋmɡb, ɱv …) — 비음 + 장애음
    if len(b) >= 2 and b[0] in NASAL_LETTERS:
        rest = b[2:] if b.startswith('ŋm') and len(b) > 2 else b[1:]
        r = NOTATION.get(rest, rest)
        if r in VOICED_OF or r in VOICELESS_OF or r in IMPLOSIVE or (r in NEAREST and r not in SONORANT and r not in NASAL_LETTERS) or r in OBSTRUENT_FRIC:
            tags.add('prenasal'); b = r
    b = NOTATION.get(b, b)
    if 'rhotic' in tags and b in ('w', 'ɻ', 'ɹ'):
        b = 'ɻ'
    return b, tags


def stopbase(b):
    """파열 · 파찰 계열로 들어갈 기본 기호(내파음 · 표 밖 파열음은 가장 가까운 칸). (기호, 대체 여부)"""
    if b in IMPLOSIVE:
        return IMPLOSIVE[b], True
    t = NEAREST.get(b)
    if t is not None and (t in VOICED_OF or t in VOICELESS_OF):
        return t, True
    return b, False


def cons_known(b):
    return b in CONS_FORM or b in CONS_EXT or b in NEAREST or b in IMPLOSIVE or b in VOICELESS_OF or any(c in CLICKS for c in b)


def cons_keys(segs):
    """한 자음 목록 → {분절: 열쇠}, 대체 수, 지원 불가 수.

    계열 규칙(조음 위치별): 유기 → ㅍ칸, 유성(무성 부호 붙은 유성 = 연음 포함) → ㅂ칸, 무기 무성 → ㅃ칸.
    유성 계열이 없고 성문화(ˀ ͈ ͉) 계열이 있으면 무기 무성 → ㅂ칸 · 성문화 → ㅃ칸(한국어형).
    방출음은 ㅃ칸으로(무기 무성이 있으면 합류 = 손실). 숨 섞인 유성 → ㅂ칸(합류).
    내파음은 같은 자리 유성이 없으면 유성 칸, 있으면 합류. ʲ ʷ ː 앞비음 → 규칙 열쇠(ㅣ계 · ㅜ계 · 겹침 · 받침).
    ˠ ˤ 성문화 공명음 · 무성 공명음 · 삐걱 → 기본 열쇠(합류하면 손실).
    """
    parsed = {s: parse_cons(s) for s in segs}
    # 위치별 계열 조사
    present = set()
    for s, (b, t) in parsed.items():
        bb, _ = stopbase(b)
        if bb in VOICED_OF or bb in VOICELESS_OF:
            vl = VOICELESS_OF.get(bb, bb)
            if b in IMPLOSIVE:
                lar = 'impl'
            elif 'asp' in t:
                lar = 'asp'
            elif 'ejective' in t:
                lar = 'ej'
            elif 'fortis' in t:
                lar = 'fortis'
            elif 'breathy' in t:
                lar = 'breathy'
            elif bb in VOICELESS_OF or 'voiceless_mark' in t:
                lar = 'voiced'
            else:
                lar = 'plain'
            present.add((vl, lar))
    keys, nsub, nunsup = {}, 0, 0
    allbases = {b for b, t in parsed.values()}
    for s, (b, t) in parsed.items():
        sub = False
        if any(c in CLICKS for c in b):
            keys[s] = ('UNSUP', s); nunsup += 1; continue
        bb, near = stopbase(b)
        if bb in VOICED_OF or bb in VOICELESS_OF:
            sub = near
            vl = VOICELESS_OF.get(bb, bb)
            has = {lar for (v, lar) in present if v == vl}
            if b in IMPLOSIVE:
                slot = 'B'
            elif 'asp' in t:
                slot = 'P'
            elif 'ejective' in t:
                slot = 'PP'; sub = True
            elif 'breathy' in t:
                slot = 'B'; sub = True
            elif 'fortis' in t:
                slot = 'PP'
            elif bb in VOICELESS_OF or 'voiceless_mark' in t:
                slot = 'B'
            else:  # 무기 무성
                slot = 'B' if ('voiced' not in has and 'fortis' in has) else 'PP'
            form = {'B': CONS_FORM.get(VOICED_OF.get(vl, vl), CONS_EXT.get(VOICED_OF.get(vl, vl), '?')),
                    'PP': CONS_FORM.get(vl, CONS_EXT.get(vl, '?')),
                    'P': CONS_FORM.get(vl + 'ʰ', CONS_EXT.get(vl + 'ʰ', CONS_FORM.get(vl, '?') + 'ʰ'))}[slot]
            if form.startswith('?') or form == '?':
                form = 'NEAR:' + vl + slot; sub = True
        else:
            nb = b
            if nb not in CONS_FORM and nb not in CONS_EXT:
                if nb in NEAREST:
                    nb = NOTATION.get(NEAREST[nb], NEAREST[nb]); sub = True
                else:
                    keys[s] = ('UNSUP', s); nunsup += 1; continue
            form = CONS_FORM.get(nb, CONS_EXT.get(nb))
            if form is None:
                form = 'NEAR:' + nb
            # s 계열: 무성 두 갈래(평 · 성문화/유기)는 ㅅ · ㅆ
            if nb == 's':
                kinds = {('fortis' if 'fortis' in tt else 'asp' if 'asp' in tt else 'plain')
                         for (bx, tt) in parsed.values() if NOTATION.get(NEAREST.get(bx, bx), NEAREST.get(bx, bx)) == 's' and not ({'pal', 'lab', 'long', 'prenasal'} & tt)}
                if 'fortis' in kinds and 'plain' in kinds:
                    form = 'ㅆ' if 'fortis' in t else 'ㅅ'
                elif 'asp' in kinds and 'plain' in kinds:
                    form = 'ㅅ' if 'asp' in t else 'ㅆ'
            if nb in SONORANT and ('voiceless_mark' in t or 'fortis' in t or 'creaky' in t or 'breathy' in t):
                sub = True
        # 이차 조음 · 길이 · 앞비음 → 규칙 열쇠
        for tag, mark in (('pal', '+ㅣ'), ('lab', '+ㅜ'), ('long', '+겹'), ('prenasal', '+받침')):
            if tag in t:
                form += mark
        if {'phar', 'vel'} & t:
            sub = sub or 'phar' in t
        keys[s] = ('OK', form)
        nsub += int(sub)
    # 합류 해소 선례
    for (a, c), (target, newform) in RESOLVE.items():
        sa = [s for s, (b, t) in parsed.items() if NOTATION.get(NEAREST.get(b, b), NEAREST.get(b, b)) == a and not t]
        sc = [s for s, (b, t) in parsed.items() if NOTATION.get(NEAREST.get(b, b), NEAREST.get(b, b)) == c and not t]
        if sa and sc:
            for s in sa:
                if keys[s][0] == 'OK' and keys[s][1] == CONS_FORM[a]:
                    keys[s] = ('OK', newform)
    return keys, nsub, nunsup


def cons_cause(seg):
    """x1: 한 자음이 합류 무리에 든 원인. 없으면 None(규약이 제 칸을 준 소리)."""
    b, t = parse_cons(seg)
    if any(c in CLICKS for c in b):
        return 'CLICK'
    if VERSION in X1B:             # x1b (2): 원인을 모두 모은다
        lar = b in IMPLOSIVE or bool(t & {'ejective', 'breathy', 'fortis', 'creaky', 'voiceless_mark'})
        sub = (stopbase(b)[1] and (b not in IMPLOSIVE or b in ('ʛ', 'ᶑ', 'ɠɓ'))) or \
            (b not in CONS_FORM and b not in CONS_EXT and b in NEAREST and b not in IMPLOSIVE) or 'phar' in t
        return '+'.join(k for k, v in (('LAR', lar), ('SUB', sub)) if v) or None
    if b in IMPLOSIVE or t & {'ejective', 'breathy', 'fortis', 'creaky', 'voiceless_mark'}:
        return 'LAR'
    if stopbase(b)[1] or (b not in CONS_FORM and b not in CONS_EXT and b in NEAREST) or 'phar' in t:
        return 'SUB'
    return None


def cons_classes(segs, keys):
    """x1: 합류 무리 · 칸 없는 자음의 유형별 수(무리마다 크기 − 1)."""
    groups = defaultdict(list)
    out = Counter()
    for s, (st, form) in keys.items():
        if st == 'OK' and VERSION in X1B and form.startswith('NEAR:'):
            out['NOGLYPH'] += 1      # x1b (3): 닫힌 목록에 꼴이 없는 칸
        elif st == 'OK':
            groups[form].append(s)
        else:
            out['CLICK' if any(c in CLICKS for c in parse_cons(s)[0]) else 'OTHER'] += 1
    for form, ms in groups.items():
        if len(ms) > 1:
            causes = sorted({k for c in (cons_cause(m) for m in ms) if c for k in c.split('+')})
            out['+'.join(causes) if causes else 'SAME'] += len(ms) - 1
    return dict(out)


def cons_axis(segs):
    keys, nsub, nunsup = cons_keys(segs)
    n = len(segs)
    if n == 0:
        return None
    cnt = Counter(v[1] for v in keys.values() if v[0] == 'OK')
    if VERSION in X1B:             # x1b (3): NEAR:* 는 적힌 대립이 아니라 칸 없음
        nunsup += sum(c for k, c in cnt.items() if k.startswith('NEAR:'))
        cnt = Counter({k: c for k, c in cnt.items() if not k.startswith('NEAR:')})
    merged = sum(c - 1 for c in cnt.values() if c > 1)
    c2 = merged + nunsup
    d = {'n': n, 'C2': c2, 'C1': 1 - c2 / n, 'Csub': nsub, 'merged': merged, 'unsup': nunsup}
    if VERSION in X1:
        d['classes'] = cons_classes(segs, keys)
    return d


# ---------------------------------------------------------------- 2. 모음 ----
V_FORM = {'a': 'ㅏ', 'e': 'ㅔ', 'i': 'ㅣ', 'o': 'ㅗ', 'ɔ': 'ㆍ', 'u': 'ㅜ', 'ɛ': 'ㅐ', 'ɨ': 'ㅡ', 'æ': 'ㅐ',
          'ɐ': 'ㅏ', 'ə': 'ㅓ', 'y': 'ㅟ'}
V_EXT = {'ʌ': 'ㅓ', 'ɯ': 'ㅡ', 'ø': 'ㅚ', 'ɤ': 'ㅓ', 'ɪ': 'ㅣ', 'ʊ': 'ㅜ', 'ʉ': 'ㅜ', 'ɵ': 'ㅗ', 'ɑ': 'ㅏ'}
V_NEAREST = {'ɒ': 'ɔ', 'œ': 'ø', 'ɘ': 'ə', 'ɜ': 'ə', 'ɞ': 'ə', 'ʏ': 'y', 'ɶ': 'æ', 'ä': 'a', 'ɚ': 'ə',
             'ɝ': 'ə', 'ᴀ': 'a', 'ɩ': 'ɪ', 'ɷ': 'ʊ', 'ᵻ': 'ɨ', 'ᵿ': 'ʊ'}
VOWEL_CHARS = set(V_FORM) | set(V_EXT) | set(V_NEAREST)


def parse_vowel(seg):
    s = ud.normalize('NFD', seg.replace('|', ''))
    if '\u032F' in s:
        return None, set()          # 비음절 부호 = 활음 · 이중모음 성분
    base, tags = [], set()
    for ch in s:
        if ch == 'ː':
            tags.add('long')
        elif ch == '\u0303':
            tags.add('nasal')
        elif ch in ('\u0324', '\u0330', 'ˤ', '˞', '\u0318', '\u0319', 'ˀ', 'ʰ', '\u0325'):
            tags.add('phon')
        elif ud.category(ch).startswith('M') or ch in 'ˑ':
            continue
        else:
            base.append(ch)
    b = ''.join(base)
    if len([c for c in b if c in VOWEL_CHARS]) != 1 or len(b) != 1:
        return None, tags            # 이중모음 · 알 수 없는 것
    return b, tags


def vowel_axis(segs):
    quals, flags_long, flags_nasal, flags_phon = defaultdict(set), False, False, False
    lengths = defaultdict(set)
    skipped = 0
    for s in segs:
        b, t = parse_vowel(s)
        if b is None:
            skipped += 1; continue
        quals[b].add(s)
        lengths[b].add('long' in t)
        flags_nasal |= 'nasal' in t
        flags_phon |= 'phon' in t
    if not quals:
        return None
    longonly = {}
    keys, nsub = {}, 0
    for b in quals:
        nb = b
        if nb not in V_FORM and nb not in V_EXT:
            nb = V_NEAREST.get(nb, nb); nsub += 1
        keys[b] = V_FORM.get(nb, V_EXT.get(nb, 'UNSUP:' + b))
    lenpair = False
    if VERSION in V2P:   # 길이로만 갈리는 두 음질 = 길이 대립(VF1), 음질 합류 아님
        groups = defaultdict(list)
        for b, k in keys.items():
            groups[k].append(b)
        for k, bs in list(groups.items()):
            if len(bs) == 2 and not k.startswith('UNSUP'):
                l0, l1 = lengths[bs[0]], lengths[bs[1]]
                if len(l0) == 1 and len(l1) == 1 and l0 != l1:
                    keys[bs[1]] = k + '+길이'; lenpair = True
    cnt = Counter(keys.values())
    merged = sum(c - 1 for k, c in cnt.items() if c > 1 and not k.startswith('UNSUP'))
    unsup = sum(1 for k in keys.values() if k.startswith('UNSUP'))
    n = len(quals)
    return {'nq': n, 'V1': 1 - (merged + unsup) / n, 'Vloss': merged + unsup, 'Vsub': nsub,
            'VF1': any(len(v) == 2 for v in lengths.values()) or lenpair, 'VF2': flags_nasal, 'VF3': flags_phon,
            'VF4': any(q in quals for q in ('y', 'ø', 'ʏ', 'œ')), 'skipped': skipped}


# ---------------------------------------------------------------- 3. 성조 ----
TONE_SOURCES = {'SPA', 'AA', 'PH', 'GM', 'RA', 'UZ'}   # PHOIBLE 원천 가운데 성조를 기록하는 것


def tone_level(n):
    if n is None:
        return None
    return 'T0' if n == 0 else 'T1' if n <= 3 else 'T2' if n <= 6 else 'T3'


# ---------------------------------------------------------------- 4. 음절 ----
CODA_OK = {'p', 't', 'k', 'm', 'n', 'ŋ', 'l'}
GLIDES = {'j', 'w', 'ɥ', 'ɰ'}


def seg_base(seg):
    s = ud.normalize('NFD', seg)
    return ''.join(ch for ch in s if not ud.category(ch).startswith('M') and ch not in 'ʰʲʷˠˤːˑʼˀ˞')


def is_prenasal(seg):
    s = ud.normalize('NFD', seg)
    return bool(s) and (s[0] in PRENASAL_SUP or s[0] in 'ᵐⁿᵑ')


def syllables(segments, labels):
    """Lexibank 의 분절 열 · 운율 문자열 → 음절 목록[(초성들, 핵들, 끝소리들)]. '_' 는 경계."""
    out, on, nu, co = [], [], [], []

    def close():
        nonlocal on, nu, co
        if nu:
            out.append((on, nu, co))
        elif out and (on or co):
            o, n_, c = out[-1]; out[-1] = (o, n_, c + on + co)
        elif on or co:
            out.append((on + co, [], []))
        on, nu, co = [], [], []
    for seg, lab in zip(segments, labels):
        if lab == '_' or seg in ('+', '_'):
            close(); continue
        if lab == 'T':
            continue
        if lab == 'C':
            if nu:
                close()
            on.append(seg)
        elif lab in ('V', 'v'):
            glide = '\u032F' in ud.normalize('NFD', seg)
            if co:
                close()
            if nu and not glide:
                close()
            nu.append(seg)
        elif lab == 'c':
            if not nu:
                on.append(seg)
            else:
                co.append(seg)
    close()
    return out


def cbase(x):
    b = seg_base(x)
    if VERSION in V2P:
        b = NOTATION.get(b, b); b = NEAREST.get(b, b); b = NOTATION.get(b, b)
    return b


def v2_adjust(sy, initials):
    """v2: 초성 끝 활음을 핵으로, 낱말 첫머리에 없는 낱말 가운데 초성 무리는 왼쪽부터 앞 음절 끝소리로."""
    out = []
    for on, nu, co in sy:
        on = list(on); nu = list(nu); co = list(co)
        while on and seg_base(on[-1]) in GLIDES and nu:
            on.pop()            # 활음은 이중모음 글자 안(콰 · 쳐) — 핵의 일부로 보되 덧글자 비용은 아님
        out.append([on, nu, co])
    if initials is not None:
        for i in range(1, len(out)):
            while len(out[i][0]) >= 2 and tuple(seg_base(x) for x in out[i][0]) not in initials:
                out[i - 1][2].append(out[i][0].pop(0))
    return [tuple(x) for x in out]


def form_measures(segments, labels, has_rhotic, initials=None):
    sy = syllables(segments, labels)
    sy = [s for s in sy if s[1]]
    if not sy:
        return None
    if VERSION in V2P:
        sy = v2_adjust(sy, initials)
    n = len(sy); c_ok = g_ok = clus = pren = x_ok = 0
    for on, nu, co in sy:
        offglide = any('\u032F' in ud.normalize('NFD', x) for x in nu[1:]) or \
            any(sum(1 for c in ud.normalize('NFD', x) if c in VOWEL_CHARS) >= 2 for x in nu) or len(nu) > 1
        cods = [cbase(x) for x in co]
        glide_cods = [x for x in cods if x in GLIDES]
        real = [x for x in cods if x not in GLIDES]
        ok_c = len(on) <= 1 and len(real) <= 1 and all(x in CODA_OK for x in real)
        c_ok += ok_c
        x_ok += len(on) <= 2 and len(real) <= 2
        g_ok += ok_c and not glide_cods and not offglide
        clus += len(on) >= 2
        pren += any(is_prenasal(x) for x in on)
    first_on = list(sy[0][0])
    s4a = len(first_on) >= 2
    fb = seg_base(segments[0]) if segments else ''
    s4b = (not s4a) and bool(first_on) and (is_prenasal(first_on[0]) or fb == 'ŋ' or (fb == 'l' and has_rhotic))
    if VERSION in X1:
        return n, c_ok, g_ok, clus, pren, int(s4a), int(s4b), x_ok
    return n, c_ok, g_ok, clus, pren, int(s4a), int(s4b)


def summarize_forms(rows):
    """rows: [(n, c_ok, g_ok, clus, pren, s4a, s4b)] → 비율과 부트스트랩 구간."""
    import numpy as np
    a = np.array(rows, dtype=float)
    if len(a) == 0:
        return None

    def stat(m):
        n = m[:, 0].sum()
        return np.array([m[:, 1].sum() / n, m[:, 2].sum() / n, m[:, 3].sum() / n, m[:, 4].sum() / n,
                         m[:, 5].mean(), m[:, 6].mean()])
    point = stat(a)
    rng = np.random.default_rng(SEED)
    wts = rng.multinomial(len(a), [1 / len(a)] * len(a), size=NBOOT)   # 낱말 단위 재표집 가중치
    tot = wts @ a                      # NBOOT × 7 (합)
    nsum = tot[:, 0]
    boots = np.stack([tot[:, 1] / nsum, tot[:, 2] / nsum, tot[:, 3] / nsum, tot[:, 4] / nsum,
                      tot[:, 5] / len(a), tot[:, 6] / len(a)], 1)
    lo, hi = np.percentile(boots, 2.5, 0), np.percentile(boots, 97.5, 0)
    names = ['S1c', 'S1g', 'S2', 'S3', 'S4a', 'S4b']
    d = {'forms': len(a), 'syll': int(a[:, 0].sum())}
    for i, k in enumerate(names):
        d[k] = round(float(point[i]), 4); d[k + '_ci'] = [round(float(lo[i]), 4), round(float(hi[i]), 4)]
    if a.shape[1] > 7:   # x1: 확장 틀 적합률 S1x(같은 재표집 가중치)
        bx = tot[:, 7] / nsum
        d['S1x'] = round(float(a[:, 7].sum() / a[:, 0].sum()), 4)
        d['S1x_ci'] = [round(float(np.percentile(bx, 2.5)), 4), round(float(np.percentile(bx, 97.5)), 4)]
    return d


# ---------------------------------------------------------------- 5. 찌아찌아어(ABVD · Havens 표 9) ----
CIACIA_CONS = ['p', 't', 'tʃ', 'k', 'ʔ', 'b', 'd̪', 'd', 'dʒ', 'ɡ', 'ᵐp', 'ⁿt', 'ⁿtʃ', 'ᵑk', 'ᵐb', 'ⁿd', 'ᵑɡ',
               'ɓ', 'ɗ', 's', 'h', 'β', 'm', 'n', 'ŋ', 'l', 'r']          # Havens 2024: 44 표 9, 괄호(차용음) f z ʃ j 제외
CIACIA_CONS_LOAN = ['f', 'z', 'ʃ', 'j']
CIACIA_VOW = ['a', 'e', 'i', 'o', 'u']                                       # Havens 2024: 2 「five phonemic vowels」
CIACIA_MAP = {'v': 'β', 'y': 'j', 'χ': 'r', 'ʧ': 'tʃ', 'ʤ': 'dʒ', 'g': 'ɡ'}  # ABVD 와삼부아 철자 → 음소(χ = /r/, Havens 2024: 54 (24))
CIACIA_HOMORGANIC = {'m': {'p', 'b'}, 'n': {'t', 'd', 'tʃ', 'dʒ'}, 'ŋ': {'k', 'ɡ'}}
VOWELS5 = set('aeiou')


def ciacia_forms(abvd_dir):
    rows = [r for r in csv.DictReader(open(os.path.join(abvd_dir, 'forms.csv'), encoding='utf-8')) if r['Language_ID'] == '1524']
    out = []
    for r in rows:
        for word in ud.normalize('NFC', r['Form']).replace('-', ' ').split():
            segs = []
            for ch in word:
                segs.append(CIACIA_MAP.get(ch, ch))
            # 앞비음 합치기(같은 자리 비음 + 파열 · 파찰) — Havens 2024: 2 · 44
            merged, i = [], 0
            while i < len(segs):
                if i + 1 < len(segs) and segs[i] in CIACIA_HOMORGANIC and segs[i + 1] in CIACIA_HOMORGANIC[segs[i]]:
                    merged.append({'m': 'ᵐ', 'n': 'ⁿ', 'ŋ': 'ᵑ'}[segs[i]] + segs[i + 1]); i += 2
                else:
                    merged.append(segs[i]); i += 1
            labs = []
            for j, s in enumerate(merged):
                if s in VOWELS5:
                    labs.append('V')
                else:
                    nxt = merged[j + 1] if j + 1 < len(merged) else None
                    labs.append('C' if nxt in VOWELS5 else 'c')
            out.append((merged, labs))
    return out


# ---------------------------------------------------------------- 6. 자료 읽기 ----
def load_phoible(d):
    P = {r['ID']: r for r in csv.DictReader(open(os.path.join(d, 'phoible', 'parameters.csv'), encoding='utf-8'))}
    inv = {r['ID']: r for r in csv.DictReader(open(os.path.join(d, 'phoible', 'inventories.csv'), encoding='utf-8'))}
    segs = defaultdict(lambda: {'consonant': [], 'vowel': [], 'tone': [], 'lang': None})
    for r in csv.DictReader(open(os.path.join(d, 'phoible', 'values.csv'), encoding='utf-8')):
        if r['Marginal'] == 'true':
            continue
        p = P[r['Parameter_ID']]
        e = segs[r['Inventory_ID']]
        e['lang'] = r['Language_ID']
        if p['SegmentClass'] in e:
            e[p['SegmentClass']].append(p['Name'])
    return inv, segs


def load_glottolog(d):
    L = {}
    for r in csv.DictReader(open(os.path.join(d, 'glottolog', 'languages.csv'), encoding='utf-8')):
        L[r['ID']] = r
    aes = {}
    for r in csv.DictReader(open(os.path.join(d, 'glottolog', 'values.csv'), encoding='utf-8')):
        if r['Parameter_ID'] == 'aes':
            aes[r['Language_ID']] = r['Code_ID'].replace('aes-', '')
    return L, aes


def lang_level(gc, G):
    r = G.get(gc)
    if not r:
        return gc
    if r['Level'] == 'dialect' and r['Language_ID']:
        return r['Language_ID']
    return gc


def load_wals(d):
    langs = {r['ID']: r['Glottocode'] for r in csv.DictReader(open(os.path.join(d, 'wals', 'languages.csv'), encoding='utf-8'))}
    out = defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(d, 'wals', 'values.csv'), encoding='utf-8')):
        if r['Parameter_ID'] in ('12A', '13A', '7A'):
            gc = langs.get(r['Language_ID'])
            if gc:
                out[gc].setdefault(r['Parameter_ID'], r['Value'])
    return out


def iter_lexibank(d, keep):
    z = zipfile.ZipFile(os.path.join(d, 'lexibank', 'forms.csv.zip'))
    f = io.TextIOWrapper(z.open('forms.csv'), encoding='utf-8')
    for r in csv.DictReader(f):
        if r['Language_ID'] in keep:
            yield r['Language_ID'], r['Segments'].split(), [c for c in r['Prosodic_String'] if c != ' ']


# ---------------------------------------------------------------- 7. 명령 ----
def cmd_coverage(a):
    inv, segs = load_phoible(a.data)
    cb, vb = Counter(), Counter()
    for e in segs.values():
        for s in e['consonant']:
            b, t = parse_cons(s)
            if not cons_known(b):
                cb[b] += 1
        for s in e['vowel']:
            b, t = parse_vowel(s)
            if b is not None and b not in V_FORM and b not in V_EXT and b not in V_NEAREST:
                vb[b] += 1
    tot_c = sum(len(e['consonant']) for e in segs.values())
    print('consonant tokens', tot_c, 'unknown-base tokens', sum(cb.values()))
    print('unknown consonant bases (top 60):', cb.most_common(60))
    print('unknown vowel bases:', vb.most_common(30))


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2


def build_table(a):
    G, aes = load_glottolog(a.data)
    inv, segs = load_phoible(a.data)
    W = load_wals(a.data)
    # PHOIBLE → 언어 수준
    per = defaultdict(list)
    clickl = set()
    for iid, e in segs.items():
        gc = lang_level(e['lang'], G)
        src = inv[iid]['Inventory_source_ID']
        c = cons_axis(e['consonant']); v = vowel_axis(e['vowel'])
        nt = int(inv[iid]['count_tones'] or 0) if src in TONE_SOURCES else None
        per[gc].append((iid, src, c, v, nt))
        if any(ch in CLICKS for x in e['consonant'] for ch in x):
            clickl.add(gc)
    table = {}
    for gc, lst in per.items():
        cs = [c for _, _, c, _, _ in lst if c]; vs = [v for _, _, _, v, _ in lst if v]
        tones = [t for *_, t in lst if t is not None]
        row = {'glottocode': gc, 'name': G.get(gc, {}).get('Name', ''), 'n_inv': len(lst),
               'sources': ';'.join(sorted({s for _, s, *_ in lst}))}
        if cs:
            row['C1'] = round(median([c['C1'] for c in cs]), 4); row['C1_range'] = [round(min(c['C1'] for c in cs), 4), round(max(c['C1'] for c in cs), 4)]
            row['C2'] = median([c['C2'] for c in cs]); row['Csub'] = median([c['Csub'] for c in cs])
        if vs:
            row['V1'] = round(median([v['V1'] for v in vs]), 4); row['V1_range'] = [round(min(v['V1'] for v in vs), 4), round(max(v['V1'] for v in vs), 4)]
            for f in ('VF1', 'VF2', 'VF3', 'VF4'):
                row[f] = sum(v[f] for v in vs) / len(vs) >= 0.5
            if VERSION in X1B:     # x1b (4): 목록 하나라도 그 대립을 적으면 자질 있음
                for f in ('VF1', 'VF2', 'VF3'):
                    k = sum(bool(v[f]) for v in vs)
                    row[f] = k > 0; row[f + '_n'] = k
                row['_nvs'] = len(vs)
        if VERSION in X1B:         # x1b (5): 방언 단위 목록
            row['_dialect_merged'] = any(segs[iid]['lang'] != gc for iid, *_ in lst)
            posd = [segs[iid]['lang'] != gc for iid, _, _, _, nt in lst if nt]
            row['_tone_dialect'] = bool(posd) and all(posd)
        row['clicks'] = gc in clickl
        if tones:
            row['tones_min'] = min(tones); row['T'] = tone_level(min(tones)); row['T_src'] = 'phoible'
        if VERSION in X1:
            row['_tones'] = tones
            if cs:
                med = row['C2']
                pick = min(((abs(c['C2'] - med), int(iid), c) for iid, _, c, _, _ in lst if c), key=lambda z: z[:2])[2]
                row['Kc'] = med; row['Kc_range'] = [min(c['C2'] for c in cs), max(c['C2'] for c in cs)]
                row['Kc_types'] = ';'.join(f'{k}:{n}' for k, n in sorted(pick['classes'].items()))
            if vs:
                row['Kv'] = median([v['Vloss'] for v in vs]); row['Kv_range'] = [min(v['Vloss'] for v in vs), max(v['Vloss'] for v in vs)]
        table[gc] = row
    # WALS 성조 · 음절
    for gc, w in W.items():
        gc2 = lang_level(gc, G)
        row = table.setdefault(gc2, {'glottocode': gc2, 'name': G.get(gc2, {}).get('Name', '')})
        if VERSION == 'x1c' and gc2 != gc and ('12A' in w or '13A' in w):
            row['_dialect_merged'] = True     # x1c (1): WALS 값이 방언 단위 자료에서 옴
        if '12A' in w:
            row['W12A'] = w['12A']
        if '7A' in w:
            row['W7A'] = w['7A']
        if '13A' in w:
            row['W13A'] = w['13A']
            if VERSION == 'x1c':
                row['_w13a_dialect'] = gc2 != gc
            if 'T' not in row:
                row['T'] = {'1': 'T0', '2': 'T1', '3': 'T2+'}[w['13A']]; row['T_src'] = 'wals'
    # Lexibank Selexion → 언어 수준(같은 언어에 둘이면 낱말 수가 많은 것)
    langs = [r for r in csv.DictReader(open(os.path.join(a.data, 'lexibank', 'languages.csv'), encoding='utf-8')) if r['Selexion'] == '1']
    pick = {}
    for r in langs:
        gc = lang_level(r['Glottocode'], G)
        if gc not in pick or int(r['FormsWithSounds'] or 0) > int(pick[gc]['FormsWithSounds'] or 0):
            pick[gc] = r
    keep = {r['ID']: gc for gc, r in pick.items()}
    rhotic = defaultdict(bool)
    forms = defaultdict(list)
    for lid, sg, lb in iter_lexibank(a.data, keep):
        forms[lid].append((sg, lb))
        if any(seg_base(x) in ('r', 'ɾ', 'ɹ', 'ɻ', 'ʀ', 'ʁ', 'ɽ') for x in sg):
            rhotic[lid] = True
    for lid, fl in forms.items():
        gc = keep[lid]
        inits = variety_initials(fl) if VERSION in V2P else None
        ms = [m for m in (form_measures(sg, lb, rhotic[lid], inits) for sg, lb in fl) if m]
        s = summarize_forms(ms) if ms else None
        if s:
            row = table.setdefault(gc, {'glottocode': gc, 'name': G.get(gc, {}).get('Name', '')})
            row.update(s); row['lexibank_variety'] = lid
            if VERSION == 'x1c' and pick[gc]['Glottocode'] != gc:
                row['_dialect_merged'] = True     # x1c (1): 쓰인 Lexibank 낱말 목록이 방언 단위
    if VERSION in X1:
        for row in table.values():
            x1_tone(row)
    for gc, row in table.items():
        row['aes'] = aes.get(gc, '')
        row['family'] = G.get(G.get(gc, {}).get('Family_ID', ''), {}).get('Name', '') if G.get(gc, {}).get('Family_ID') else ''
    return table


def x1_tone(row):
    """x1 성조 규칙: 양수인 성조 수가 있으면 그 중앙값, 없으면 WALS 13A, 그것도 없으면 PHOIBLE 0 = T0?(미확정)."""
    tones = row.pop('_tones', [])
    pos = [t for t in tones if t > 0]
    w = row.get('W13A')
    for k in ('T', 'T_src', 'tones_min'):
        row.pop(k, None)
    if pos:
        m = median(pos)
        row['tones_med'] = m; row['tones_range'] = [min(pos), max(pos)]
        row['T'] = 'T1' if m <= 3 else 'T2' if m <= 6 else 'T3'
        if VERSION in ('x1a',) + X1B:   # x1a: 수준은 범위로 — 최솟값과 최댓값의 수준이 다르면 'T1~T2' 꼴
            lv = lambda n: 'T1' if n <= 3 else 'T2' if n <= 6 else 'T3'
            lo, hi = lv(min(pos)), lv(max(pos))
            row['T'] = lo if lo == hi else f'{lo}~{hi}'
        row['T_basis'] = f'phoible+({len(pos)}/{len(tones)})'
        if w == '1':
            row['T_conflict'] = 'phoible>0 vs WALS none'
    elif w in ('2', '3'):
        row['T'] = 'T1' if w == '2' else 'T2+'; row['T_basis'] = 'wals'
        if tones:
            row['T_conflict'] = 'phoible 0 vs WALS tonal'
    elif w == '1':
        row['T'] = 'T0'; row['T_basis'] = 'wals none' + (f' + phoible 0({len(tones)})' if tones else '')
    elif tones:
        row['T'] = 'T0?'; row['T_basis'] = f'phoible 0 only({len(tones)})'


def x1_category(r, theta=0.95):
    """반환 (갈래, 글자층_현행 여부 또는 None)."""
    has_l = 'Kc' in r and 'Kv' in r
    has_s = 'S1c' in r and 'S1x' in r
    has_t = 'T' in r
    letters = None
    if has_l:
        letters = r['Kc'] == 0 and r['Kv'] == 0 and not (r.get('VF1') or r.get('VF2') or r.get('VF3'))
    if not (has_l and has_s and has_t):
        return 'partial', letters
    if r['T'] == 'T2+':
        return 'hold', letters
    if '~' in r['T'] and r['T'].endswith('T3'):   # x1a: 성조 수 갈림이 여섯 칸 경계를 넘음
        return 'hold-range', letters
    if r['S1x'] < theta or r['T'] == 'T3':
        return 'C', letters
    if r['S1c'] < theta:
        return 'B2', letters
    return ('A' if letters else 'B1'), letters


def variety_initials(fl):
    ini = set()
    for sg, lb in fl:
        sy = [s for s in syllables(sg, lb) if s[1]]
        if sy:
            on = list(sy[0][0])
            while on and seg_base(on[-1]) in GLIDES:
                on.pop()
            ini.add(tuple(seg_base(x) for x in on))
    return ini


def ciacia_row(a, rhotic=True):
    fl = ciacia_forms(os.path.join(a.data, 'abvd'))
    inits = variety_initials(fl) if VERSION in V2P else None
    ms = [m for m in (form_measures(sg, lb, rhotic, inits) for sg, lb in fl) if m]
    row = {'glottocode': 'ciac1237', 'name': 'Cia-Cia (수기: Havens 표 9 + ABVD 와삼부아)', 'handcoded': True}
    row.update(summarize_forms(ms))
    c = cons_axis(CIACIA_CONS); v = vowel_axis(CIACIA_VOW)
    row.update({'C1': round(c['C1'], 4), 'C2': c['C2'], 'Csub': c['Csub'], 'V1': round(v['V1'], 4),
                'VF1': v['VF1'], 'VF2': v['VF2'], 'VF3': v['VF3'], 'VF4': v['VF4'], 'T': 'T0', 'T_src': 'Havens 2024 (강세, 성조 없음)'})
    cl = cons_axis(CIACIA_CONS + CIACIA_CONS_LOAN)
    row['C1_withloans'] = round(cl['C1'], 4); row['C2_withloans'] = cl['C2']
    if VERSION in X1:
        row.update({'Kc': c['C2'], 'Kc_range': [c['C2'], c['C2']], 'Kc_types': ';'.join(f'{k}:{n}' for k, n in sorted(c['classes'].items())),
                    'Kv': v['Vloss'], 'Kv_range': [v['Vloss'], v['Vloss']], 'T_basis': 'Havens 2024 (stress, no tone)', 'n_inv': 1, 'sources': 'Havens2024'})
        row.pop('T_src', None)
        if VERSION == 'x1c':   # x1c (2 · 3): 원전에 「성조 없음」 문장이 없다 — 추론임을 밝힌다
            row['T'] = 'T0?'; row['T_basis'] = 'Havens 2024: stress described, tone not mentioned (inferred)'
            row['_composite'] = True
    return row


def quantile(vals, q):
    v = sorted(vals)
    if not v:
        return None
    k = (len(v) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


X1_COLS = ['glottocode', 'name', 'family', 'category', 'letters_ok', 'Kc', 'Kc_range', 'Kc_types', 'Kv', 'Kv_range', 'vowel_features',
           'VF4', 'S1c', 'S1c_ci', 'S1x', 'S1x_ci', 'S2', 'S3', 'S4a', 'S4b', 'forms', 'syll', 'T', 'tones_med', 'tones_range',
           'T_basis', 'T_conflict', 'W13A', 'W12A', 'aes', 'n_inv', 'sources', 'lexibank_variety', 'flags']


X1B_NAMES = {'A': 'current', 'B1': 'letters', 'B2': 'syllable', 'C': 'outside', 'hold': 'tone-unknown',
             'hold-range': 'tone-range', 'partial': 'partial'}


def cmd_explore(a, table):
    """x1 사후 탐색판: 층별 기술과 갈래. 분위수 문턱 없음."""
    for r in table.values():
        r['category'], lo = x1_category(r)
        if lo is not None:
            r['letters_ok'] = lo
        if 'VF1' in r:
            r['vowel_features'] = ';'.join(n for f, n in (('VF1', 'length'), ('VF2', 'nasal'), ('VF3', 'phonation')) if r.get(f))
            if VERSION in X1B and '_nvs' in r:
                r['vowel_features'] = ';'.join(f"{n}({r[f + '_n']}/{r['_nvs']})" for f, n in (('VF1', 'length'), ('VF2', 'nasal'), ('VF3', 'phonation')) if r.get(f))
        fl = []
        if VERSION in X1B:
            r['category'] = X1B_NAMES[r['category']]
            if r.get('T') == 'T0?':
                fl.append('tone-unconfirmed')
            if (r.get('_tone_dialect') and str(r.get('T_basis', '')).startswith('phoible+')) or                     (VERSION == 'x1c' and r.get('T_basis') == 'wals' and r.get('_w13a_dialect')):
                fl.append('tone-from-dialects')
            if r.get('_dialect_merged'):
                fl.append('dialect-merged')
        if r.get('n_inv') == 1:
            fl.append('single-inventory')
        if 'forms' in r and r['forms'] < 100:
            fl.append('small-sample')
        if r.get('handcoded'):
            fl.append('handcoded')
        if r.get('_composite'):
            fl.append('composite-varieties')
        r['flags'] = ';'.join(fl)
    with open(os.path.join(a.out, 'explore-axes.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(X1_COLS)
        for g in sorted(table):
            r = table[g]
            w.writerow([json.dumps(r[c], ensure_ascii=False) if isinstance(r.get(c), (list, bool)) else r.get(c, '') for c in X1_COLS])
    nm = (lambda c: X1B_NAMES[c]) if VERSION in X1B else (lambda c: c)
    sens = {str(th): dict(Counter(nm(x1_category(r, th)[0]) for r in table.values())) for th in (0.90, 0.95, 0.99)}
    ca, cb = pick_controls(table)
    keep = lambda r: {k: r.get(k) for k in X1_COLS if k in r} if r else None
    summ = {'n_rows': len(table), 'categories_by_theta': sens,
            'layers': {'letters': sum('Kc' in r and 'Kv' in r for r in table.values()), 'syllable': sum('S1x' in r for r in table.values()),
                       'tone': sum('T' in r for r in table.values())},
            'tone_levels': dict(Counter(r.get('T', '') for r in table.values())),
            'bench_rows': {k: keep(table.get(v)) for k, v in BENCH.items()},
            'controls': [ca, cb], 'control_rows': {c: keep(table.get(c)) for c in (ca, cb) if c}}
    json.dump(summ, open(os.path.join(a.out, 'explore-summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('rows', len(table), 'categories', sens['0.95'])


def cmd_run(a):
    os.makedirs(a.out, exist_ok=True)
    table = build_table(a)
    table['ciac1237'] = ciacia_row(a)
    if VERSION in X1:
        return cmd_explore(a, table)
    data_rows = [r for g, r in table.items() if not r.get('handcoded')]
    thr = {k: quantile([r[k] for r in data_rows if k in r], 2 / 3) for k in ('S1c', 'C1', 'V1', 'S1g')}
    thr10 = {k: quantile([r[k] for r in data_rows if k in r], 0.9) for k in ('S1c', 'C1', 'V1')}
    for r in table.values():
        need = ('S1c', 'C1', 'V1', 'T')
        if not all(k in r for k in need):
            r['status'] = '판정 불가(' + ','.join(k for k in need if k not in r) + ')'
        elif r['T'] == 'T2+':
            r['status'] = '판정 보류(성조 WALS 「복잡」)'
        else:
            ok = r['S1c'] >= thr['S1c'] and r['C1'] >= thr['C1'] and r['V1'] >= thr['V1'] and r['T'] in ('T0', 'T1', 'T2') and r['C2'] <= 2
            r['status'] = '목록' if ok else '목록 밖'
    bench = evaluate(table, thr, thr10)
    json.dump(bench, open(os.path.join(a.out, 'bench.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('predictions hit', bench['hits'], '/ 14 · gate', bench['gate'])
    json.dump({'thresholds_2_3': thr, 'thresholds_0_9': thr10, 'n_languages': len(table)},
              open(os.path.join(a.out, 'thresholds.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cols = ['glottocode', 'name', 'family', 'status', 'S1c', 'S1c_ci', 'S1g', 'S1g_ci', 'S2', 'S3', 'S4a', 'S4b', 'forms', 'syll',
            'C1', 'C1_range', 'C2', 'Csub', 'V1', 'V1_range', 'VF1', 'VF2', 'VF3', 'VF4', 'T', 'T_src', 'tones_min',
            'W12A', 'W13A', 'W7A', 'aes', 'n_inv', 'sources', 'lexibank_variety', 'C1_withloans', 'C2_withloans']
    with open(os.path.join(a.out, 'fit-axes.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(cols)
        for g in sorted(table):
            r = table[g]
            w.writerow([json.dumps(r[c], ensure_ascii=False) if isinstance(r.get(c), (list, bool)) else r.get(c, '') for c in cols])
    print('languages', len(table), 'thresholds', thr)


BENCH = {'cia': 'ciac1237', 'vie': 'viet1252', 'cmn': 'mand1415', 'spa': 'stan1288', 'rus': 'russ1263', 'kor': 'kore1280'}


def pick_controls(table):
    """부정 통제: (가) WALS 12A 복잡 + 7A 성문화 자음 있음, (나) 흡착음 — 각각 S1c · C1 · V1 이 있는 언어 가운데 Glottocode 순 첫째."""
    full = [g for g, r in sorted(table.items()) if all(k in r for k in ('S1c', 'C1', 'V1')) and not r.get('handcoded') and g not in BENCH.values()]
    a = next((g for g in full if table[g].get('W12A') == '3' and table[g].get('W7A') not in (None, '', '1')), None)
    b = next((g for g in full if table[g].get('clicks')), None)
    return a, b


def evaluate(table, thr, thr10):
    R = {k: table.get(v, {}) for k, v in BENCH.items()}
    five = ['cia', 'vie', 'cmn', 'spa', 'rus']
    g = lambda k, f: R[k].get(f)
    P = {}
    try:
        P['P1'] = g('cia', 'S1c') >= thr['S1c'] and g('cia', 'S1g') >= thr['S1g']
        P['P2'] = all(g('cia', 'S4b') > g(k, 'S4b') for k in five if k != 'cia')
        P['P3'] = g('cia', 'C2') >= 2
        P['P4'] = g('cia', 'status') == '목록'
        gap = {k: g(k, 'S1c') - g(k, 'S1g') for k in five}
        P['P5'] = g('vie', 'S1c') >= thr['S1c'] and g('vie', 'S2') <= 0.02 and all(gap['vie'] > gap[k] for k in five if k != 'vie')
        P['P6'] = bool(g('vie', 'VF1'))
        P['P7'] = g('vie', 'T') == 'T2'
        P['P8'] = g('cmn', 'T') == 'T2'
        P['P9'] = g('cmn', 'C2') == 0
        P['P10'] = g('vie', 'S1c') > g('spa', 'S1c') and g('cmn', 'S1c') > g('spa', 'S1c') > g('rus', 'S1c')
        P['P11'] = all(g('rus', 'S1c') < g(k, 'S1c') and g('rus', 'S2') > g(k, 'S2') for k in five if k != 'rus')
        P['P12'] = g('rus', 'C2') == 0
        P['P13'] = all(g('kor', f) >= thr10[f] for f in ('S1c', 'C1', 'V1')) and g('kor', 'T') == 'T0'
    except TypeError as e:
        P['error'] = str(e)
    ca, cb = pick_controls(table)
    P['P14'] = all(c and table[c].get('status') != '목록' for c in (ca, cb))
    hits = sum(1 for k, v in P.items() if k.startswith('P') and v is True)
    return {'predictions': P, 'hits': hits, 'gate': hits >= 12 and P.get('P13') is True,
            'controls': [ca, cb], 'bench_rows': {k: table.get(v) for k, v in BENCH.items()},
            'control_rows': {c: table.get(c) for c in (ca, cb) if c}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['coverage', 'run'])
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', default='.')
    ap.add_argument('--version', default='v1', choices=['v1', 'v2', 'x1', 'x1a', 'x1b', 'x1c'])
    a = ap.parse_args()
    global VERSION
    VERSION = a.version
    sys.stdout.reconfigure(encoding='utf-8')
    {'coverage': cmd_coverage, 'run': cmd_run}[a.cmd](a)


if __name__ == '__main__':
    main()
