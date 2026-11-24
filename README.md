# 한글로 적으면 무엇이 남고 무엇이 빠지나 · What Hangul writes and what it misses

**사이트 · Site:** https://bowonkwon.github.io/Hangul-Notation-Conditions/ ([한국어](https://bowonkwon.github.io/Hangul-Notation-Conditions/ko/) · [English](https://bowonkwon.github.io/Hangul-Notation-Conditions/en/))

3,886개 언어 단위의 형식 조건표 — 탐색판 1 (2026. 11.) · A formal-condition table of 3,886 language units — exploratory edition 1 (November 2026)

사이트 판 1.0.2 (2026-11-24). 표는 탐색판 1 그대로다. · Site version 1.0.2 (2026-11-24); the table is that of exploratory edition 1.

공개 음운 자료(PHOIBLE · WALS · Lexibank · Glottolog · ABVD)를 가지고, 한 언어의 소리를 [세종 표기 판 3.2](https://bowonkwon.github.io/Legal-Language-Handbooks/sejong/)의 규약으로 적을 때, 음운 목록에 적힌 소리들이 이 분류에서 같은 글자 칸으로 합쳐지는 자리와 글자가 없는 자리를 언어 단위마다 센 표다. 한 행은 원자료가 코드 하나로 묶은 단위이고, 3,886행 가운데 3,843행이 Glottolog 가 언어로 분류한 단위다(사이트의 「방법」 면).

A table that counts, unit by unit and from public phonological data (PHOIBLE, WALS, Lexibank, Glottolog, ABVD), where the sounds listed in phoneme inventories merge into a shared letter slot in this classification and where there is no letter when a language is written with the notation of [Sejong notation, edition 3.2](https://bowonkwon.github.io/Legal-Language-Handbooks/sejong/). A row is a unit that the source data file under one code; 3,843 of the 3,886 rows are units that Glottolog classifies as languages (see the Method page).

## 먼저 읽어 주기 바라는 점 · Please read first

- 한글을 쓰면 좋다는 권고가 아니다. 글자와 소리의 형식적 대응만 셌다. · It is not a recommendation to write any language in Hangul; only the formal correspondence between letters and sounds is counted.
- 추상 조건 검사다. 적은 글자열을 되읽어 본 검사가 아니다. · It is an abstract condition check, not a test of reading written strings back.
- 미리 적어 둔 검정을 넘지 못한 뒤에 만든 탐색판이다. 경과는 사이트의 「경과」 면에 있다. · It is an exploratory edition made after a test written down in advance had failed; see the Record page.
- 성조가 「없다」고 나오는 값의 절반 이상은 근거가 약하다(`T0?`). · For more than half of the "no tone" values the evidence is weak (`T0?`).
- 언어들의 순위를 매기지 않는다. · It does not rank languages.

## 폴더 · Layout

- `docs/` 사이트(GitHub Pages) · the site
- `data/` 표 `hangul-conditions-ed1.tsv`(3,886행 · 34열), `summary.json`, 지도의 좌표 표 `map-points.tsv`, 열 설명 `columns.md`, 원자료의 판과 해시 `SOURCES.md` · the table, a summary, the coordinates behind the map, the column guide, and the versions and hashes of the source data
- `code/` 계산 도구 · the computation tool

## 다시 만들기 · Reproducing

`data/SOURCES.md` 의 판으로 원자료를 받은 뒤 · After obtaining the source data at the versions in `data/SOURCES.md`:

```
pip install numpy
python code/hangul_fit.py run --data DATA --out OUT --version x1c
```

`OUT/explore-axes.tsv` 는 `data/hangul-conditions-ed1.tsv` 와 바이트 단위로 같다. · `OUT/explore-axes.tsv` is byte-identical to `data/hangul-conditions-ed1.tsv`.

## 인용 · Citation

What Hangul writes and what it misses: a formal-condition table of 3,886 language units, exploratory edition 1 (2026), https://bowonkwon.github.io/Hangul-Notation-Conditions/

## 라이선스 · License

글 CC BY-NC 4.0 · 표 CC BY 4.0 · 도구 MIT. 자세한 것은 `LICENSE.md`. · Text CC BY-NC 4.0; table CC BY 4.0; tool MIT. See `LICENSE.md`.

생성형 AI와 함께 만들었다. 틀린 값을 찾으면 [Issues](https://github.com/BowonKwon/Hangul-Notation-Conditions/issues)로 알려 주시기 바란다. 엮은이 개인의 작업이며 소속 기관과 관계가 없다.
Compiled with generative AI. Please report errors in [Issues](https://github.com/BowonKwon/Hangul-Notation-Conditions/issues). This is the compiler's personal work and is unrelated to any institution.

[모든 공개 자료 · All public materials](https://bowonkwon.github.io/)
