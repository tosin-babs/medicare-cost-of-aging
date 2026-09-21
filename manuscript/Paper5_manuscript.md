# Health-State Transitions and the Lifetime Cost of Aging: A Multi-State Actuarial Model of Medicare Spending and Household Out-of-Pocket Tail Risk

**Oluwatosin Dorcas Babalola**¹ *(corresponding author)*, **Oluwakemi Elizabeth Iroko**¹, **Doris Ansah**²

¹ Department of Actuarial Science and Quantitative Risk Analysis and Management, Georgia State University, Atlanta, GA, USA. obabalola4@student.gsu.edu

² J. Mack Robinson College of Business, Georgia State University, Atlanta, GA, USA.

**Word count.** 7,663 excluding abstract, tables, figure captions and references.

---

## Abstract

Medicare's Hospital Insurance trust fund is projected to be depleted in 2033, but aggregate projections say little about how the cost of aging falls on households. We build a six-state continuous-time Markov model of later life (healthy, chronic illness, disability, severe disability at home, nursing home, dead) from 197,258 intervals between Health and Retirement Study interviews, 1998 to 2022, with deaths dated to the month, a linear spline in age, and standard errors clustered on the household. Medicare costs by state come from the Medicare Current Beneficiary Survey with the concentration of spending in the last year of life imposed; out-of-pocket costs are drawn from HRS core and exit interviews by state, age, sex, Medicaid status and income tertile, with persistence modeled as a permanent component plus an AR(1); Medicaid eligibility is reached by asset spend-down inside the simulation. Mortality is calibrated to the 2023 US life table. For a 65-year-old drawn from the population, the present value at 3% of lifetime Medicare spending is $154,423 for men and $171,804 for women, and of household out-of-pocket spending on care $35,329 and $43,666, with Part B and Part D premiums adding $32,195 and $33,977. The distribution is heavily skewed: the mean of the worst 5% of outcomes is $188,368 for men and $235,495 for women, 5.3 and 5.4 times the mean, and 71.8% and 85.7% of the lives in that tail pass through long-term care against 44.2% and 57.9% of all lives. 15.3% of men and 23.2% of women reach Medicaid, and among the lowest income tertile 37% and 45% do. Passing half of the post-2033 Part A shortfall to beneficiaries raises expected out-of-pocket cost by about $2,000; real cost growth at the Trustees' rate raises the worst-5% mean by $52,211 and $77,837. Code and a public calculator are released.

**Keywords.** multi-state model; interval-censored panel data; Medicare; long-term care; out-of-pocket spending; tail risk; Medicaid spend-down; microsimulation; Health and Retirement Study

---

## 1. Introduction

The 2026 Medicare Trustees Report projects that the Hospital Insurance (HI) trust fund will be depleted in the second quarter of 2033, after which incoming revenue would cover 89% of scheduled Part A benefits, and that Medicare spending will rise from 3.9% of GDP in 2025 to 6.5% in 2050 (Boards of Trustees, 2026). These are aggregates. They answer what the program will cost, not what aging costs a particular household, how uncertain that cost is, which health paths produce the bad outcomes, or who ends up on Medicaid. Those questions matter to the people who price long-term-care, Medigap and Medicare Advantage products, to planners advising retirees, and to policymakers choosing how a financing gap is closed.

The actuarial tool for the problem is the multi-state model: a person moves among health states with age-dependent intensities, each state carries a cost, expected present values follow from the transition probabilities, and the distribution follows from simulating paths. Multi-state models are standard in disability and long-term-care insurance (Haberman and Pitacco, 2018) and have been estimated on the Health and Retirement Study (HRS) for functional disability (Fong, Shao and Sherris, 2015; Sherris and Wei, 2021). Economists have separately measured medical-expense risk in retirement and its consequences for saving (Hubbard, Skinner and Zeldes, 1995; De Nardi, French and Jones, 2010; Jones et al., 2018). The strands rarely meet in one model that separates payers, separates care at home from care in an institution, reports the tail rather than the mean, and connects to Medicare's financing.

This paper builds that model from public data with released code. We ask five questions.

- RQ1. What are the transition intensities among healthy (H), chronic illness (C), disability (D), severe disability at home (L), nursing home (N) and death (X) for Americans aged 50 and over, and how do they vary with age, sex, education and race or ethnicity?
- RQ2. What are expected lifetime Medicare and household out-of-pocket costs from 65, by health state at 65, sex and income?
- RQ3. What is the distribution of the present value of lifetime out-of-pocket cost, what are its Value-at-Risk and Conditional Value-at-Risk, and which paths produce the tail?
- RQ4. Who exhausts their assets and reaches Medicaid, at what age, and how does that change the distribution of what households pay?
- RQ5. How would plausible responses to the post-2033 HI shortfall change household out-of-pocket risk?

Six design choices shape the answers, and each was made because the alternative changes the results.

*Care at home and care in an institution are different states.* Pooling them, as a five-state model does, mixes an annual out-of-pocket mean of about $3,800 with one of about $18,000 and hides the state that produces the tail.

*The likelihood is the exact interval-censored one.* Transitions between biennial interviews are not assumed away (Kalbfleisch and Lawless, 1985), intensities are piecewise constant over pieces of at most three years rather than held at an interval midpoint, and for a death dated to the month the death intensity is evaluated at the age at death.

*Age enters as a spline, not a single Gompertz slope.* Knots at 70 and 85 let the intensities bend, which a single log-linear slope cannot do over a 50-year age range.

*Standard errors are clustered on the household.* Spouses are both in the sample and their health and survival are correlated; the cluster-robust standard errors are a median 1.09 times the model ones.

*Costs are drawn from distributions, not means, and they persist.* Out-of-pocket draws are conditioned on state, age band, sex, Medicaid status and income tertile, with a permanent component and an AR(1) fitted to repeated HRS observations (French and Jones, 2004), and the last year of life is drawn from exit interviews, which core interviews never observe.

*Medicaid is endogenous.* A life whose assets fall below the eligibility limit while in long-term care becomes a Medicaid beneficiary inside the simulation, which is what actually stops the out-of-pocket spending of the people with the worst draws.

The main results follow. Life expectancy at 65 is 18.2 years for men and 20.7 for women, of which 1.4 and 2.3 are spent in long-term care. Expected lifetime Medicare spending varies little with health at 65 because poorer health shortens the years over which cost accrues, reproducing Lubitz et al. (2003) with a payer split and a modern panel. Out-of-pocket risk, by contrast, is concentrated: the worst 5% of outcomes average 5.3 and 5.4 times the mean, the tail is made of long-term-care paths, and it is truncated for the poorest households only because Medicaid takes over. A partial pass-through of the HI shortfall moves the expected household cost by about 6%, small beside the effect of the long-run cost trend, which falls mostly on the tail.

## 2. Background

