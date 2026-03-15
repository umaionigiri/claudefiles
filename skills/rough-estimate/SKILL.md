---
name: rough-estimate
description: |
  合同会社サイビットの概算見積書を作成。システム開発・コンサルティング・保守・研修に対応。
  単価: ¥15,000/時間。費用内訳、オプション比較、ROI分析、免責事項を含むMarkdown出力。
  トリガー: 「見積りを作成」「概算見積り」「費用見積り」「いくらかかるか」
---

# Rough Estimate Skill

## Company Information (Scibit LLC)

| Item | Value |
|------|-------|
| Company | 合同会社サイビット（Scibit LLC） |
| Hourly rate | ¥15,000/hour (pre-tax) |
| Daily rate | ¥120,000 (8 hours) |
| Monthly rate | ¥2,400,000 (20 days) |
| Contact | contact@scibit.ai |

### Pricing Display Options

| Mode | Display | Use Case |
|------|---------|----------|
| Detailed | Effort, rate, amount | Internal review, transparency-focused clients |
| Simple | Effort, amount only (no rate) | General client-facing |
| Amount only | Amount only | Executive summary |

**Validation**: Always verify internally with `effort × ¥15,000 = amount`

## Estimation Workflow

### Step 1: Gather Project Information

1. **顧客名** (Client name)
2. **案件名** (Project name)
3. **種別**: システム開発 / コンサルティング / 保守 / 研修
4. **概要**: What to achieve
5. **希望時期** (if any)
6. **予算感** (if any)
7. **特記事項**: Constraints, etc.

### Step 2: Select Estimate Type

| Type | Reference | Features |
|------|-----------|----------|
| システム開発 | @references/estimate-types.md | Phase-based effort, architecture comparison |
| コンサルティング | @references/estimate-types.md | Duration/deliverable-based |
| 保守 | @references/estimate-types.md | Monthly, SLA definition |
| 研修 | @references/estimate-types.md | Headcount/session-based |

### Step 3: Document Structure

See @references/document-structure.md.

**Required sections:**
1. Header (date, validity, addressee)
2. Rough estimate disclaimer
3. Executive summary
4. Estimated costs
5. Included/excluded items
6. Notes and disclaimers
7. Contact information

**Optional sections (as needed):**
- Current state analysis, solution overview, architecture options
- Implementation roadmap (Gantt), ROI analysis, risks and countermeasures
- RACI table (joint projects), value proposition, next steps

### Step 4: Effort and Cost Calculation

See @references/cost-estimation.md.

**Phase Effort Ratios (MVP development):**

| Phase | Ratio |
|-------|-------|
| PM・顧客調整 | 10-12% |
| 要件定義・設計 | 12-16% |
| 環境構築 | 10-14% |
| データ移行 | 15-20% |
| コア開発 | 20-25% |
| UI開発 | 10-14% |
| テスト・調整 | 10-12% |
| 引き渡し | 5-6% |
| バッファ | 4-5% |

### Step 5: Internal Estimate (Required)

Always create an internal estimate alongside the client-facing one.

**File naming:**
- Client: `{project}_概算見積-{title}_{YYYYMMDD}.md`
- Internal: `{project}_（内部）概算見積-{title}_{YYYYMMDD}.md` (same directory)

**Template:** @assets/internal-template.md

**Required internal sections:**
1. Internal-only notice (no client sharing)
2. Rate setup (selling rate, cost rate, margin)
3. Effort breakdown per pattern/option (selling amount, cost, gross profit)
4. Effort validity analysis (comparison with similar estimates if available)
5. Mapping to existing estimates (if applicable)
6. Revenue analysis summary

**Calculation rules:**
- Selling amount: `effort × selling rate` (rounded to ¥10,000)
- Cost: `effort × cost rate` (exact)
- Gross profit: `selling amount - cost`
- Margin: `(selling amount - cost) / selling amount × 100`

**Selling rate determination:**
- Default: ¥180,000/person-day (= ¥22,500/h, 1.5x cost)
- Use project-specific rate if defined (in CLAUDE.md, etc.)

