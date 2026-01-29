# Cost Estimation Methods

Standard methods for effort calculation and cost estimation in rough estimates.

## Table of Contents

- Base Rates
- Phase-based Effort Ratios
- Cost Structure Patterns
- Multi-layer Cost Structure
- Cost Breakdown Templates
- Option Comparison Summary
- ROI Analysis
- Phased Investment Pattern (Annual Cost Estimation)
- Estimation Accuracy Levels
- Effort Estimation Tips
- Calculation Verification Flow
- Checklist

## Base Rates

| Item | Cost Rate | Selling Price | Notes |
|------|-----------|---------------|-------|
| Hourly Rate | ¥15,000/h | ¥22,500/h | 1.5x margin |
| Daily Rate | ¥120,000 | ¥180,000 | 8 hours |
| Monthly Rate | ¥2,400,000 | ¥3,600,000 | 20 days |

## Profit Margin Calculation

### Development Cost Margin (1.5x)

```
Selling Price = Cost × 1.5
Cost = Selling Price ÷ 1.5

Example:
- Cost: 100h × ¥15,000 = ¥1,500,000
- Selling Price = ¥1,500,000 × 1.5 = ¥2,250,000
- Gross Profit = ¥750,000 (33% margin)
```

### Running Cost Margin (20%)

```
Selling Price = Cost ÷ (1 - 0.2) = Cost ÷ 0.8 = Cost × 1.25

Example:
- Cloud Cost: ¥10,000/month
- Selling Price = ¥10,000 ÷ 0.8 = ¥12,500/month
- Margin = ¥2,500 (20% margin)
```

### Cost Breakdown Template (with profit)

```markdown
### Cost Breakdown

| Item | Amount | Notes |
|------|--------|-------|
| Cost (XXh × ¥15,000) | ¥X,XXX,XXX | |
| Gross Profit (Cost × 0.5) | ¥XXX,XXX | 1.5x margin |
| **Selling Price** | **¥X,XXX,XXX** | Tax excluded |
```

### Running Cost Template (with margin)

```markdown
### Monthly Running Costs

* Selling Price = Cost ÷ (1 - 0.2) (includes 20% margin)

| Item | Cost (tax excl.) | Selling Price (tax excl.) | Notes |
|------|------------------|---------------------------|-------|
| Cloud Infrastructure | ¥XX,XXX | ¥XX,XXX | GCP/AWS |
| External API Usage | ¥XX,XXX | ¥XX,XXX | Usage-based |
| **Monthly Total** | **¥XX,XXX** | **¥XX,XXX** | |
```

## Phase-based Effort Ratios (MVP Development)

| Phase | Ratio | Notes |
|-------|-------|-------|
| PM & Client Coordination | 10-12% | Project management, meetings |
| Requirements & Design | 12-16% | Specifications, architecture design |
| Environment Setup | 10-14% | Infrastructure, CI/CD, dev environment |
| Data Migration | 15-20% | When existing data migration required |
| Core Development | 20-25% | Main feature implementation |
| UI Development | 10-14% | Frontend implementation |
| Testing & Adjustments | 10-12% | Unit, integration, system testing |
| Handover | 5-6% | Documentation, training, delivery |
| Buffer | 4-5% | Risk buffer |

**Note**: If no data migration, redistribute to other phases.

## Cost Structure Patterns

### On-premise
```
Initial Cost: High (server purchase, licenses)
Running Cost: Low (electricity, maintenance)
Characteristics: Cost-effective for long-term operation, requires initial investment
```

### Hybrid
```
Initial Cost: Medium
Running Cost: Medium-High
Characteristics: Balance of flexibility and control
```

### Cloud
```
Initial Cost: Low (pay-as-you-go)
Running Cost: High (monthly fees)
Characteristics: Small start possible, scalable
```

## Multi-layer Cost Structure

Break down running costs by layer:

```
Running Cost = Infrastructure Layer + Service Layer + Operations Layer
```

| Layer | Examples | Variable Factors |
|-------|----------|------------------|
| Infrastructure | Cloud usage, DB, storage | Data volume, traffic |
| Service | External APIs, SaaS, licenses | Usage volume, user count |
| Operations | Maintenance, monitoring, improvement | SLA, coverage scope |

