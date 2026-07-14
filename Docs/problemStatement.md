# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview

The objective of this project is to build a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as **AMC (Asset Management Company) websites**, **AMFI**, and **SEBI**.

The system must strictly avoid providing investment advice, opinions, or recommendations. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

---

## Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)**-based assistant that:

- Answers factual queries about mutual fund schemes
- Uses a curated corpus of official documents
- Provides concise, source-backed responses

---

## Target Users

| User Group | Description |
|---|---|
| Retail Investors | Comparing mutual fund schemes and seeking factual information |
| Customer Support & Content Teams | Handling repetitive mutual fund queries efficiently |

---

## Scope of Work

### 1. Corpus Definition

The RAG corpus is built across **4 AMCs** and **20 mutual fund schemes**, spanning diverse categories. The **20 primary Groww scheme page URLs have been identified and confirmed** (listed below). These serve as the base data sources, supplemented by official AMC, AMFI, and SEBI documents.

#### 🏦 Parag Parikh Financial Advisory Services (PPFAS)

| # | Scheme | Category | Groww URL |
|---|---|---|---|
| 1 | Parag Parikh Long Term Value Fund – Direct Growth | Flexi Cap | [Link](https://groww.in/mutual-funds/parag-parikh-long-term-value-fund-direct-growth) |
| 2 | Parag Parikh ELSS Tax Saver Fund – Direct Growth | ELSS | [Link](https://groww.in/mutual-funds/parag-parikh-elss-tax-saver-fund-direct-growth) |
| 3 | Parag Parikh Large Cap Fund – Direct Growth | Large Cap | [Link](https://groww.in/mutual-funds/parag-parikh-large-cap-fund-direct-growth) |
| 4 | Parag Parikh Conservative Hybrid Fund – Direct Growth | Conservative Hybrid | [Link](https://groww.in/mutual-funds/parag-parikh-conservative-hybrid-fund-direct-growth) |
| 5 | Parag Parikh Liquid Fund – Direct Growth | Liquid | [Link](https://groww.in/mutual-funds/parag-parikh-liquid-fund-direct-growth) |

#### 🏦 HDFC Mutual Fund

| # | Scheme | Category | Groww URL |
|---|---|---|---|
| 6 | HDFC Silver ETF FoF – Direct Growth | FoF / Commodity | [Link](https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth) |
| 7 | HDFC Mid Cap Fund – Direct Growth | Mid Cap | [Link](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| 8 | HDFC Equity Fund – Direct Growth | Multi Cap | [Link](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
| 9 | HDFC Defence Fund – Direct Growth | Sectoral / Thematic | [Link](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth) |
| 10 | HDFC Small Cap Fund – Direct Growth | Small Cap | [Link](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth) |
| 11 | HDFC Gold ETF Fund of Fund – Direct Growth | FoF / Commodity | [Link](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth) |
| 12 | HDFC Nifty 50 Index Fund – Direct Growth | Index | [Link](https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth) |

#### 🏦 ICICI Prudential Mutual Fund

| # | Scheme | Category | Groww URL |
|---|---|---|---|
| 13 | ICICI Prudential Large Cap Fund – Direct Growth | Large Cap | [Link](https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth) |
| 14 | ICICI Prudential Silver ETF FoF – Direct Growth | FoF / Commodity | [Link](https://groww.in/mutual-funds/icici-prudential-silver-etf-fof-direct-growth) |
| 15 | ICICI Prudential Dynamic Plan – Direct Growth | Dynamic Asset Allocation | [Link](https://groww.in/mutual-funds/icici-prudential-dynamic-plan-direct-growth) |
| 16 | ICICI Prudential Technology Fund – Direct Growth | Sectoral / Thematic | [Link](https://groww.in/mutual-funds/icici-prudential-technology-fund-direct-growth) |

#### 🏦 Motilal Oswal Mutual Fund

| # | Scheme | Category | Groww URL |
|---|---|---|---|
| 17 | Motilal Oswal Focused Midcap 30 Fund – Direct Growth | Mid Cap | [Link](https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth) |
| 18 | Motilal Oswal Large and Midcap Fund – Direct Growth | Large & Mid Cap | [Link](https://groww.in/mutual-funds/motilal-oswal-large-and-midcap-fund-direct-growth) |
| 19 | Motilal Oswal Small Cap Fund – Direct Growth | Small Cap | [Link](https://groww.in/mutual-funds/motilal-oswal-small-cap-fund-direct-growth) |
| 20 | Motilal Oswal Focused Multicap 35 Fund – Direct Growth | Multi Cap | [Link](https://groww.in/mutual-funds/motilal-oswal-most-focused-multicap-35-fund-direct-growth) |

#### 📄 Corpus URL Status

| Source Type | Count | Status |
|---|---|---|
| Groww scheme pages | 20 URLs | ✅ **Defined & Confirmed** |

> **Note:** The 20 Groww scheme page URLs listed above are the **sole data sources** for this project. No PDFs, KIM, SID, or other supplementary documents are in scope for the current version.

---

### 2. FAQ Assistant Requirements

The assistant must answer **facts-only** queries, such as:

- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

**Response Formatting Rules:**

- Each response is limited to a **maximum of 3 sentences**
- Each response includes **exactly one citation link**
- Each response includes a footer:
  > *"Last updated from sources: `<date>`"*

---

### 3. Refusal Handling

The assistant must **refuse** non-factual or advisory queries, such as:

- *"Should I invest in this fund?"*
- *"Which fund is better?"*

Refusal responses should:
- Be polite and clearly worded
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

---

### 4. User Interface (Minimal)

The solution should include a simple interface with:

- A **welcome message**
- **Three example questions**
- A visible disclaimer:
  > *"Facts-only. No investment advice."*

---

## Constraints

### Data & Sources
- Use **only official public sources** (AMC, AMFI, SEBI)
- Do **not** use third-party blogs or aggregator websites

### Privacy & Security
Do not collect, store, or process:
- PAN or Aadhaar numbers
- Account numbers
- OTPs
- Email addresses or phone numbers

### Content Restrictions
- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance-related queries, provide a link to the official factsheet only

### Transparency
- Responses must be **short, factual, and verifiable**
- Every answer must include a **source link** and **last updated date**

---

## Expected Deliverables

| Deliverable | Details |
|---|---|
| **README Document** | Setup instructions, selected AMC and schemes, architecture overview (RAG approach), known limitations |
| **Disclaimer Snippet** | *"Facts-only. No investment advice."* |

---

## Success Criteria

- ✅ Accurate retrieval of factual mutual fund information
- ✅ Strict adherence to facts-only responses
- ✅ Consistent inclusion of valid source citations
- ✅ Proper refusal of advisory queries
- ✅ Clean, minimal, and user-friendly interface

---

## Summary

The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only verified, source-backed financial information — without any advisory bias or speculative content.

---

> **Disclaimer:** *Facts-only. No investment advice.*