**Medical-expense risk in retirement.** Uncertain medical costs affect saving and decumulation (Hubbard, Skinner and Zeldes, 1995; Palumbo, 1999), and De Nardi, French and Jones (2010) showed that expenses rising with age and income help explain why the elderly run assets down slowly. French and Jones (2004) showed that out-of-pocket costs are persistent, with a permanent component and a highly autocorrelated transitory one, which is the structure used here. De Nardi et al. (2016) documented the medical spending of the US elderly by payer, and Jones et al. (2018) estimated lifetime medical spending of retirees from a structural model. End-of-life spending has been measured from HRS exit interviews (Marshall, McGarry and Skinner, 2011; Kelley et al., 2013) and is highest for people with dementia (Kelley et al., 2015; Hurd et al., 2013). Fahle, McGarry and Skinner (2016) examine what HRS out-of-pocket measures do and do not capture. Hurd, Michaud and Rohwedder (2017) showed that lifetime nursing-home use and its out-of-pocket cost are concentrated in a minority, and Kemper, Komisar and Alecxih (2005) gave the standard lifetime estimates of long-term-care use. Poterba, Venti and Wise (2011) documented how little wealth many households hold late in life, which is why an asset-based spend-down rule matters. Medicaid's role as payer of last resort shapes the private long-term-care market (Brown and Finkelstein, 2008), its means test shapes saving (Braun, Kopecky and Koreshkova, 2017), and preferences over long-term care shape late-life saving (Ameriks et al., 2020).

**Health paths and cumulative spending.** Lubitz et al. (2003) found that older people in better health live longer and accumulate similar lifetime Medicare spending. Riley and Lubitz (2010) measured the share of Medicare spending that falls in the last year of life, about a quarter, which this paper imposes rather than assumes away. Multi-state health expectancies go back to Crimmins, Hayward and Saito (1994), and microsimulation of the future elderly to the Future Elderly Model (Goldman et al., 2005).

**Actuarial multi-state models.** Haberman and Pitacco (2018) set out the framework for disability and long-term-care insurance. Fong, Shao and Sherris (2015) estimated multi-state models of functional disability from HRS; Shao, Sherris and Fong (2017) priced long-term-care insurance with one; Li, Shao and Sherris (2017) and Sherris and Wei (2021) added systematic trend and uncertainty.

**Estimation from panel data.** When states are seen only at interviews, the likelihood is built from transition probabilities over observed intervals (Kalbfleisch and Lawless, 1985), as in the msm package (Jackson, 2011) and treated at length by van den Hout (2016). Titman and Sharples (2010) review diagnostics, and Aguirre-Hernández and Farewell (2002) give the observed-against-expected test used in Section 5. Putter, Fiocco and Geskus (2007) and de Wreede, Fiocco and Putter (2011) cover the exactly observed case.

**What this paper adds.** A six-state model that separates severe disability at home from nursing-home residence, estimated on interval-censored HRS data with a spline in age and household-clustered standard errors; payer-specific costs with the end-of-life concentration imposed and persistence modeled; Medicaid spend-down inside the simulation; tail measures (Rockafellar and Uryasev, 2000); scenarios tied to the Trustees' financing projections; and the whole pipeline, with a public calculator, released.

## 3. Data

**HRS panel.** We use the RAND HRS Longitudinal File 2022 (V1) (Bugliari et al., 2025; Sonnega et al., 2014), waves 4 to 16 (1998 to 2022), respondents aged 50 and over. Each interview is assigned a state:

- H: no ever-diagnosed condition among eight (hypertension, diabetes, cancer, lung disease, heart problems, stroke, psychiatric problems, arthritis) and no limitation in the five RAND activities of daily living (ADL);
- C: at least one condition and no ADL limitation;
- D: one or two ADL limitations, living in the community;
- L: three or more ADL limitations, living in the community;
- N: living in a nursing home at interview, whatever the ADL count;
- X: dead, dated to the month from the RAND death date.

The panel has 40,354 respondents and 237,944 classified person-interviews (Table 1). Consecutive interviews give 197,258 transitions with a mean interval of 2.14 years; 16,160 deaths are dated, 139 of them to the year only and placed at mid-year; 8,548 observations are censored at the last interview at which the person was known to be alive, contributing 39,761 person-years; 375 observations are dropped for missing race. Weighted, 16.3% of person-interviews are in H, 67.5% in C, 10.6% in D, 4.0% in L and 1.6% in N. Crude transition counts are in Table A2. Because conditions are ever diagnosed, C to H cannot occur and is not modeled.

**Out-of-pocket spending.** Core interviews report out-of-pocket medical spending over the previous two years, excluding premiums, with RAND imputations. We halve it to an annual figure, express it in 2024 dollars with the CPI-U, and attach it to the state at that interview. Draws are taken from waves 8 onward (2006 and later) so that every draw is from a year in which Part D existed. The exit interview, answered by a proxy after death, reports spending from the last core interview to death; 9,965 decedents aged 65 and over contribute, and the last-year amount is that spending scaled by min(1, 12/months). Table 4b reports these distributions and Table 4e the persistence they show.

**Medicare spending.** The MCBS Cost Supplement public use files for 2019 and 2021 to 2023 (29,144 beneficiary-years) give annual spending by payer, with Medicare Advantage payments included, in cells of age by count of chronic conditions (0-1, 2-3, 4+). Standard errors use balanced repeated replication with Fay's adjustment of 0.30. The pooled Medicare mean is $11,802 (standard error $278) and 44% of beneficiary-years are in Medicare Advantage (Table A7).

**Other sources.** Mortality benchmarks are the 2023 US period life tables (Arias and Xu, 2025). HI depletion timing, the payable share and cost growth are from the 2026 Trustees Report. The standard Part B premium is $174.70 a month in 2024 and the Part D base premium $34.70 (CMS, 2023).

## 4. Model

### 4.1 Transition intensities

Let $S = \{H, C, D, L, N, X\}$ and let $q_{jk}(x, z)$ be the intensity of moving from $j$ to $k$ at age $x$ for covariates $z$. Eighteen transitions are allowed (Figure 1): H to C, D, X; C to D, L, N, X; D to H, C, L, N, X; L to D, N, X; N to D, L, X. Transitions without their own intensity, such as H to N, are reached through intervening states within an interval, which is what a continuous-time model does with interval-censored data. Each intensity is log-linear in a linear spline in age,

$$\log q_{jk}(x, z) = \beta_{0,jk} + \beta_{1,jk}\frac{x - 65}{10} + \beta_{2,jk}\frac{(x-70)_+}{10} + \beta_{3,jk}\frac{(x-85)_+}{10} + \gamma_{jk}^{\top}z,$$

with $z$ = (female, any college, nonwhite or Hispanic). The intensity matrix $Q(x, z)$ has off-diagonal entries $q_{jk}$ and rows summing to zero.

![Figure 1. State space and allowed transitions.](output/figures/fig_state_diagram.png)

