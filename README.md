# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/zenoonne/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/zenoonne/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A newspaper front page that sums up **Monday 23 November 2026** — the full day, not just the morning. It carries the date huge in the masthead, a numbers strip with the 33-story count per region (Asia 3 · Europe 11 · Americas 8 · Middle East 5 · Africa 3 · Oceania 1 · World 1 · Markets 1) plus five verified statistics from the day, **three big illustrated features** each with a detailed code-drawn scene and a confidence tag, **ten medium illustrated stories** (scene, location label, coloured region tag, bold headline, sourced subline and confidence tag), and the remaining **twenty stories** in a compact numbered list. A **world map** ("WHERE IT HAPPENED") pins the thirteen features, a **MARKETS & MONEY** box holds the day's verified market-moving numbers, a **THE DAY BY HOURS** timeline lists six timed events in UTC, and a **DATE CHECK** box names the eight notable stories left off the page because they actually happened on other days. Every illustrated story is tagged **REPORTED**, **FORECAST** or **CLAIM** so the page is honest about what is asserted versus asserted-by-someone. Every one of the 33 items is an *event of that day* (not merely a 23 November report), checked against a primary outlet and recorded with its event date in `SOURCES.md` (the Nvidia/Jensen Huang reinstatement and record Wall Street rally, Ukraine's naval-drone strikes on Russian ships off Libya, the US–Iran Gulf standoff, the UK's 2035 Women's World Cup confirmation, India's $1.6bn pledge to Nepal, the Sudan Khartoum drone strikes, the Gisèle Pelicot row, the CrowdStrike–Zscaler deal, and more). The renderer (`render.py`, Python + Pillow, with `worldmap.py` for the simplified continent polygons) draws the whole page offline and deterministically from embedded data — no external images and no network — and the graded entrypoint (`main.ts`) copies the rendered `entry.png` to the output directory.

## Run it

```sh
node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
