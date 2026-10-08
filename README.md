# Shakepay — Reward Eligibility Intelligence

Independent research and technical proof-of-work by **Felipe Mattos**.

**Question:** When a paycheque arrives but a reward does not appear as expected, how could a team distinguish an ineligible event, a classification ambiguity and a genuine discrepancy?

**Study:** https://felipervm.github.io/shakepay-reward-intelligence/

The website has a chapter-based fullscreen navigation and a simplified interactive eligibility demonstration. It is independent, not affiliated with Shakepay, and not a consulting pitch. I built it to demonstrate how I approach product/data questions while interested in working at the company.

### Repository
- `index.html`, `site/styles.css`, `site/script.js`: static GitHub Pages site.
- `model.py`: simplified public-rule eligibility engine.
- `rules/reward_status_v1.json`: illustrative versioned rule assumptions.
- `analysis.py`: deterministic synthetic dataset generator.
- `tests/test_model.py`: model unit tests.
- `sql/eligibility_audit.sql`: reconciliation queries.
- `notebooks/analysis.ipynb`: reproducible notebook.
- `docs/RESEARCH_AND_METHOD.md`: evidence, boundaries and evaluation plan.

### Run
```bash
python analysis.py
python -m unittest discover -s tests -v
python -m http.server 8000
```
Open http://localhost:8000/.

**Reproducibility note:** this repository contains a rebuilt model and deterministic generator for the public portfolio study. The previously prepared original analytical package and image assets are not byte-for-byte copies here. Generated records and summary numbers are synthetic, not real Shakepay operations data. The website's figures denote synthetic design inputs, not proven issues or measured business impact.

Author: Felipe Mattos · October 2026.
