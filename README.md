# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/zenoonne/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/zenoonne/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

An illustrated newspaper front page that sums up **Monday 23 November 2026**: a masthead carrying the date huge, a numbers strip giving the 33-story count per region (Asia 11 · Europe 7 · Americas 6 · Africa 4 · Middle East 1 · Oceania 1 · Space 1 · Markets/Money 2) plus six verified statistics from the day, a "HOW SURE ARE WE?" line, **three big illustrated features** each with a detailed code-drawn scene and a confidence tag, **ten medium illustrated stories** (each with a scene, a location label, a coloured region tag, a bold headline, a sourced one-line subline and a confidence tag), and the remaining **twenty stories** in a compact numbered list. A **world map** ("WHERE IT HAPPENED") carries numbered pins matching the thirteen features, a **MARKETS & MONEY** box holds the day's verified market-moving numbers, a **THE DAY BY HOURS** timeline lists five events with their UTC times, and a **DATE CHECK** box names the stories left off the page because they actually happened on other days. Every illustrated story is tagged **REPORTED**, **FORECAST** or **CLAIM** so the page is honest about what is asserted versus asserted-by-someone. Every one of the 33 items is an *event of that day* (not merely a 23 November report), verified against a primary outlet and recorded with its event date in `SOURCES.md` (the AI-bubble selloff, the boy pulled from the rubble, the US spy chief, the DR Congo Ebola fighting, the Poland assassination claim, the Lebanon demolitions, the Indonesia factory fire, the Lowy Asia Power Index, the NHS AI breast-cancer trial, the California suit against OpenAI, and more). The renderer (`render.py`, Python + Pillow, with `worldmap.py` for the simplified continent polygons) draws the whole page offline and deterministically from embedded data — no external images and no network — and the graded entrypoint (`main.ts`) copies the rendered `entry.png` to the output directory.

## Run it

```sh
node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
