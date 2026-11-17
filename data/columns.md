# Column guide · 열 설명

`hangul-conditions-ed1.tsv` — 3,886 rows, 34 columns, tab-separated, UTF-8.

## English

| Column | Meaning |
|---|---|
| `glottocode`, `name`, `family` | Glottolog code, name and top-level family (empty for languages with no higher family) |
| `category` | `current`, `letters`, `syllable`, `outside`, `tone-unknown`, `tone-range`, `partial` (Method, section 5) |
| `letters_ok` | Whether the letter-layer condition is met (median K_c and K_v of 0 and no vowel feature) |
| `Kc`, `Kc_range` | Number of consonants that merge into a shared slot or have no slot — median across inventories and [minimum, maximum] |
| `Kc_types` | The causes: `LAR` laryngeal series, `SUB` sent to the nearest slot, `SAME` two sounds the notation gives one shape, `CLICK` clicks, `NOGLYPH` no shape, `OTHER`. These are from the single inventory closest to the median, so they need not add up to `Kc` |
| `Kv`, `Kv_range` | Number of vowel qualities that merge or have no letter — median and [minimum, maximum] |
| `vowel_features` | Vowel contrasts the notation has no device for: `length`, `nasal`, `phonation`. In parentheses: inventories recording the feature / inventories whose vowels were counted |
| `VF4` | Whether at least half of the inventories have front rounded vowels (the y and ø series), which the notation writes with ㅟ and ㅚ |
| `S1c`, `S1c_ci` | Share of syllables that fit the current syllable frame, with a 95% interval |
| `S1x`, `S1x_ci` | Share of syllables that fit the widened frame (two onset consonants, two coda consonants, any coda), with a 95% interval |
| `S2` | Share of syllables with two or more onset consonants |
| `S3` | Share of syllables whose onset is a prenasalized consonant |
| `S4a` | Share of words whose first syllable has two or more onset consonants |
| `S4b` | Share of all words that do not begin with an onset cluster and whose first sound is a prenasalized consonant, ŋ, or l (where the wordlist also has an r-type sound) |
| `forms`, `syll` | Number of words and of syllables |
| `T` | Tone level: `T0` none, `T0?` unconfirmed (no source records tone), `T1` 1–3, `T2` 4–6, `T3` 7 or more, `T2+` complex with unknown count; `T1~T2` and the like are ranges where sources differ |
| `tones_med`, `tones_range` | Median and [minimum, maximum] of the positive tone counts |
| `T_basis` | Basis of the tone value. `phoible+(2/4)` means two of four inventories from tone-recording sources have a positive count; `wals` and `wals none` refer to WALS 13A; `phoible 0 only` means only inventories with a count of 0 |
| `T_conflict` | Cases where PHOIBLE and WALS disagree |
| `W13A`, `W12A` | Raw WALS values for 13A (tone: 1 none, 2 simple, 3 complex) and 12A (syllable structure: 1 simple, 2 moderately complex, 3 complex) |
| `aes` | Glottolog's Agglomerated Endangerment Status |
| `n_inv`, `sources` | Number of PHOIBLE inventories and the abbreviations of their sources (for the Cia-Cia row, the one written source is entered as 1) |
| `lexibank_variety` | Identifier of the Lexibank wordlist used |
| `flags` | Flags (Method, section 6) |

## 한국어

