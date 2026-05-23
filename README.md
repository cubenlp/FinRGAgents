# FinRGAgents: A Multi-Agent Collaboration Framework for Multi-modal Chinese Financial Research Report Generation

This repository contains the code and data for the ACL 2025 submission:

> **FinRGAgents: A Multi-Agent Collaboration Framework for Multi-modal Chinese Financial Research Report Generation**  
> Anonymous ACL submission

---

## Overview

We formulate **MM-FinRG** (Multi-Modal Chinese Financial Research Report Generation), a new task requiring a system to synthesize heterogeneous evidence — market news, stock indicators, annual reports, and financial metrics — into a coherent, forward-looking, multimodal research report. Three constituent challenges make this task distinct from prior report generation work:

- **(C1)** Evidence synthesis from heterogeneous multi-source inputs  
- **(C2)** Dialectical viewpoint construction through explicit argument–counterargument reasoning  
- **(C3)** Schema-grounded multimodal generation maintaining semantic consistency between text and co-produced charts

To address MM-FinRG, we propose **FinRGAgents**, a collaborative multi-agent framework built on AutoGen that mirrors the analytical workflow of a professional sell-side research team. The system operates through three coordinated stages targeting C1–C3 respectively.

We also construct **FinRG**, a large-scale benchmark of 1,500 multimodal financial research reports spanning 25 industry domains (avg. report length: 5,723 tokens), and introduce a four-dimensional LLM-as-judge evaluation protocol covering Factuality, Forward-looking reasoning, Logical coherence, and Vision–text consistency.

---

## Framework

### System Overview

```
Input: I = {c, n, s, a, f}
  c: company name
  n: market news (latest 30-day articles)
  s: stock indicators (latest 120-trading-day OHLCV + technical indicators)
  a: annual report (PDF → Markdown, with tables and unstructured text)
  f: financial metrics (12-month structured data: P/E, ROE, etc.)

                    ┌─────────────────────────────────┐
                    │   Stage 1: Information           │
                    │   Summarization                  │
                    │                                  │
                    │  Stock Analyst ──┐               │
                    │  News Analyst ───┤               │
                    │  Business Analyst┤→ Analyst      │
                    │  FinData Analyst─┘   Manager     │
                    └────────────────────────┬────────┘
                                             │ Info
                    ┌────────────────────────▼────────┐
                    │   Stage 2: Plan Generation       │
                    │                                  │
                    │  Thesis Proponent Agent    ┐     │
                    │  Counterargument Agent ────┤→    │
                    │  Rejoinder Proponent Agent ┘     │
                    │  (Chief Analyst dialectical debate│
                    │   → core view V̄m)               │
                    │                                  │
                    │  Senior Analyst → Outline O      │
                    └────────────────────────┬────────┘
                                             │ Outline + V̄m
                    ┌────────────────────────▼────────┐
                    │   Stage 3: Report Writing        │
                    │                                  │
                    │  Research Analyst (Code-as-Action│
                    │  + RAG + Visual Schema)          │
                    │  Quality Inspector (dual verify) │
                    └────────────────────────┬────────┘
                                             │
                              Multimodal Research Report (Markdown)
```

---

### Stage 1: Information Summarization

Four specialist agents extract and reconcile evidence from multi-source inputs:

| Agent | Role | Key Tools |
|---|---|---|
| **Stock Analyst Agent** | Computes technical indicators (MA, MACD, KDJ) on 120-day price series to identify momentum and reversal signals | `get_stock_data`, `stock_indicators` |
| **News Analyst Agent** | Retrieves material events (earnings surprises, regulatory changes, macro shifts) and extracts impact factors | `get_company_news`, `get_news_factor` |
| **Business Analyst Agent** | Distills the annual report into business highlights, revenue mix, cash flow quality, and risk assessment | `analyze_business_highlights`, `get_risk_assessment`, `analyze_cash_flow` |
| **FinData Analyst Agent** | Computes valuation and profitability ratios (P/E, ROE, etc.) on a trailing-twelve-month basis | `get_pe_eps_performance`, `get_share_performance` |

The **Analyst Manager Agent** aggregates these outputs and resolves inter-source conflicts using a domain-motivated priority rule: audited annual-report data takes precedence over market-derived signals when claims are contradictory.