### Step 6: Calculation Verification (Required)

Verify before output:

**Client-facing:**
1. Each line amount is consistent
2. Subtotals sum to total
3. Monthly × 12 = Annual (running costs)
4. ROI assumptions and results are consistent
5. Comparison table options use same logic
6. **No rate exposure** (no effort/rate leaking)

**Internal:**
1. Each line: `effort × selling rate ≈ selling amount` (¥10,000 rounding allowed)
2. Each line: `effort × cost rate = cost` (exact match)
3. Each line: `selling amount - cost = gross profit`
4. Client and internal selling amounts match exactly

**Common calculation mistakes:**
- Digit errors (e.g., 40h → ¥60,000 instead of ¥600,000)
- Monthly-to-annual conversion omission
- Tax-inclusive notation (pre-tax is correct)
- Amount mismatch between internal and client

### Step 7: Disclaimers

See @references/disclaimers.md. Always specify:
- **This is a rough estimate**
- **Pre-tax pricing**
- **Validity period** (typically 1 month)
- **Included/excluded items**
- **Variable factors**

## Phased Investment

Propose phased approach when:
- High uncertainty (technical validation needed, fluid requirements)
- Data accumulation / AI training required
- Long-term project (1+ years)
- Large investment (¥10,000,000+)

## Joint Projects

For multi-company projects, clarify:
- Estimate scope and responsibility boundaries
- RACI-format role assignment table
- Integration specifications

## Templates

- Client-facing: @assets/template.md
- Internal: @assets/internal-template.md

## Quick Reference

### Scale Guide (System Development)

| Scale | Effort | Duration | Estimated Cost |
|-------|--------|----------|---------------|
| Small | 40-80h | 2-4 weeks | ¥600,000-1,200,000 |
| Medium | 200-400h | 2-4 months | ¥3,000,000-6,000,000 |
| Large | 800h+ | 6+ months | ¥12,000,000+ |

### Cost Structure Patterns

| Type | Initial Cost | Running Cost |
|------|-------------|-------------|
| On-premises | High | Low |
| Hybrid | Medium | Medium |
| Cloud | Low | High |

### Maintenance Plan Guide

| Plan | Support Hours | Monthly |
|------|-------------|---------|
| Light | Weekdays 10-18 | ¥150,000+ |
| Standard | Weekdays 9-21 | ¥300,000+ |
| Premium | 24/7/365 | ¥600,000+ |

## Running Cost Rules

When including a running cost section, always:

1. **Reference actual data**: Read `docs/billing/` etc. for license cost actuals
2. **Context7 verification for external services**: Check latest pricing via Context7. Docs/memory info may be stale
3. **Tax notation consistency**: Main estimate is pre-tax; license actuals may be tax-inclusive. Add notes when mixed
4. **New infra disclosure**: If new infra (DB, storage, etc.) is needed, specify setup cost in initial and monthly impact in running

## Client Estimate Rate Protection

To prevent rate reverse-engineering:

1. **Cost breakdown shows amounts only**: No effort (person-days/hours). Feature-based amounts only
2. **Gantt at coarse granularity**: Phase-level ("Design & Implementation", etc.). No per-task day counts
3. **Schedule consistency**: Verify overview "~X weeks" matches Gantt critical path

## Important Notes

1. **Output estimate documents in Japanese**
2. **Always state this is a rough estimate**
3. **Pre-tax pricing**
4. **Set validity period** (typically 1 month)
5. **Specify exclusions** (infra, licenses, etc.)
6. **Explain variable factors**
7. **State ROM accuracy (±25-50%) in disclaimers**
8. **Always create internal estimate simultaneously** (record effort, cost, margin rationale)

## Reference Documents

- @references/document-structure.md — Section structure, Mermaid diagram patterns
- @references/cost-estimation.md — Calculation methods, ROI, multi-layer cost structure
- @references/disclaimers.md — Notes and disclaimer templates
- @references/estimate-types.md — Development/consulting/maintenance/training, phased investment
- @assets/template.md — Copy and use