An interval of length $d$ from age $x$ is split into pieces of at most three years; over each piece $Q$ is held at the piece's midpoint age, and the transition matrix is the product of the pieces' matrix exponentials. For a person seen in state $r$ at age $x$ and in state $s$ after $d$ years, the likelihood contribution is $P_{rs}(x, x+d)$. For a death at $d$ years after the last interview in state $r$, the state just before death is unobserved and the contribution is

$$\sum_{k \neq X} P_{rk}(x, x+d)\, q_{kX}(x + d, z),$$

with the death intensity evaluated at the age at death rather than at the midpoint. For a person last seen alive at age $x + d$ the contribution is $\sum_{k \neq X} P_{rk}(x, x+d)$, which uses the information that the person did not die without asserting a state.

The log likelihood is maximized with gradients from automatic differentiation through the matrix exponential. Standard errors come from a sandwich estimator with scores clustered on the household. Estimation is unweighted, the usual convention for panel multi-state models, with the covariates carrying composition; weighted prevalence is used for validation.

### 4.2 Entry population and mortality calibration

A simulated 65-year-old is drawn from the weighted joint distribution of state, education, race or ethnicity, household income tertile, non-housing assets and Medicaid enrollment among HRS respondents aged 64 to 66. The entry mix is 14.7% H, 73.5% C, 8.9% D, 2.4% L and 0.5% N for men, and 14.4%, 72.3%, 9.2%, 3.5% and 0.5% for women.

The fitted model pools deaths from 1998 to 2022, and its life expectancy at 65 is 17.49 years for men and 20.35 for women against 18.19 and 20.71 in the 2023 table. Rather than change the relative mortality of the states, which the data identify, we scale every death intensity by $\lambda(x) = \exp\{c_0 + c_1 (x-65)/10\}$ by sex, choosing $(c_0, c_1)$ to minimize the $l_x$-weighted squared difference in $\log q_x$ between model and table at ages 65 to 99. The multiplier runs from 0.865 at 65 to 0.928 at 95 for men and from 0.831 to 1.064 for women (Table 3b). The uncalibrated model is kept as a robustness variant.

### 4.3 Costs

**Medicare.** Medicare cost in state $j$ and age band $b$ (65-74, 75 and over) is the MCBS cell mean for band $b$ averaged over the distribution of chronic-condition counts among HRS respondents in $j$ and $b$. The HRS counts eight conditions and the MCBS a longer list, so this bridge places HRS respondents in lighter cells than the population they represent; we keep the state relativities and scale the level in each band so that the weighted cohort average equals the MCBS band mean, factors of 1.16 and 1.14 (Table A5). Spending is concentrated at the end of life: we set the ratio of a decedent's Medicare cost to a survivor's so that the last year of life takes 25.1% of the cohort's Medicare spending, the share reported by Riley and Lubitz (2010), holding the overall level fixed. That implies a decedent multiplier of 5.44 and a rescaling of survivor costs to 0.795. Medicare spending is 17% higher in the lowest income tertile, the MCBS relativity.

**Out-of-pocket.** Out-of-pocket cost in a year alive is drawn from the weighted empirical HRS distribution for the state, age band, sex, Medicaid status and income tertile, with a minimum cell size of 150 observations and coarser cells used where that is not met. Draws are persistent: a life carries a standard normal factor with a permanent share of 0.367 and an AR(1) coefficient of 0.463 on the transitory part, both estimated from repeated HRS observations of the same person, and the year's draw is the quantile of its cell at the implied uniform. In the year of death the draw is replaced by one from the exit-interview distribution for the age band and sex, conditioned on whether the person was in long-term care at the last interview. Premiums for Part B and Part D are added for each year alive outside Medicaid and reported separately.

**Medicaid.** A life enters with the Medicaid status and non-housing assets of its HRS cell. In each year, income meets up to 10% of the out-of-pocket cost and the rest draws on assets; a life in L or N whose assets fall below $2,000 becomes eligible, after which Medicaid pays for long-term care, out-of-pocket draws come from the Medicaid cells and premiums stop. This is an exposure rule, not an eligibility determination: it ignores spousal protections, home equity, look-back rules and state variation.

### 4.4 Lifetime cost, its distribution and the tail

Lives step through one-year transition matrices from 65 to 110. With costs accruing at the start of each year and a discount factor $v = 1/1.03$, the present value of out-of-pocket cost is the discounted sum of the yearly draws, with the end-of-life draw replacing the ordinary one in the year of death, and $PV^{M}$ and the premium defined the same way. Tail risk is summarized by $\mathrm{VaR}_\alpha$, the $\alpha$ quantile of $PV^{O}$, and $\mathrm{CVaR}_\alpha = \mathbb{E}[PV^{O} \mid PV^{O} \ge \mathrm{VaR}_\alpha]$ at $\alpha = 0.90, 0.95, 0.99$ (Rockafellar and Uryasev, 2000). We simulate 100,000 lives for each sex and each state at 65, and 100,000 from the population mix, with common random numbers across scenarios so that differences are not simulation noise. Monte Carlo standard errors are reported for every mean and tail measure.

Expected values are also computed exactly, by forward recursion over the state distribution with spend-down and persistence switched off, cell by cell over income tertile and Medicaid status so that the recursion prices the same cost cells the simulation draws from (Table 5c). Parameter uncertainty is the spread of those exact values over 200 draws of the intensity parameters from their asymptotic distribution.

### 4.5 Financing scenarios

Scenarios apply to a cohort turning 65 in 2026, so calendar year is 2026 plus years since 65. Part A's share of a state's Medicare cost is the MCBS inpatient-plus-home-health share within each chronic-condition cell, and the HI share of total Medicare benefits, 35.1% in the 2024 Trustees tables, sets the size of the shortfall.

- S0: benefits paid in full, the Trustees' convention.
- S1: from 2033 Part A pays the projected payable share (89% in 2033, 85% in 2050, 93% in 2100, interpolated between), and a share $s$ of the shortfall becomes household cost, for $s$ = 0, 25%, 50% and 100%.
- S1b: the same with Part A's share taken as the community inpatient-plus-home-health share of 26%, a narrower definition.
- S2: the whole cohort shortfall falls on person-years in long-term care, as a cut to post-acute coverage would.
- S3: S1 with $s$ = 50% plus real cost growth at the Trustees' per-beneficiary rate of 1.7% a year.

## 5. Validation

**Goodness of fit.** Table 3 compares observed and expected destination distributions by starting state, age group and interval length, excluding censored rows, in the form of Aguirre-Hernández and Farewell (2002). The fit is close from H (largest gap 0.3 points), C (0.8) and D (3.1). It is poor from the two long-term-care states: from L the model expects 47.0% to remain against 39.8% observed and 20.5% to die against 25.8%; from N it expects 56.5% to remain against 41.2% and 36.6% to die against 50.6%, a gap of 15.2 points. The consequence for this paper is that years in N are overstated and deaths from N understated, so lifetime nursing-home cost is, if anything, overstated and time in that state too long. Section 6.9 tests the obvious explanation, duration in state, and rejects it for mortality: the duration proxy transforms the fit of movements between live states but leaves the death intensity from the nursing home unchanged. What is left is unobserved heterogeneity among residents, which a model with one hazard per state and age cannot represent.

