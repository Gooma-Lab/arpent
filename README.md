# Arpent

> **Live demo:** _not deployed yet — due week 6._
> Status: week 1 of 12. The skeleton stands; the agent loop is not written.

Ask in plain language whether a technical niche in the JavaScript/TypeScript
ecosystem is **occupied**, **open**, or a **desert** — and get a verdict rather
than a dashboard.

A dashboard hands the interpretation back to you. Arpent decides, and says how
sure it is.

```
OCCUPIED                                        confidence 80%
14 active packages, 4 maintained in the last 6 months.

WHAT SUPPORTS THIS VERDICT     …
WHAT COULD NOT BE MEASURED     Is anyone paying? Not measurable
                               from npm and GitHub.
VERIFIABLE SAMPLE              the first 5 results, in the clear
```

## Why this is not a scraper

Before concluding, the agent **checks its own instrument**: it looks at a
sample of what it collected and asks whether it actually matches the question.
If it has drifted, it replans — twice at most, then answers anyway with
degraded confidence and a stated reason.

That step exists because of a real failure. A search for `wiki` returned
Instagram scrapers, because the registry also searches descriptions. The defect
was detectable in ten seconds by looking at a sample — and nobody looked. So
the tool now looks, every time, and shows you the sample so you can look too.

## What it cannot do

**npm and GitHub measure adoption. Never money.**

Arpent can tell you "nobody built this" or "whoever did stopped maintaining
it". It cannot tell you "somebody pays for this". It is a fast elimination
filter, not commercial validation — and it says so in the interface, not only
here.

This is why `DESERT` never reads as an opportunity. An empty space is usually
the absence of a problem.

## Design

| Decision | Rationale |
|---|---|
| One agent holds the context, spawning throwaway sub-agents | The only multi-agent pattern that survives production; peer channels degrade sequential reasoning by 39–70% |
| Models plan, judge relevance, and arbitrate. They never count | A counter is cheaper and more reliable than a language model at arithmetic |
| Thresholds and confidence are deterministic | A number you cannot reconstruct has no place in a tool about honest measurement |
| Raw SDK, no orchestration framework | Writing the loop teaches more than assembling one |
| Collected text is always data, never instruction | Package descriptions are third-party input, and a hostile one is cheap to publish |

Python 3.12 · Anthropic API · Gradio in a Docker container on Hugging Face
Spaces.

## Documentation

The design documents are in French, under [`docs/`](docs/). They are the source
of truth; this README is the summary.

| Document | Content |
|---|---|
| [PRODUCT](docs/PRODUCT.md) | Problem, personas, scope, structural limit |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | The loop, the deterministic/model boundary, pluggable sources |
| [DESIGN](docs/DESIGN.md) | Verdict layout, confidence formula, failure handling |
| [DATA](docs/DATA.md) | What is collected, what is kept, three data-quality rules |
| [SECURITY](docs/SECURITY.md) | Prompt injection, budget ceilings, legal posture |
| [DELIVERY](docs/DELIVERY.md) | 12-week schedule, checkpoint, reduction order |
| [THRESHOLDS](docs/THRESHOLDS.md) | The numbers behind the three verdicts, and their calibration log |
| [GLOSSARY](docs/GLOSSARY.md) | French terms in `docs/` ↔ English identifiers in the code |

## Development

```bash
uv sync --all-groups
uv run arpent --check
uv run pytest
uv run ruff check .
```

`uv` reads `.python-version` and installs the pinned interpreter itself. A test
fails loudly if the running interpreter is not 3.12 — drift between development
and deployment should surface in CI, not at deploy time.

Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY`. `GITHUB_TOKEN`
is optional: without it, GitHub enrichment is skipped, confidence drops, and
the missing source is named in the verdict.

## Scope

JavaScript/TypeScript packages and CLI tools, from the npm registry and the
GitHub API. Other package ecosystems are v2, and require no rewrite — only a
new connector.

Retail, after-sales service, repair, and resale are permanently out of scope.
This is an external constraint, enforced in code and covered by a test.

## License

MIT — see [LICENSE](LICENSE).