---

### Stage 2: Plan Generation (Core View + Outline)

Inspired by the investment committee process, the **Chief Analyst Agent** is split into three specialized variants that engage in multi-round dialectical debate:

**Thesis Proponent Agent (A_tp)**
- Proposes an initial major investment view v_m (Buy / Hold / Sell with a 12-month price target rationale)
- Generates 3–5 supporting sub-views (v_1, ..., v_n), each grounded in at least one data point

**Counterargument Proponent Agent (A_cp)**
- Generates an *overriding rebuttal* r_i that directly challenges the validity of each v_i
- Produces a revised view v̄_i integrating the challenge

**Rejoinder Proponent Agent (A_rp)**
- Introduces *undercutting rebuttals* r^u_i to address hidden assumptions not caught in the first pass
- Produces further-refined views ṽ_i

The two-stage refinement process per sub-view is: v_i →(A_cp)→ v̄_i →(A_rp)→ ṽ_i. The Thesis Proponent Agent synthesizes all refined sub-views {ṽ_1, ..., ṽ_n} into the final major view V̄_m. Debate terminates when the cosine similarity between consecutive view embeddings exceeds 0.9 (max 3 rounds).

The **Senior Analyst Agent** then translates the ratified thesis into a structured report outline (JSON format with second-level and third-level headings, plus Visual Schema specifications for each section).

---

### Stage 3: Multimodal Report Writing

The **Research Analyst Agent** adopts a **Code-as-Action** paradigm:

1. Retrieves fine-grained knowledge from Stage 1 outputs via RAG, conditioned on each section heading in the outline
2. For sections requiring visualization, generates a **Visual Schema** (JSON) that explicitly maps narrative data to chart parameters:
   ```json
   {
     "chart_type": "bar|line|pie",
     "x_axis": ["label1", "label2", ...],
     "y_axis": [num1, num2, ...],
     "caption": "chart title"
   }
   ```
3. Synthesizes executable Python code (Matplotlib/Seaborn) to render charts in a sandboxed environment, ensuring every pixel is traceable to specific data points
4. Integrates text and charts using Markdown syntax

The **Quality Inspector Agent** conducts a dual-verification loop:
- **Factual grounding**: verifies that every quantitative claim is traceable to a specific entry in the Stage 1 information base
- **Visual–textual consistency**: verifies that chart axes and data match the narrative description

If issues are found, the Research Analyst Agent is triggered to revise (max 3 cycles; persistent issues are flagged for human review).

---

## FinRG Dataset

FinRG is a large-scale benchmark of **1,500 multimodal financial research reports** sourced from Eastmoney, spanning **25 industry domains**. All reference reports are institutionally authored and pass a four-criterion quality filter: (1) attributed to registered institutional contributors; (2) ≥ 2,000 characters of substantive analysis; (3) includes at least one structured financial data table; (4) published within the target time window. This filtering reduces the raw pool by ~62%.

| Statistic | Value |
|---|---|
| Reports | 1,500 |
| Industry domains | 25 |
| Avg. prompt length | 2,054 tokens |
| Avg. report length | 5,723 tokens |
| Time span | 2023.01 – 2024.08 |

The `dataset/` directory in this repository contains the **annual report source documents** (1,506 annual report PDFs converted to Markdown via Doc2x), which serve as the `a` component of the input I = {c, n, s, a, f}. These are distinct from the FinRG research report benchmark.

---

## Evaluation Protocol

We propose a four-dimensional **LLM-as-judge** protocol (scored 1–5):

| Dimension | What it measures |
|---|---|
| **Factuality** | Accuracy of facts and traceability to source data |
| **Forward-looking** | Depth and reliability of predictive analysis and investment rationale |
| **Logical** | Coherence, data-to-insights progression, and document-level structure |
| **Vision** | Semantic consistency between textual claims and co-generated charts |