**Mortality.** After calibration, life expectancy at 65 is 18.23 years for men and 20.74 for women against 18.19 and 20.71 in the table, and one-year death probabilities are within 6% of the table at every age from 65 to 95 (ratios 0.92 to 1.05; Table 3b, with the life table in Table A8).

**Prevalence.** The calibrated model's state distribution among survivors is compared with the weighted HRS cross-section by sex and age band (Table A4 and Figure 2). The largest gap in any cell is 3.1 percentage points, and gaps exceed 2 points only above age 85, where the model holds slightly too few people in H and slightly too many in N.

![Figure 2. State prevalence by age: weighted HRS cross-section (solid) and calibrated model (dashed).](output/figures/fig_prevalence.png)

**Spending.** After the level scaling, the cohort's Medicare spending per person-year is 1.00 and 1.01 times the MCBS band mean (Table A5). It is 0.56 and 0.70 of Medicare's own per-beneficiary spending in 2024 ($17,837), which is expected: the Trustees' figure covers all beneficiaries including those under 65 on disability, and includes Part D and the institutional and hospice spending the Cost Supplement omits.

**Medicaid.** In the model, 23.5% of men's and 31.0% of women's long-term-care person-years are on Medicaid, against 30.5% in HRS (Table A5). The model therefore under-covers men, whose spend-down is slower because they reach long-term care later and die sooner.

**Published estimates.** Table 8 sets the model against four published studies, with each figure converted to 2024 dollars. Two comparisons are close: out-of-pocket spending in the last five years of life, $35,182 for men and $42,826 for women against Kelley et al. (2013) at $56,368 for a pooled sample that includes premiums, and last-year spending of $10,386 and $12,568 against Marshall, McGarry and Skinner (2011) at $16,927, with the model's 95th percentile ($53,447 and $67,837) bracketing theirs ($72,714). Two are not. Jones et al. (2018) report lifetime medical spending from 70 of $161,662 per household including Medicaid payments, against $33,235 and $42,298 here for one person's own out-of-pocket spending, a different object. And Hurd, Michaud and Rohwedder (2017) report that 56% of people have a nursing-home stay, against 19% of men and 30% of women here; their measure counts any stay, including the short post-acute stays that a biennial interview cannot see, while the state N here means residence at interview. Kemper, Komisar and Alecxih (2005) put lifetime nursing-home use nearer 35%. The model's N state should be read as long nursing-home residence, not as any admission.

## 6. Results

### 6.1 Transitions (RQ1)

Table 2 reports the intensities as hazard ratios. The likelihood-ratio test for the education and race-ethnicity terms is 1,756.2 on 36 degrees of freedom. Cluster-robust standard errors are a median 1.09 times the model ones across the 126 parameters, with a range of 0.23 to 1.43, so treating spouses as independent would overstate precision for most parameters.

Death intensities rise with age from every state, by a factor of 2.59 per decade from H, 1.75 from C, 2.32 from D, 1.87 from L and 1.72 from N, the flattening expected when frailer people leave the at-risk group first. Women's death intensities are 0.42 to 0.67 of men's, with the largest difference from H. Any college lowers mortality from H (hazard ratio 0.47) and C (0.78) and lowers the intensity of moving from C to D (0.72). Being nonwhite or Hispanic raises the intensity from H to D (1.73) and from C to D (1.32) while lowering mortality from D (0.74) and from N (0.93), the pattern expected when a group enters a state at lower average severity.

Two features of the fit need stating. First, the optimizer for the full model stopped at its iteration limit rather than on its own convergence test; at the reported solution the largest absolute gradient component is 0.023 on a log likelihood of 166,665, with all but two components below 0.001 and no parameter at a bound, so the solution is a maximum for practical purposes. Second, the covariate effects on the direct C to L intensity are not identified: only 2,149 of the 197,258 observed transitions end in L from C, most severe disability is reached through D, and the model standard errors on that intensity's intercept and race term are 6.6 and 6.5 on the log scale. The hazard ratios in that row of Table 2 should not be interpreted; the aggregate flow into L is identified, as the goodness-of-fit table for starting state C shows (1.51% observed against 1.51% expected).

One-year transition probabilities at ages 65, 75 and 85 are in Table A3 and the death probabilities in Figure 3.

![Figure 3. One-year probability of death by state at ages 65, 75 and 85, fitted model, reference covariates.](output/figures/fig_transitions.png)

### 6.2 Health expectancies

A 65-year-old man with no college and not nonwhite, healthy at 65, can expect 18.30 more years: 6.60 in H, 8.94 in C, 1.76 in D, 0.57 in L and 0.43 in N (Table A6 and Figure 4). The equivalent woman can expect 21.17 years, with 0.90 in L and 0.98 in N. Starting in chronic illness costs about two years, starting in D about four and a half, starting in L seven, and starting in N nearly twelve: a man in a nursing home at 65 can expect 6.42 more years, 3.05 of them in the nursing home. Women spend about twice as many years as men in the two long-term-care states from every starting point, which is the main reason their lifetime out-of-pocket cost is higher.

![Figure 4. Expected years in each state from 65, by health state at 65.](output/figures/fig_health_expectancy.png)

### 6.3 Annual costs by state

Medicare spending per year rises with disability and is nearly flat between the two long-term-care states: at 65 to 74 it runs from $5,127 in H through $9,940 in C, $12,678 in D and $13,998 in L to $14,129 in N, and at 75 and over from $6,815 to $14,293 (Table 4). Out-of-pocket spending is where the states differ most, and where separating home from institution matters. At 75 and over the mean is about $1,200 in H, $2,020 in C, $2,800 to $2,900 in D and $3,600 to $4,000 in L, but $16,387 for men and $19,047 for women in N, with 99th percentiles of $135,957 and $157,817 (Table 4b). Medicaid covers 35% and 40% of nursing-home person-years at those ages and 15% and 25% of severe disability at home, which is why the N distribution has a long right tail rather than a high median (Table 4c).

Out-of-pocket spending in the last year of life depends on where the person was: for decedents aged 75 and over who were in long-term care at the last interview it averages $16,607 for men and $17,751 for women, against $7,536 and $8,378 for the others (Table 4d).

### 6.4 Expected lifetime cost (RQ2)

Table 5 gives expected lifetime costs from 65 at a 3% discount rate. For the population mix the present value of Medicare spending is $154,423 for men and $171,804 for women; of household out-of-pocket spending on care, $35,329 and $43,666 with medians of $20,520 and $25,125; and of Part B and Part D premiums, $32,195 and $33,977. Households therefore face about $67,500 and $77,600 in present value in total, of which just under half is premiums. Monte Carlo standard errors are $147 and $187 on the out-of-pocket means, and the parameter-uncertainty intervals from 200 draws of the intensities span about 2% of the mean (Table 5).

