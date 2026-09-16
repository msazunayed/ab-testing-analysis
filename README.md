# A/B Test Analysis: New Checkout Button

This is a full writeup of an A/B test on a checkout button redesign - the kind of thing I'd actually hand to a team after a test wraps up. I wanted something that goes past "here's the p-value" and actually shows the judgment calls that come up in a real test: checking the split wasn't broken, whether the sample was even big enough, whether the effect is the same for everyone or just some segment, and whether early results can be trusted.

Full notebook is here: [`ab_test_analysis.ipynb`](./ab_test_analysis.ipynb)

## The setup

An e-commerce team redesigned the checkout button (bigger, higher contrast, moved above the fold) and ran a 14-day test against the old one, 50/50 split, ~42,000 users.

- H0: the new button doesn't change conversion
- H1: it does
- Primary metric: conversion rate. Secondary: revenue per user
- alpha = 0.05, two-tailed

## What came out of it

| Metric | Control | Treatment | Diff | Significance |
|---|---|---|---|---|
| Conversion rate | 10.62% | 13.03% | +2.41pp (+22.7% relative) | z = 7.65, p < 0.0001 |
| Revenue / user | $5.03 | $6.44 | +$1.41 | Welch's t = 8.24, p < 0.0001 |

95% CI on the conversion lift: [1.79pp, 3.03pp] - so it's genuinely positive, not just noise that happened to land above zero.

## The parts that actually matter beyond "yes it's significant"

- Checked for sample ratio mismatch first (p = 0.626, fine) - no point trusting anything downstream if the split itself was broken
- Ran the two-proportion z-test by hand instead of importing it, so I can actually explain the math if someone asks
- Backed into the minimum effect size this sample could've detected, since a null result from an underpowered test doesn't really tell you anything
- Split by device and found the lift isn't even close to uniform - mobile went 10.2% -> 13.3%, desktop only 11.4% -> 12.6%. This alone changes what I'd actually recommend
- Looked at day-by-day results and there's a clear novelty spike the first couple days (+7.9pp at the peak) that settles down to something closer to +2-3pp later on - the later number is the one I'd trust for forecasting
- Revenue was tested separately with Welch's t-test since it's skewed and zero-inflated, not something you can treat like a clean proportion
- Turned the lift into an actual dollar estimate (~$282K/month at 200K monthly users) with a note on how rough that projection really is

## What I'd actually do with this

Ship it, but lead with mobile since that's where it's clearly working. I'd hold off calling desktop a win off this one test and run something longer just for that segment before deciding. Also worth checking conversion again a month or two after launch, since a chunk of the early lift looks like it could just be people reacting to something new.

Caveats worth keeping in mind: this only covers one 14-day window, so who knows how it'd hold up during a weird traffic period like a holiday, and the revenue number specifically is noisier than conversion, so I wouldn't treat that dollar figure as locked in.

## What's in here

```
ab_test_project/
├── README.md
├── generate_data.py          <- builds the fake dataset, comments explain the assumptions
├── ab_test_analysis.ipynb    <- the actual analysis, already run with all outputs/charts saved
├── requirements.txt
├── data/
│   └── ab_test_data.csv
└── charts/
    ├── conversion_rate_ci.png
    ├── segment_by_device.png
    └── daily_trend.png
```

## Running it yourself

```bash
pip install -r requirements.txt
python generate_data.py     # makes data/ab_test_data.csv
jupyter notebook ab_test_analysis.ipynb
```

## About the data

It's synthetic - I made it up (see `generate_data.py` for exactly what assumptions went into it) rather than pull a real company's numbers, mainly so I could bake in specific quirks (the device difference, the novelty effect) and know they'd actually be there to find. The analysis itself doesn't take any shortcuts because of that though - it's run exactly like I would on a real event log. If you wanted to swap in real data, it just needs the same columns (`user_id, group, device, date, converted, revenue`) and nothing else changes.

## Tools/skills used

Python, pandas, NumPy, SciPy for the hypothesis testing, Matplotlib/Seaborn for the charts, plus the actual thinking part - experiment design, picking the right test, power analysis, checking for heterogeneity, and writing it up in a way a non-technical stakeholder could still follow.
