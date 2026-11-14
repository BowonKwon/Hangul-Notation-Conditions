# Source data · 원자료

The source data are not redistributed here. Obtain them at the versions below and place the files in one folder with the
subfolders shown; pass that folder to the tool as `--data`.
원자료는 이 저장소에 싣지 않는다. 아래 판으로 받아 한 폴더 아래에 표의 하위 폴더 이름으로 두고, 그 폴더를 도구의 `--data` 로 준다.

All five are CC BY 4.0. 다섯 모두 CC BY 4.0.

| Subfolder | Dataset | Version | Files used · SHA-256 |
|---|---|---|---|
| `phoible/` | PHOIBLE as CLDF — https://github.com/cldf-datasets/phoible (`cldf/`) | commit `5c477f1934f57b3c1a16168fadc08e83dbc03362` (2025-04-10) | `inventories.csv` `998cc5b434a44c898fbe0abf0b217f061da7f7b42c7bd0c007a0690f4ac7ccb2` · `parameters.csv` `dfb9564d9272bcdddbde29f5fe2f2188aa2a132d16d9f728f6401baf41bcc620` · `values.csv` `5557f4fcf52aaebe32c18cc2569b8d9daa75636ff8ddfa188c746db2c57855c3` |
| `wals/` | WALS as CLDF — https://github.com/cldf-datasets/wals (`cldf/`) | tag `v2020.6` | `languages.csv` `10e0742f158dadd4ef9484797ef7606a337306ee49a110a58c8e658826d3290e` · `values.csv` `2d672f80dbe8cf1839061af0301650bde60c326bbb486835c93ab7304b5b06cd` |
| `lexibank/` | Lexibank Analysed — https://github.com/lexibank/lexibank-analysed (`cldf/`) | tag `v2.2` | `languages.csv` `324471478232de35c6d2840abd1e56fa602ea3fa5038b7da9e9e272678b19e42` · `forms.csv.zip` `ec63a2ac7ea5da96c4b7ff3b1b75b0c5b5f181de9c153843d747b8b9ba2522df` |
| `glottolog/` | Glottolog as CLDF — https://github.com/glottolog/glottolog-cldf (`cldf/`) | tag `v5.4` | `languages.csv` `ecadbfd440f3d0c28182f676b7e49c6e38fd3d40774c7ae3d90bf28ca137fe90` · `values.csv` `f7f39813ed2ff80f71172a1f962b7ac19fb5306ac8aea55af168ad1219e330d7` |
| `abvd/` | ABVD as CLDF — https://github.com/lexibank/abvd (`cldf/`) | tag `v0.3` | `forms.csv` `d9fd41f1fef9d7dd5e68a388b94b623d369a3e465033c389ee1724d052080dcd` |

Citations are on the site's Sources page. The READMEs of WALS, Lexibank, Glottolog and ABVD ask that the release used also be cited by its DOI; this edition does not give those DOIs, so please check the release page of each repository.
인용은 사이트의 「출처」 면에 있다. WALS · Lexibank · Glottolog · ABVD 의 안내문은 쓴 판의 DOI 로도 인용해 달라고 요청한다. 이 판에는 그 DOI 를 싣지 않았으니 각 저장소의 릴리스 면에서 확인해 주기 바란다.

The versions above record how the files were obtained; that the files received are identical to those releases cannot be proven from this repository alone. The files actually used are fixed by the hashes.
위의 판은 받은 경로의 기록이다. 받은 파일이 그 판과 같다는 것은 이 저장소의 자료만으로 증명되지 않는다. 실제로 쓴 파일은 해시로 고정했다.

## This edition · 이 판

| File | SHA-256 |
|---|---|
| `hangul-conditions-ed1.tsv` | `3e50c67be1d41840df289564f8f987ef064c5d622a71d6443625519135d9f61d` |
| `summary.json` | `c94deab0e8aa245e10b26f392774c84b2fafda7d228bba4b0a0e61e855a9bf52` |
| `code/hangul_fit.py` | `86a1cf089484acc932640e7c147cf0b57c5d05d93fa6830cd65338c827176a66` |

`python code/hangul_fit.py run --data DATA --out OUT --version x1c` writes `explore-axes.tsv` and `explore-summary.json`,
byte-identical to the two data files above. 위 명령이 만드는 두 파일은 위의 두 데이터 파일과 바이트 단위로 같다.