Health at 65 changes expected lifetime Medicare cost much less than it changes annual cost. A man healthy at 65 is expected to cost Medicare $139,934 over his life; one already in a nursing home, whose annual cost is nearly three times as high, is expected to cost $125,828, because he is expected to live 8.4 years rather than 20.4. The highest expected Medicare cost is for people with chronic illness and no limitation at 65, $157,383 for men and $174,647 for women, who combine long lives with high annual cost.

Expected out-of-pocket cost behaves differently again, and not monotonically in health. It is $34,484 for a man healthy at 65, $35,727 with chronic illness, $32,300 with disability, $26,780 in severe disability at home and $40,213 in a nursing home. Two forces offset: worse health at 65 means more long-term-care years, which cost more, but also shorter life and a far higher chance of reaching Medicaid, which stops household spending. For men starting in L, 56.3% reach Medicaid; starting in N, 68.8%. The premium column falls monotonically with worse health at 65, from $36,431 to $6,937, because premiums are paid for years alive outside Medicaid.

### 6.5 Income (RQ2)

Income changes the composition of the cost more than its total (Table 5b). Men in the lowest tertile of household income have median non-housing assets of $7,970 at 65, are in long-term care at entry three times as often as the highest tertile, and reach Medicaid at some point in 37% of lives against 4%. Their expected lifetime out-of-pocket cost is $29,154 against $39,257 in the highest tertile, and for women $36,436 against $52,254. The poorest households pay less not because they use less care but because Medicaid pays once their assets are gone, while their expected Medicare cost is the highest of the three groups ($170,053 for men against $149,496), reflecting both the MCBS income relativity and more time in long-term care.

### 6.6 The tail (RQ3)

Figure 5 shows the distribution of lifetime out-of-pocket cost for the population mix. For men, VaR95 is $119,688 and CVaR95 $188,368, 5.3 times the mean, with a Monte Carlo standard error of $1,433; CVaR99 is $311,744. For women, VaR95 is $147,062, CVaR95 $235,495, 5.4 times the mean, and CVaR99 $407,630 (Table 6).

![Figure 5. Distribution of the present value of lifetime out-of-pocket cost from 65, population mix, with Value-at-Risk at 90%, 95% and 99%.](output/figures/fig_lifetime_oop.png)

The tail is a long-term-care phenomenon. Among men in the worst 5% of outcomes, 71.8% passed through long-term care against 44.2% of all men, and they spent 3.1 years there against 1.4; for women, 85.7% against 57.9%, and 5.0 years against 2.3. People in the tail live longer, dying at 87.4 on average against 83.2 for all men, because a long stay in care requires surviving to have it. The end-of-life draw accounts for 12.5% of the tail's present value for men and 8.3% for women. 34% of the men and 45% of the women in the tail reach Medicaid, which is what stops their costs; without a spend-down rule the tail would be longer and the poorest lives would carry impossible amounts.

Starting state matters much more for the tail than for the mean. A man in a nursing home at 65 has an expected out-of-pocket cost only 14% above the population mix but a CVaR95 of $292,873 against $188,368; for women the figures are $380,546 against $235,495 (Figure 6).

![Figure 6. Expected lifetime out-of-pocket cost and CVaR95 by health state at 65.](output/figures/fig_entry_states.png)

### 6.7 Medicaid, spend-down and financing scenarios (RQ4, RQ5)

15.3% of men and 23.2% of women reach Medicaid at some point after 65, at a median age of 68 and 70 (Table 5). In the lowest income tertile, 21% of men and 24% of women are already enrolled at 65 and a further 16% and 22% spend down to it, at a median age of 82 and 83; in the middle tertile 8% and 11% spend down; in the highest, 3% and 4% (Table 7b). 25% of the lowest tertile has no positive non-housing assets at 65 at all.

Table 7 and Figure 7 report the financing scenarios. A pure provider payment cut (S1 at 0%) leaves household cost unchanged by construction; its effect would come through access, which this model does not capture. Passing a quarter of the Part A shortfall to households raises expected lifetime out-of-pocket cost by $1,002 for men and $1,104 for women; half raises it by $2,003 and $2,208; the whole shortfall by $4,003 and $4,414. On the narrower community definition of Part A's share (S1b) the effect at 50% is $1,481 and $1,634. Concentrating the shortfall on long-term-care years (S2) produces a similar mean change, $2,081 and $2,782, but more than twice the tail effect: CVaR95 rises by $4,713 and $6,093 against $2,428 and $2,531 when the shortfall is spread. Real cost growth at the Trustees' rate with half the shortfall shifted (S3) raises the mean by $10,352 and $14,229 and CVaR95 by $52,211 and $77,837, an order of magnitude more than the shortfall itself. Spend-down rises by at most 2 percentage points in any scenario, because the households most exposed to a Part A cut are those already closest to Medicaid.

![Figure 7. Change in the mean and in CVaR95 of lifetime out-of-pocket cost under the financing scenarios.](output/figures/fig_scenarios.png)

### 6.8 Robustness

