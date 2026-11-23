# The World in One Page — 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/ariallg90-gif/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/ariallg90-gif/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Entry for the [news-image-20261122](https://make.fun/bounty/news-image-20261122)
bounty on [make.fun](https://make.fun): sum up Sunday 22 November 2026's
world news in a single image.

`main.py` (Python 3.13, standard library only) draws a one-page newspaper
front page — "THE WORLD IN ONE PAGE" — with six stories from 22 November
2026: the COP31 climate talks collapsing in Antalya, two tankers struck
near the Strait of Hormuz, Ukraine sinking a Russian warship off Libya,
the capture of cartel kingpin "El Chapo Isidro" in Mexico, the Delta
system outage delaying 1,600+ flights, and the Indonesian candy factory
fire with 34 workers missing. Everything is drawn in code: a hand-rolled
PNG encoder, a tiny rasteriser and a home-made 5x7 bitmap font. No
network, no external files, deterministic — two runs produce a
byte-identical PNG.

## Run

```sh
mkdir -p /output
python3 main.py        # writes /output/entry.png (1024x1024, PNG)
```

## License

MIT — see [LICENSE](LICENSE).
