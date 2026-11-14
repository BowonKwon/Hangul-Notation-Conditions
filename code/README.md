# Computation tool · 계산 도구

`hangul_fit.py` — standard library + numpy. MIT (see `LICENSE`).

```
python hangul_fit.py run --data DATA --out OUT --version x1c
```

`DATA` holds the source datasets as described in `../data/SOURCES.md`. `--version x1c` builds exploratory edition 1.
The tables of letter slots inside the tool are the common rows of the mapping table published by the Sejong notation site
(https://bowonkwon.github.io/Legal-Language-Handbooks/sejong/, `data/mapping.csv`, CC BY 4.0), extended by the processing
rules described on this site's Method page.

`DATA` 는 `../data/SOURCES.md` 대로 원자료를 둔 폴더다. `--version x1c` 가 탐색판 1 이다. 도구 안의 글자 칸 표는 세종 표기 사이트가
공개한 대응표(`data/mapping.csv`, CC BY 4.0)의 공통 행에, 이 사이트 「방법」 면의 처리 규칙을 더한 것이다.

Comments in the code are in Korean. 코드의 주석은 한국어다.