Table 9 reports variants, each changing one decision, with 40,000 lives per sex, so its baseline row differs from Table 5 by simulation error (men's out-of-pocket mean $35,058 against $35,329). Three groups of variants matter.

**How costs are modeled.** The single largest effect in the whole paper is the persistence of out-of-pocket draws. With independent draws, the specification most cost models use, men's CVaR95 falls from $185,746 to $119,229 and women's from $234,519 to $158,542, while the means barely move ($35,067 and $44,130). A model that draws costs independently each year understates the tail by about a third, because the people who draw badly once draw badly again. Dropping the end-of-life step lowers CVaR95 to $167,370 and $219,115, so the last year of life carries about a tenth of the tail; making the end-of-life draw independent of the state at the last interview lowers it by 2%. Drawing out-of-pocket costs from all waves rather than from 2006 onward raises the mean to $37,233 and $47,470 and CVaR95 to $206,564 and $265,687, because pre-Part D years carry heavier drug spending; the restriction is the conservative choice.

**How Medicare's level is set.** The level of lifetime Medicare spending is the least settled number here. Without the scaling to MCBS band means it is $134,608 for men; with it, $154,778; using fee-for-service spending only, $149,507; raising the whole level to Medicare's own per-beneficiary spending in 2024 would give $246,855. A 25% uplift for the facility and hospice events the Cost Supplement omits gives $166,176, and the functional cost gradient variant $159,704. None of these changes household out-of-pocket cost, which is drawn from HRS; the Medicare column should be read as a well-anchored relativity across states with a level that is uncertain by roughly a fifth.

**Mortality, discounting and the Medicaid rule.** Without calibration, life expectancy at 65 falls to 17.6 years for men and CVaR95 to $179,906; calibrating on the H and C states only changes nothing material. Mortality improvement of 1% a year, which a cohort turning 65 in 2026 will plausibly see, raises life expectancy to 19.2 and 21.8 years, the share ever in long-term care to 49% and 63%, and CVaR95 to $199,785 and $257,055: longevity is a risk factor for out-of-pocket cost. Discounting at 2% instead of 3% raises men's CVaR95 to $213,025 and at 4% lowers it to $163,868. Turning spend-down off cuts the share ever on Medicaid from 15% and 23% to 6% and 9% and raises CVaR95 to $193,566 and $251,851; requiring income to meet none of the out-of-pocket cost raises the Medicaid share to 19% and 29%; a $10,000 asset limit raises it to 17% and 26%. The Medicaid rule therefore moves who pays much more than it moves the total. Replacing the full covariate model with the sex-only model raises the share ever in long-term care to 47% and 61% and CVaR95 to $191,226 and $246,060.

**Refitting the state definition.** One variant re-estimates the transition model rather than re-simulating it: folding nursing-home residence back into severe disability at home, which is the five-state definition this paper argues against. Because refits carry sex alone, the comparison is with the sex-only model. Pooling gives $36,104 and $44,809 with CVaR95 $199,397 and $247,942, against $35,760 and $45,178 with $191,226 and $246,060, and leaves the share ever in long-term care at 46% and 61%, as it must, since that share is the union of the two states either way. The case for separating them is therefore not that pooling moves the headline totals, which it does by about 1% in the mean and 4% in men's tail, but that pooling hides where the money goes: a state with annual out-of-pocket cost of about $4,000 and one with about $18,000, with Medicaid covering a quarter of the first and two-fifths of the second, are not one state.

Four further refits change the definition of long-term-care need, the sample period or the likelihood. Lowering the threshold for long-term care to two ADL limitations raises the share of lives ever in long-term care from 47% and 61% to 58% and 71%, and counting dementia (a 27-point cognition score of 6 or less, or a reported diagnosis, carried forward once observed because the score is missing in 2022 and the diagnosis items begin in 2010) raises it to 57% and 69%. Neither moves the money much: out-of-pocket means of $35,599 and $44,382 at two ADLs and $35,489 and $45,302 with dementia, with CVaR95 of $191,305 and $240,045, and $188,082 and $251,586. A wider definition brings people with lighter needs into the state, so the share rises while the cost per person in it falls. Restricting estimation to waves 9 to 16 (2008 to 2022) lowers the tail to $183,424 and $232,429, 4% and 6% below the sex-only row, consistent with the declining disability and nursing-home entry the period extension in Section 6.9 finds. Weighting the likelihood by the respondent weights gives $35,274 and $44,275 with CVaR95 $187,408 and $240,359, within 2% of the unweighted means. Across the five refits, out-of-pocket means stay within 6% and CVaR95 within 6% of the sex-only model, against a Monte Carlo standard error of about $2,400 on CVaR95. The optimizer for the two-ADL refit stopped at its evaluation limit; restarting it from a different point and allowing four times as many iterations returned the same log likelihood (−170,892.7) and the same headline figures to within $20, so the reported values are at the maximum.

### 6.9 Extensions to the transition model

Table A1 reports extensions that add a term to every one of the 18 intensities of the full model and test it by likelihood ratio. Each starts from the main model's estimates with the new terms at zero, and the table records whether the optimizer converged. Three are reported. A fourth, a quadratic in age on top of the spline, is not: the first attempt built the term from age at the interval midpoint, which for a death row carries the date of death, and the re-estimation with age at the start of the interval had not converged after 29 hours and was stopped. The spline already lets the intensities bend at 70 and 85, so little rests on it.

**Income.** Adding indicators for the lowest and highest tertile of household income improves the likelihood by 1,789.7 on 36 degrees of freedom. Low income raises the intensity of moving from H to D (hazard ratio 1.72), from C to D (1.43), from C to a nursing home (1.66) and from C to death (1.41); high income lowers the last two to 1.19 and 0.73. The effect on life expectancy is large: starting from chronic illness at 65, a man in the lowest tertile can expect 13.9 years and one in the highest 18.6, and a woman 17.5 against 22.2. The main model has no income term, so its income results in Section 6.5 carry differences in composition, costs and Medicaid but not in health dynamics, and the 2-year gap in life expectancy they show is less than half of the 4.7 years this extension implies.

**Duration.** Adding an indicator for having been in the same state at the previous interview, a coarse proxy for duration in state, improves the likelihood by 3,046.3 on 18 degrees of freedom, the largest improvement of any extension tried. Movements between live states are strongly duration-dependent in the expected direction: for someone already in the state two years earlier, the intensity of moving from C to D is 0.41 of the intensity for a recent entrant, from D back to C 0.48, from L to D 0.41 and from a nursing home back to D 0.22. Transitions happen soon after a change, and a Markov model spreads them evenly.

Mortality is the exception, and it matters for Section 5. The death intensity from the nursing home is unchanged by the duration proxy (hazard ratio 1.03, interval 0.95 to 1.12), as is the death intensity from severe disability at home (1.00) and from disability (0.98). The model's failure to fit deaths from the nursing home is therefore not duration dependence in mortality. The more likely explanation is unobserved heterogeneity: nursing-home residents differ in frailty in ways the six states and three covariates do not capture, so the observed group dies faster than a common hazard predicts. A frailty or semi-Markov specification is the next step, and it is a different model rather than another term in this one.

**Calendar time.** Adding a linear term in interview year, per decade from 2010, improves the likelihood by 354.8 on 18 degrees of freedom: far less than income or duration, but not negligible. The trend is toward less institutional care. Per decade, the intensity of entering a nursing home falls to 0.70 of its level from chronic illness, 0.70 from disability and 0.67 from severe disability at home, and the intensity of dying from chronic illness falls to 0.87. Recovery from disability to health also falls, to 0.50, and deaths from disability and from the nursing home become slightly more likely (1.13 and 1.07), consistent with people reaching those states later and in worse health. Starting from chronic illness at 65, life expectancy rises from 15.8 years in 1998 to 17.0 in 2022 for men and from 18.8 to 19.9 for women. The main model pools the period, so it describes the average of 1998 to 2022. Calibration to the 2023 life table corrects the level of mortality but not the decline in nursing-home entry, so for a cohort turning 65 now the model's nursing-home use is, if anything, too high; the waves 9 to 16 refit in Section 6.8, with a tail 4% to 6% lower, points the same way.

## 7. Discussion

**For Medicare policy.** How the HI gap is closed matters far less to the average household than the rate at which costs grow, and matters most to the few who need long-term care. A cut that falls on post-acute and long-term-care services doubles the tail effect of the same aggregate shortfall. The people at the front of that queue are also those closest to Medicaid, so a shortfall passed to households is partly a shortfall passed to state Medicaid programs, which this model makes visible by letting eligibility be reached rather than assumed.

**For insurers and planners.** Expected lifetime out-of-pocket cost is nearly flat across health states at 65, but the tail is not, and the two long-term-care states drive it. Products that cover long nursing-home stays or the last year of life address exactly the part of the distribution that saving cannot cover, and the model's state intensities, calibrated to current mortality and reported with household-clustered standard errors, can be used in pricing and reserving with the covariate structure of Table 2. The flatness of lifetime Medicare cost across entry states supports Lubitz et al. (2003) on a newer panel with a payer split.

**For households.** A 65-year-old should expect a present value of out-of-pocket care costs near $35,000 (men) or $44,000 (women) plus about $33,000 of premiums, but should plan for a small chance of five times that. For households in the lowest income tertile, the realistic bad case is not a large bill; it is spending down to Medicaid in the early eighties.

**Questions a reader will ask.** *Why does expected out-of-pocket cost fall for people who start in worse health?* Because Medicaid takes over for many of them and because they live fewer years; the tail, not the mean, is where their risk shows. *Does the nursing-home misfit invalidate the results?* It biases years in N upward and deaths from N downward, so lifetime nursing-home cost is overstated rather than understated. Section 6.9 shows the cause is not duration in state, which leaves nursing-home mortality unchanged, but heterogeneity the model does not observe. *Why is the model's nursing-home use so far below published lifetime figures?* Because a biennial interview sees residence, not admissions; the state should be read as long residence. *Why not weight the likelihood?* Panel multi-state models are conventionally fitted unweighted with composition carried by covariates; a weighted-likelihood variant is reported in Section 6.8. *Why is Medicaid modeled by assets alone?* Because HRS gives assets and income but not the state-specific eligibility tests; the rule is an exposure measure, and the validation against HRS long-term-care person-years on Medicaid shows it lands close for women and low for men.

**Limitations.** Six matter most. First, the model is Markov in age and homogeneous within a state: movements between live states are strongly duration-dependent (Section 6.9), and deaths from the nursing home are underpredicted by an amount that duration does not explain, which points to frailty the model does not observe. Second, the MCBS Cost Supplement excludes facility, hospice and institutional events, so Medicare cost in the long-term-care states is understated even after scaling, and the Part A share omits skilled nursing. Third, out-of-pocket draws come from HRS self-reports, which are known to understate some categories and to be measured with error (Fahle, McGarry and Skinner, 2016); the comparison with published end-of-life estimates suggests the level here is low by roughly a third. Fourth, the spend-down rule ignores spousal protections, home equity, look-back rules and state variation, and the model has no spouse: every life is simulated alone. Fifth, the main model has no calendar trend: Section 6.9 finds nursing-home entry falling by about 30% a decade while life expectancy rises, so the pooled model overstates institutional use for a cohort turning 65 in 2026 while calibration to a period table understates its longevity, and there is no trend in long-term-care prices. Sixth, the main transition model has no income term; the extension in Section 6.9 shows that the income results of Section 6.5, which carry composition and costs but not differential health dynamics, understate the gap between tertiles. Linked HRS-Medicare claims would address the second and third and are the natural next step.

## 8. Conclusion

A six-state model fitted to 24 years of HRS panel data, calibrated to current mortality, linked to payer-specific costs and allowed to reach Medicaid through spend-down shows that the expected lifetime cost of aging varies little with health at 65 while its tail varies enormously; that the tail is made of long nursing-home stays and the last year of life, and is truncated for poorer households only by Medicaid; and that a partial pass-through of Medicare's Part A shortfall matters far less to households than the long-run growth of costs, unless the shortfall is concentrated on long-term care, in which case it hits precisely the households already at risk. The released code rebuilds every number, and the calculator puts the results in front of the people who carry the risk.

---

## Declarations

**Data availability.** The RAND HRS Longitudinal File and HRS exit data are available to registered users from the Health and Retirement Study; the MCBS Cost Supplement public use files from the Centers for Medicare & Medicaid Services; the life tables and Trustees Report are public. None is redistributed, and no microdata is included in the repository or the calculator. The HRS is sponsored by the National Institute on Aging (grant numbers NIA U01AG009740 and NIA R01AG073289) and is conducted by the University of Michigan.

**Code availability.** The seeded pipeline is at https://github.com/tosin-babs/medicare-cost-of-aging; `python/run_all.py` rebuilds every table and figure and `pytest tests` runs the checks. The public calculator is at https://medicare-cost-of-aging.vercel.app.

**Competing interests.** None declared.

**Ethics.** The analysis uses de-identified public-use survey data and did not require ethical approval.


---

## References

1. Aguirre-Hernández, R., & Farewell, V. T. (2002). A Pearson-type goodness-of-fit test for stationary and time-continuous Markov regression models. *Statistics in Medicine*, 21(13), 1899–1911. doi:10.1002/sim.1152
2. Ameriks, J., Briggs, J., Caplin, A., Shapiro, M. D., & Tonetti, C. (2020). Long-term-care utility and late-in-life saving. *Journal of Political Economy*, 128(6), 2375–2451. doi:10.1086/706686
3. Arias, E., & Xu, J. (2025). United States life tables, 2023. *National Vital Statistics Reports*, 74(6). Hyattsville, MD: National Center for Health Statistics.
4. Boards of Trustees, Federal Hospital Insurance and Federal Supplementary Medical Insurance Trust Funds (2026). *2026 Annual Report*. Washington, DC.
5. Braun, R. A., Kopecky, K. A., & Koreshkova, T. (2017). Old, sick, alone, and poor: a welfare analysis of old-age social insurance programmes. *Review of Economic Studies*, 84(2), 580–612. doi:10.1093/restud/rdw016
6. Brown, J. R., & Finkelstein, A. (2008). The interaction of public and private insurance: Medicaid and the long-term care insurance market. *American Economic Review*, 98(3), 1083–1102. doi:10.1257/aer.98.3.1083
7. Bugliari, D., Birnbaum, D. A., Carroll, J., Hayes, J., Hollister, B., Hurd, M. D., Lee, S., Main, R., Meijer, E., Pantoja, P., & Rohwedder, S. (2025). *RAND HRS Longitudinal File 2022 (V1) Documentation*. Santa Monica, CA: RAND Center for the Study of Aging.
8. Centers for Medicare & Medicaid Services (2023). *2024 Medicare Parts A & B Premiums and Deductibles*. Fact sheet, 12 October 2023.
9. Centers for Medicare & Medicaid Services. *Medicare Current Beneficiary Survey Cost Supplement Public Use Files, 2019, 2021, 2022 and 2023*. Accessed September 2026.
10. Crimmins, E. M., Hayward, M. D., & Saito, Y. (1994). Changing mortality and morbidity rates and the health status and life expectancy of the older population. *Demography*, 31(1), 159–175. doi:10.2307/2061913
11. De Nardi, M., French, E., & Jones, J. B. (2010). Why do the elderly save? The role of medical expenses. *Journal of Political Economy*, 118(1), 39–75. doi:10.1086/651674
12. De Nardi, M., French, E., Jones, J. B., & McCauley, J. (2016). Medical spending of the US elderly. *Fiscal Studies*, 37(3–4), 717–747. doi:10.1111/j.1475-5890.2016.12106
13. de Wreede, L. C., Fiocco, M., & Putter, H. (2011). mstate: an R package for the analysis of competing risks and multi-state models. *Journal of Statistical Software*, 38(7). doi:10.18637/jss.v038.i07
14. Fahle, S., McGarry, K., & Skinner, J. (2016). Out-of-pocket medical expenditures in the United States: evidence from the Health and Retirement Study. *Fiscal Studies*, 37(3–4), 785–819. doi:10.1111/j.1475-5890.2016.12126
15. Fong, J. H., Shao, A. W., & Sherris, M. (2015). Multistate actuarial models of functional disability. *North American Actuarial Journal*, 19(1), 41–59. doi:10.1080/10920277.2014.978025
16. French, E., & Jones, J. B. (2004). On the distribution and dynamics of health care costs. *Journal of Applied Econometrics*, 19(6), 705–721. doi:10.1002/jae.790
17. Goldman, D. P., Shang, B., Bhattacharya, J., et al. (2005). Consequences of health trends and medical innovation for the future elderly. *Health Affairs*, 24(Suppl. 2), W5-R5–W5-R17. doi:10.1377/hlthaff.w5.r5
18. Haberman, S., & Pitacco, E. (2018). *Actuarial Models for Disability Insurance*. Boca Raton, FL: Chapman and Hall/CRC. doi:10.1201/9781315136622
19. Health and Retirement Study. *RAND HRS Longitudinal File 2022 (V1) public use dataset*. Produced and distributed by the University of Michigan with funding from the National Institute on Aging (NIA U01AG009740 and NIA R01AG073289). Ann Arbor, MI (May 2025).
20. Hubbard, R. G., Skinner, J., & Zeldes, S. P. (1995). Precautionary saving and social insurance. *Journal of Political Economy*, 103(2), 360–399. doi:10.1086/261987
21. Hurd, M. D., Martorell, P., Delavande, A., Mullen, K. J., & Langa, K. M. (2013). Monetary costs of dementia in the United States. *New England Journal of Medicine*, 368(14), 1326–1334. doi:10.1056/NEJMsa1204629
22. Hurd, M. D., Michaud, P.-C., & Rohwedder, S. (2017). Distribution of lifetime nursing home use and of out-of-pocket spending. *Proceedings of the National Academy of Sciences*, 114(37), 9838–9842. doi:10.1073/pnas.1700618114
23. Jackson, C. H. (2011). Multi-state models for panel data: the msm package for R. *Journal of Statistical Software*, 38(8). doi:10.18637/jss.v038.i08
24. Jones, J. B., De Nardi, M., French, E., McGee, R., & Kirschner, J. (2018). The lifetime medical spending of retirees. *Federal Reserve Bank of Richmond Economic Quarterly*, 104(3), 103–135. doi:10.21144/eq1040301
25. Kalbfleisch, J. D., & Lawless, J. F. (1985). The analysis of panel data under a Markov assumption. *Journal of the American Statistical Association*, 80(392), 863–871. doi:10.1080/01621459.1985.10478195
26. Kelley, A. S., McGarry, K., Fahle, S., et al. (2013). Out-of-pocket spending in the last five years of life. *Journal of General Internal Medicine*, 28(2), 304–309. doi:10.1007/s11606-012-2199-x
27. Kelley, A. S., McGarry, K., Gorges, R., & Skinner, J. S. (2015). The burden of health care costs for patients with dementia in the last 5 years of life. *Annals of Internal Medicine*, 163(10), 729–736. doi:10.7326/M15-0381
28. Kemper, P., Komisar, H. L., & Alecxih, L. (2005). Long-term care over an uncertain future: what can current retirees expect? *Inquiry*, 42(4), 335–350. doi:10.5034/inquiryjrnl_42.4.335
29. Li, Z., Shao, A. W., & Sherris, M. (2017). The impact of systematic trend and uncertainty on mortality and disability in a multistate latent factor model for transition rates. *North American Actuarial Journal*, 21(4), 594–610. doi:10.1080/10920277.2017.1330157
30. Lubitz, J., Cai, L., Kramarow, E., & Lentzner, H. (2003). Health, life expectancy, and health care spending among the elderly. *New England Journal of Medicine*, 349(11), 1048–1055. doi:10.1056/NEJMsa020614
31. Marshall, S., McGarry, K., & Skinner, J. S. (2011). The risk of out-of-pocket health care expenditure at the end of life. In D. A. Wise (Ed.), *Explorations in the Economics of Aging* (pp. 101–128). Chicago: University of Chicago Press. doi:10.7208/chicago/9780226903385.003.0004
32. Palumbo, M. G. (1999). Uncertain medical expenses and precautionary saving near the end of the life cycle. *Review of Economic Studies*, 66(2), 395–421. doi:10.1111/1467-937X.00092
33. Poterba, J., Venti, S., & Wise, D. A. (2011). The composition and drawdown of wealth in retirement. *Journal of Economic Perspectives*, 25(4), 95–118. doi:10.1257/jep.25.4.95
34. Putter, H., Fiocco, M., & Geskus, R. B. (2007). Tutorial in biostatistics: competing risks and multi-state models. *Statistics in Medicine*, 26(11), 2389–2430. doi:10.1002/sim.2712
35. Riley, G. F., & Lubitz, J. D. (2010). Long-term trends in Medicare payments in the last year of life. *Health Services Research*, 45(2), 565–576. doi:10.1111/j.1475-6773.2010.01082.x
36. Rockafellar, R. T., & Uryasev, S. (2000). Optimization of conditional value-at-risk. *Journal of Risk*, 2(3), 21–41. doi:10.21314/JOR.2000.038
37. Shao, A. W., Sherris, M., & Fong, J. H. (2017). Product pricing and solvency capital requirements for long-term care insurance. *Scandinavian Actuarial Journal*, 2017(2), 175–208. doi:10.1080/03461238.2015.1095793
38. Sherris, M., & Wei, P. (2021). A multi-state model of functional disability and health status in the presence of systematic trend and uncertainty. *North American Actuarial Journal*, 25(1), 17–39. doi:10.1080/10920277.2019.1708755
39. Sonnega, A., Faul, J. D., Ofstedal, M. B., Langa, K. M., Phillips, J. W. R., & Weir, D. R. (2014). Cohort profile: the Health and Retirement Study (HRS). *International Journal of Epidemiology*, 43(2), 576–585. doi:10.1093/ije/dyu067
40. Titman, A. C., & Sharples, L. D. (2010). Model diagnostics for multi-state models. *Statistical Methods in Medical Research*, 19(6), 621–651. doi:10.1177/0962280209105541
41. van den Hout, A. (2016). *Multi-State Survival Models for Interval-Censored Data*. Boca Raton, FL: Chapman and Hall/CRC. doi:10.1201/9781315374321

*DOIs were verified against the Crossref REST API on 15 September 2026.*