### Multi-layer Cost Breakdown Template
```markdown
### Monthly Running Costs (Multi-layer Structure)

| Layer | Item | Content | Monthly (tax excl.) |
|-------|------|---------|---------------------|
| **Infrastructure** | | | |
| | Cloud Platform | AWS/GCP/Azure | ¥XX,XXX-¥XX,XXX |
| | Database | RDS/Cloud SQL | ¥XX,XXX-¥XX,XXX |
| | Storage | S3/GCS | ¥X,XXX-¥XX,XXX |
| **Service** | | | |
| | External API | OpenAI API etc. | ¥XX,XXX-¥XXX,XXX |
| | SaaS Integration | Monitoring tools etc. | ¥X,XXX-¥XX,XXX |
| **Operations** | | | |
| | Maintenance Support | Inquiry handling | ¥XXX,XXX |
| | Monitoring & Ops | 24h monitoring | ¥XX,XXX |
| **Monthly Total** | | | **¥XXX,XXX-¥XXX,XXX** |

* Range shown to account for usage-based variation
```

### Scaling Projections

| Scale Stage | Users | Infrastructure | Service | Operations |
|-------------|-------|----------------|---------|------------|
| Initial | ~100 | ¥Xm | ¥Xm | ¥Xm |
| Growth | ~1,000 | ¥XXm | ¥XXm | ¥Xm |
| Expansion | ~10,000 | ¥XXm | ¥XXXm | ¥XXm |

**Note**: Service layer (especially AI API usage) tends to scale rapidly with usage

## Cost Breakdown Templates

### Initial Costs
```markdown
### Initial Costs

| Item | Hours | Rate | Amount |
|------|-------|------|--------|
| Requirements & Design | XXh | ¥15,000 | ¥XXX,XXX |
| Environment Setup | XXh | ¥15,000 | ¥XXX,XXX |
| Development | XXh | ¥15,000 | ¥XXX,XXX |
| Testing | XXh | ¥15,000 | ¥XXX,XXX |
| PM & Management | XXh | ¥15,000 | ¥XXX,XXX |
| **Subtotal** | | | **¥X,XXX,XXX** |
```

### Running Costs
```markdown
### Monthly Running Costs

| Item | Content | Monthly |
|------|---------|---------|
| Infrastructure | Cloud usage | ¥XX,XXX |
| Maintenance Support | Inquiry handling | ¥XX,XXX |
| Monitoring & Ops | System monitoring | ¥XX,XXX |
| **Monthly Total** | | **¥XXX,XXX** |
```

## Option Comparison Summary

```markdown
## Cost Comparison Summary

| Item | Option A | Option B | Option C |
|------|----------|----------|----------|
| Initial Cost | ¥X,XXX,XXX | ¥X,XXX,XXX | ¥X,XXX,XXX |
| Monthly Cost | ¥XXX,XXX | ¥XXX,XXX | ¥XXX,XXX |
| Annual Running | ¥X,XXX,XXX | ¥X,XXX,XXX | ¥X,XXX,XXX |
| 3-Year Total | ¥XX,XXX,XXX | ¥XX,XXX,XXX | ¥XX,XXX,XXX |
```

## ROI Analysis

### Formulas
```
ROI = (Annual Savings - Annual Cost) / Initial Investment × 100%

Payback Period = Initial Investment / (Annual Savings - Annual Cost)
```

### Client Terminology Adaptation

Adapt job titles and terms in ROI analysis to client context:

| Generic Term | Client Adaptation Examples |
|--------------|---------------------------|
| Consultant | Operations staff, team member, operator |
| Analysis effort | Aggregation work, report creation, data review |
| Labor rate | Hourly rate, personnel cost |

**Note:** Always mark assumptions with "(TBC)" or "(to be confirmed)"

### Analysis Template
```markdown
## ROI Analysis

> ⚠️ **Note**: The following is a **reference estimate** and actual
> results will vary based on your operational conditions.
> Formal ROI evaluation recommended after validation.

### Assumptions (Estimated Values)
- Current operations staff analysis effort: XX hours/month (TBC)
- Operations staff labor rate: ¥X,XXX/hour (TBC)
- Post-implementation reduction rate: XX% (estimated from automation)

### Impact Estimate
| Item | Amount |
|------|--------|
| Current Cost (Annual) | ¥X,XXX,XXX |
| Savings (Annual) | ¥X,XXX,XXX |
| System Cost (Annual) | ¥X,XXX,XXX |
| **Net Benefit (Annual)** | **¥X,XXX,XXX** |
| **Payback Period** | **~X months** |

### Qualitative Benefits (Not included in ROI)
| Benefit | Description |
|---------|-------------|
| Faster Decision-making | Potential Xx+ improvement vs. current |
| Reduced Opportunity Loss | Shortened lead time |
```

### Assumption Notation Rules

| Assumption Type | Notation Example | Description |
|-----------------|------------------|-------------|
| Actual Data | "20 hours/month (actual)" | Client-provided real data |
| Estimated Value | "20 hours/month (TBC)" | Pre-hearing assumption |
| Industry Standard | "20 hours/month (industry avg.)" | Based on published data/research |