Human agreement analysis (9 finance postgraduates, 3 independent groups) yields Pearson = 0.75 and Spearman = 0.80 (avg. Cohen's Kappa = 0.759), surpassing the 0.5–0.7 range reported for general text generation tasks.

---

## Main Results

FinRGAgents achieves state-of-the-art performance on the FinRG benchmark (GPT-5.1 backbone, averaged over 5 runs):

| Method | Factuality | Forward-looking | Logical | Vision | Avg |
|---|---|---|---|---|---|
| E2E LLM | 2.93 | 3.03 | 3.21 | — | 3.06 |
| CoT LLM | 3.10 | 2.98 | 3.35 | — | 3.15 |
| LongWriter | 3.09 | 3.12 | 3.37 | — | 3.19 |
| STORM | 3.05 | 3.08 | 3.24 | — | 3.12 |
| FinRobot | 2.72 | 2.64 | 2.88 | 2.79 | 2.75 |
| FinSight | 3.13 | 3.24 | 3.32 | 3.59 | 3.32 |
| **FinRGAgents** | **3.14** | **3.59**\*\* | **3.64**\*\* | **3.63**\*\* | **3.50**\*\* |

\*\* p < 0.01 over best baseline (paired t-test). FinRGAgents improves over FinRobot by 26.9% and outperforms FinSight (the strongest multimodal baseline) across all dimensions. Average report generation time: 356 seconds (60× faster than human experts); cost: $5/report with GPT-5.1.

---

## Repository Structure

```
FinRGAgents/
├── dataset/                        # 1,506 annual report Markdown files (annual report inputs)
├── fin2rg/
│   ├── agents/
│   │   ├── architecture.py         # Agent role definitions and toolkit assignments
│   │   ├── finrobot.py             # FinRobot agent class (AutoGen AssistantAgent subclass)
│   │   └── prompts.py              # System prompt templates (leader, role)
│   ├── argument_gen/
│   │   ├── argument_gen_utils.py   # Core view generation and report planning pipeline
│   │   └── prompts.py              # Prompts for claim/rebuttal/refinement
│   ├── data_source/
│   │   ├── tushare_utils.py        # TuShare API integration (stock prices, financial statements)
│   │   ├── news_utils.py           # Company news retrieval (Eastmoney)
│   │   └── sec_utils.py            # Regulatory filing utilities
│   ├── functional/
│   │   ├── analyzer.py             # Financial data analysis (Stage 1 tools)
│   │   ├── charting.py             # Chart generation (Matplotlib / mplfinance)
│   │   ├── writing.py              # Report content writing utilities
│   │   ├── report.py               # PDF rendering (ReportLab)
│   │   └── baseline.py             # Baseline comparison utilities
│   ├── toolkits.py                 # AutoGen function registration helpers
│   ├── utils.py                    # LLM query wrapper, file I/O, date utilities
│   └── log_util.py                 # Logging configuration
└── README.md
```

---

## Requirements

```
pyautogen>=0.2
tushare
openai
pandas
matplotlib>=3.8
mplfinance
seaborn>=0.13
reportlab
pymupdf
chinese_calendar
python-dateutil
```

Install via:

```bash
pip install pyautogen tushare openai pandas matplotlib mplfinance \
            seaborn reportlab pymupdf chinese_calendar python-dateutil
```

---

## Configuration

API keys are loaded at runtime from a JSON file:

```python
from fin2rg.utils import register_keys_from_json
register_keys_from_json("keys.json")
```

`keys.json` format:

```json
{
  "TUSHARE_TOKEN": "<tushare token>",
  "OPENAI_API_KEY": "<openai api key>",
  "NEWS_API_KEY": "<news api key>"
}
```

The LLM backend supports GPT-5.1 / GPT-4o (via OpenAI API) and Qwen3-32B (local inference via vLLM). Model selection is configured via the `model` parameter in `fin2rg/utils.py`.

---

## Usage

```python
from fin2rg.utils import register_keys_from_json
from fin2rg.argument_gen.argument_gen_utils import build_annual_report_key_infos

register_keys_from_json("keys.json")

build_annual_report_key_infos(
    company="宁德时代",
    stock_code="300750.SZ"
)
```

Agent role definitions, toolkit assignments, and group configurations are specified in `fin2rg/agents/architecture.py`. The Core View Generation pipeline (Thesis / Counterargument / Rejoinder) is implemented in `fin2rg/argument_gen/argument_gen_utils.py` and `fin2rg/argument_gen/prompts.py`.

---

## License

This code is released for research purposes under the terms of the associated paper. The complete source code, including preprocessing scripts, will be fully open-sourced upon acceptance.