| 열 | 뜻 |
|---|---|
| `glottocode` · `name` · `family` | Glottolog 의 코드 · 이름 · 최상위 계통(비어 있으면 상위 계통이 없는 언어) |
| `category` | 갈래. `current` · `letters` · `syllable` · `outside` · `tone-unknown` · `tone-range` · `partial`(방법 5) |
| `letters_ok` | 글자 층의 조건을 충족하는가(K_c · K_v 의 중앙값이 0 이고 모음 자질이 없음) |
| `Kc` · `Kc_range` | 자음에서 같은 칸으로 합쳐지거나 칸이 없는 소리의 수 — 목록들의 중앙값과 [최소, 최대] |
| `Kc_types` | 그 까닭. `LAR` 후두 계열 · `SUB` 가까운 칸으로 보냄 · `SAME` 규약이 한 꼴에 둔 두 소리 · `CLICK` 흡착음 · `NOGLYPH` 꼴 없음 · `OTHER`. 중앙값에 가장 가까운 목록 하나의 것이라 `Kc` 와 합이 다를 수 있다 |
| `Kv` · `Kv_range` | 모음 음질에서 합쳐지거나 글자가 없는 것의 수 — 중앙값과 [최소, 최대] |
| `vowel_features` | 규약에 장치가 없는 모음 대립. `length` 길이 · `nasal` 비음 · `phonation` 발성. 괄호 안은 「그 자질을 적은 목록 수 / 모음을 센 목록 수」 |
| `VF4` | 전설 원순 모음(y · ø 계)이 음운 목록의 절반 이상에 있는가. 규약은 ㅟ · ㅚ 로 적는다 |
| `S1c` · `S1c_ci` | 현행 음절 틀에 드는 음절의 비율과 95% 구간 |
| `S1x` · `S1x_ci` | 넓힌 틀(초성 둘 · 끝소리 둘, 끝소리 종류 제한 없음)에 드는 음절의 비율과 95% 구간 |
| `S2` | 초성 자음이 둘 이상인 음절의 비율 |
| `S3` | 앞비음 자음이 초성인 음절의 비율 |
| `S4a` | 첫 음절의 초성 자음이 둘 이상인 낱말의 비율 |
| `S4b` | 전체 낱말 가운데, 초성 연쇄로 시작하지 않으면서 첫소리가 앞비음 자음 · ŋ · l(낱말 목록에 r 류 소리도 있을 때)인 낱말의 비율 |
| `forms` · `syll` | 낱말 수 · 음절 수 |
| `T` | 성조 수준. `T0` 없음 · `T0?` 미확정(성조를 적은 자료가 없음) · `T1` 1~3 · `T2` 4~6 · `T3` 7 이상 · `T2+` 복잡(수 모름) · `T1~T2` 따위는 자료마다 다른 범위 |
| `tones_med` · `tones_range` | 성조 수가 양수인 목록들의 중앙값과 [최소, 최대] |
| `T_basis` | 성조 값의 근거. `phoible+(2/4)` 는 성조를 적는 원천의 목록 넷 가운데 둘이 양수라는 뜻. `wals` · `wals none` 은 WALS 13A. `phoible 0 only` 는 0 으로 적은 목록뿐이라는 뜻 |
| `T_conflict` | PHOIBLE 과 WALS 가 어긋나는 경우 |
| `W13A` · `W12A` | WALS 13A(성조: 1 없음 · 2 단순 · 3 복잡) · 12A(음절 구조: 1 단순 · 2 중간 · 3 복잡) 원값 |
| `aes` | Glottolog 의 위험도(Agglomerated Endangerment Status) |
| `n_inv` · `sources` | PHOIBLE 목록 수와 그 원천의 약호(찌아찌아어 행은 문헌 하나를 1 로 적었다) |
| `lexibank_variety` | 쓴 Lexibank 낱말 목록의 식별자 |
| `flags` | 표시(방법 6) |

The name of the Cia-Cia row carries a Korean note meaning "hand-entered: Havens Table 9 + ABVD Wasambua".
찌아찌아어 행의 이름에는 「수기: Havens 표 9 + ABVD 와삼부아」라는 주기가 붙어 있다.

The `l1` row comes from a PHOIBLE inventory whose code is not in Glottolog; its name and family are empty. 42 rows are codes that Glottolog classifies as groups of languages.
`l1` 행은 PHOIBLE 목록 하나의 코드가 Glottolog 에 없어 이름과 계통이 비어 있다. 42행은 Glottolog 가 여러 언어의 묶음으로 분류한 코드다.

## `map-points.tsv`

The coordinates behind the map on the Results page: one line per row of the table, in the same order (3,886 lines, 6 columns). 결과 면 지도의 좌표 — 표의 행마다 한 줄, 같은 순서(3,886줄 · 6열).

| Column · 열 | Meaning · 뜻 |
|---|---|
| `glottocode` · `name` | As in the table · 표와 같다 |
| `latitude` · `longitude` | Glottolog `languages.csv` values, copied unchanged; empty if Glottolog has none · Glottolog 의 값 그대로, 없으면 빈칸 |
| `layers` | `all3` = data in all three layers (dark dot) · 세 층 모두(짙은 점); `partial` = some layers only (light dot) · 일부 층만(옅은 점) |
| `drawn` | `yes` = drawn · 그렸다; `no-coordinates` = Glottolog has no coordinates · 좌표 없음; `not-in-glottolog` = code not in Glottolog · Glottolog 에 없는 코드; `outside-latitude-range` = outside the map (78°N–58°S) · 지도 범위 밖 |