## Phased Investment Pattern

For large-scale or high-uncertainty projects, propose phased investment:

```
Phase 1 (Validation) → Phase 2 (Expansion) → Phase 3 (Full Operation)
```

### Phase Division Template
```markdown
## Phased Investment Plan

### Phase 1: Validation (X months)
| Item | Content | Cost |
|------|---------|------|
| Objective | Technical validation, PoC | - |
| Initial Cost | Requirements & development | ¥X,XXX,XXX |
| Running | Infrastructure & API | ¥XX,XXX/month |
| Go/No-go Criteria | KPI achievement XX%+ | - |

### Phase 2: Expansion (X months)
| Item | Content | Cost |
|------|---------|------|
| Objective | Feature expansion, data accumulation | - |
| Additional Development | Feature additions | ¥X,XXX,XXX |
| Running | Scale-up | ¥XXX,XXX/month |
| Go/No-go Criteria | XXX users achieved | - |

### Phase 3: Full Operation
| Item | Content | Cost |
|------|---------|------|
| Objective | Full deployment, optimization | - |
| Additional Development | Enhancement & optimization | ¥X,XXX,XXX |
| Running | Full scale | ¥XXX,XXX/month |
```

### Annual Cost Estimation Template
```markdown
## Annual Cost Estimate

### Assumptions
- Operation Start: XXXX/XX
- Expected Usage: XX cases/month

### Estimate
| Item | Amount |
|------|--------|
| Initial Development | ¥X,XXX,XXX |
| Annual Running | ¥X,XXX,XXX |
| **Year 1 Total** | **¥X,XXX,XXX** |
```

## Estimation Accuracy Levels

| Accuracy Level | Variance Range | Use Case |
|----------------|----------------|----------|
| Rough (ROM) | ±50% | Early exploration |
| Budget Estimate | ±25% | Budget planning |
| Firm Estimate | ±10% | Purchase decision |

**This skill assumes "Rough (ROM)" level.**

## Effort Estimation Tips

### Increase Factors (coefficient 1.2-1.5)
- Many existing system integrations
- Large data migration volume
- Strict security requirements
- Many stakeholders

### Decrease Factors (coefficient 0.8-0.9)
- Prior experience with similar projects
- Standard package usage
- Clear requirements

## Calculation Verification Flow

Required verification before outputting estimate.

### Step 1: Unit Price Verification
```
Each row: Hours × ¥15,000 = Amount

Example:
- Requirements: 40h × ¥15,000 = ¥600,000 ✓
- Development: 120h × ¥15,000 = ¥1,800,000 ✓
```

### Step 2: Total Verification
```
Subtotal = Σ(Each row amount)
Total = Subtotal + Overhead (if any)

Example:
- Requirements: ¥600,000
- Development: ¥1,800,000
- Testing: ¥450,000
- Subtotal: ¥2,850,000 ✓
```

### Step 3: Running Cost Verification
```
Annual = Monthly × 12
Year 1 Total = Initial + Annual Running

Example:
- Monthly: ¥100,000
- Annual: ¥1,200,000 ✓
- Initial: ¥3,000,000
- Year 1 Total: ¥3,000,000 + ¥1,200,000 = ¥4,200,000 ✓
```

### Step 4: ROI Verification
```
Savings = Current Cost × Reduction Rate
Net Benefit = Savings - System Cost
Payback = Initial Investment ÷ Annual Net Benefit

Example:
- Current: 100h/month × ¥5,000 = ¥500,000/month = ¥6,000,000/year
- 50% reduction: ¥3,000,000/year
- System cost: ¥1,200,000/year
- Net benefit: ¥1,800,000/year ✓
- ¥3,000,000 initial ÷ ¥1,800,000 = ~1.7 years ✓
```

### Step 5: Comparison Table Consistency
```
Verify all options use same calculation logic:
- Unit rates are consistent
- Running cost calculation periods are consistent
```

## Checklist

Verification items when creating estimates:

**Content:**
- [ ] Stated assumptions
- [ ] Specified inclusions/exclusions
- [ ] Provided costs by option
- [ ] Explained variable factors
- [ ] Noted tax-excluded pricing
- [ ] Set validity period

**Calculations:**
- [ ] Hours × Rate = Amount matches all rows
- [ ] Subtotals and totals are accurate
- [ ] Monthly × 12 = Annual running is accurate
- [ ] ROI assumptions align with results
- [ ] Comparison table options use consistent logic

**Profit Margins:**
- [ ] Development costs include 1.5x margin
- [ ] Cost and selling price are explicit
- [ ] Running costs include 20% margin
- [ ] Margin formula (cost ÷ 0.8) is correct
