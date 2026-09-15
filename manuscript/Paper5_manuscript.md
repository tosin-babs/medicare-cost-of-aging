# Health-State Transitions and the Lifetime Cost of Aging: A Multi-State Actuarial Model of Medicare Spending and Household Out-of-Pocket Tail Risk

**Oluwatosin Dorcas Babalola**¹ *(corresponding author)*

¹ Department of Actuarial Science and Quantitative Risk Analysis and Management, Georgia State University, Atlanta, GA, USA. obabalola4@student.gsu.edu

**Word count.** 4,482 excluding abstract, tables and references.

---

## Abstract

Medicare's Hospital Insurance trust fund is projected to be depleted in 2033, yet aggregate projections say little about how the cost of aging falls on individual households. We build a five-state continuous-time Markov model of later-life health (healthy, chronic illness, disability, long-term-care need, dead) from 213,552 intervals between Health and Retirement Study interviews, 1998 to 2022, with deaths dated to the month. State-specific Medicare costs come from the Medicare Current Beneficiary Survey and out-of-pocket cost distributions from HRS core and exit interviews. Mortality is calibrated to the 2023 US life table, and lifetime costs from age 65 are projected by microsimulation and checked against an exact recursion. For a 65-year-old drawn from the population, the present value at 3% of lifetime Medicare spending is $153,316 for men and $172,481 for women, and of out-of-pocket spending on care $37,660 and $48,975, before Part B premiums. The distribution is strongly skewed: the mean of the worst 5% of outcomes (CVaR95) is $127,541 for men and $174,866 for women, and 77.8% and 88.3% of lives in that tail pass through long-term-care need, against 46.4% and 60.6% of all lives. Health at 65 changes the timing of costs far more than their expected value. Passing half of the post-2033 Part A shortfall to beneficiaries raises expected lifetime out-of-pocket cost by $872 for men and $1,042 for women; real cost growth at the Trustees' Part B rate raises CVaR95 by $36,990 and $55,219. Code and a public calculator are released.

**Keywords.** multi-state model; interval-censored panel data; Medicare; long-term care; out-of-pocket spending; tail risk; microsimulation; Health and Retirement Study

---

## 1. Introduction

The 2026 Medicare Trustees Report projects that the Hospital Insurance (HI) trust fund will be depleted in the second quarter of 2033, after which incoming revenue would cover 89% of scheduled Part A benefits, and that Medicare spending will rise from 3.9% of GDP in 2025 to 6.5% in 2050 (Boards of Trustees, 2026). These projections are aggregates. They answer what the program will cost, not what aging will cost a particular household, how uncertain that cost is, or which health paths produce the bad outcomes. Those questions matter to the people who price and regulate long-term-care, Medigap and Medicare Advantage products, to planners advising retirees, and to policymakers choosing how a financing gap is closed.

The actuarial tool for this problem is the multi-state model. A person moves among health states with age-dependent intensities; each state carries a cost; the expected present value of lifetime cost follows from the transition probabilities, and its distribution follows from simulating paths. Multi-state models are standard in disability and long-term-care insurance (Haberman and Pitacco, 2018) and have been estimated on the Health and Retirement Study (HRS) for functional disability (Fong, Shao and Sherris, 2015; Sherris and Wei, 2021). Economists, separately, have measured medical-expense risk in retirement and its consequences for saving (Hubbard, Skinner and Zeldes, 1995; De Nardi, French and Jones, 2010; Jones et al., 2018). The two strands rarely meet in one model that is payer-specific, reports the tail, and connects to Medicare's financing.

This paper builds that model with public data and released code. We ask four questions.

- RQ1. What are the transition intensities among healthy (H), chronic illness (C), disability (D), long-term-care need (L) and death (X) for Americans aged 50 and over, and how do they vary with age, sex, education and race-ethnicity?
- RQ2. What are expected lifetime Medicare and household out-of-pocket costs from 65, by health state at 65, sex and income?
- RQ3. What is the distribution of the present value of lifetime out-of-pocket cost, what are its Value-at-Risk and Conditional Value-at-Risk, and which paths produce the tail?
- RQ4. How would plausible responses to the post-2033 HI shortfall change household out-of-pocket tail risk and asset exhaustion?

Four design choices shape the answers. The transition model is fitted to interval-censored panel data by exact likelihood, so transitions between biennial interviews are not assumed away. The model's mortality is tested against the 2023 US life table and then calibrated to it, keeping the state relativities the data identify. Out-of-pocket costs are drawn from full empirical distributions by state, not means, and the last year of life is drawn from exit interviews, which core interviews never observe. And the expected values reported by simulation are checked against an exact recursion.

The main results are as follows. Life expectancy at 65 is 18.3 years for men and 20.8 for women, of which 1.58 and 2.60 years are spent in long-term-care need; 46.4% of men and 60.6% of women enter that state. Lifetime Medicare spending varies little with health at 65, because poorer health shortens the years over which costs accrue. Out-of-pocket risk is concentrated: CVaR95 is 3.4 times the mean for men and 3.6 times for women, and the tail is dominated by long-term-care paths. A partial pass-through of the HI shortfall moves expected out-of-pocket cost by about 2%, small beside the effect of faster real cost growth, which falls mostly on the tail.

## 2. Background

**Medical-expense risk in retirement.** Uncertain medical costs affect saving and asset decumulation (Hubbard, Skinner and Zeldes, 1995; Palumbo, 1999), and De Nardi, French and Jones (2010) showed that medical expenses that rise with age and income help explain why the elderly run down assets slowly. De Nardi et al. (2016) documented medical spending of the US elderly by payer, and Jones et al. (2018) estimated lifetime medical spending of retirees with a dynamic model of health and spending. End-of-life spending has been measured from HRS exit interviews (Marshall, McGarry and Skinner, 2011; Kelley et al., 2013) and is highest for people with dementia (Kelley et al., 2015; Hurd et al., 2013). Hurd, Michaud and Rohwedder (2017) showed that lifetime nursing-home use and its out-of-pocket cost are concentrated in a minority of people. Medicaid's role as payer of last resort shapes demand for private long-term-care insurance (Brown and Finkelstein, 2008), and preferences over long-term care shape late-life saving (Ameriks et al., 2020).

**Health paths and cumulative spending.** Lubitz et al. (2003) found that older people in better health live longer but accumulate similar Medicare spending over their remaining lives. Multi-state health expectancies go back at least to Crimmins, Hayward and Saito (1994), and microsimulation of the future elderly is the basis of the Future Elderly Model (Goldman et al., 2005).

**Actuarial multi-state models.** Haberman and Pitacco (2018) set out the multiple-state framework for disability and long-term-care insurance. Fong, Shao and Sherris (2015) estimated multi-state models of functional disability from HRS; Shao, Sherris and Fong (2017) used such a model for long-term-care insurance pricing and solvency capital; Li, Shao and Sherris (2017) and Sherris and Wei (2021) added systematic trend and uncertainty.

**Estimation from panel data.** When states are observed only at interviews, the likelihood of a continuous-time Markov model is built from transition probabilities over the observed intervals (Kalbfleisch and Lawless, 1985), as implemented in the msm package (Jackson, 2011) and treated at length by van den Hout (2016). Titman and Sharples (2010) review diagnostics. Competing-risk and multi-state models for exactly observed transitions are covered by Putter, Fiocco and Geskus (2007) and de Wreede, Fiocco and Putter (2011).

**What this paper adds.** It combines a multi-state health model estimated on interval-censored HRS data with payer-specific costs from the MCBS, empirical out-of-pocket distributions including end-of-life costs, tail measures (Rockafellar and Uryasev, 2000), and scenarios tied to the Trustees' financing projections, and it releases the whole pipeline and a public calculator.

## 3. Data

**HRS panel.** We use the RAND HRS Longitudinal File 2022 (V1) (Bugliari et al., 2025; Sonnega et al., 2014), waves 4 to 16 (1998 to 2022), respondents aged 50 and over at interview. Each interview is assigned a state:

- H: no ever-diagnosed condition among eight (hypertension, diabetes, cancer, lung disease, heart problems, stroke, psychiatric problems, arthritis) and no limitation in the five RAND activities of daily living (ADL);
- C: at least one condition and no ADL limitation;
- D: one or two ADL limitations;
- L: three or more ADL limitations, or living in a nursing home at interview;
- X: dead, dated to the month from the RAND death date.

The panel has 40,354 respondents with 237,944 classified person-interviews (Table 1). Consecutive interviews give 197,590 intervals with a mean length of 2.0 years, and 15,962 deaths are dated exactly; persons last seen alive are censored at that interview. Weighted, 16.5% of person-interviews are in H, 68.6% in C, 10.8% in D and 4.1% in L. Observed transitions are in Table A1. Because conditions are ever diagnosed, C to H does not occur and is not modeled.

**Out-of-pocket spending.** Core interviews report out-of-pocket medical spending over the previous two years, excluding premiums, with RAND imputations. We halve it to an annual figure, express it in 2024 dollars with the CPI-U, and attach it to the state observed at that interview. The exit interview, answered by a proxy after death, reports out-of-pocket spending from the last core interview to death. We take the final-year amount as that spending times min(1, 12/months), which assigns a longer window's spending evenly and so understates the final year; 14,576 decedents aged 65 and over contribute.

**Medicare spending.** The MCBS Cost Supplement public use files for 2019 and 2021 to 2023 (29,144 beneficiary-years) give annual spending by payer, with Medicare Advantage payments included, in cells of age by count of chronic conditions (0-1, 2-3, 4+). Standard errors use the survey's balanced repeated replication with Fay's adjustment of 0.30. The pooled Medicare mean is $11,802 (standard error $278), 44.2% of beneficiary-years are in Medicare Advantage, and inpatient plus home health account for 17.6% of all-payer spending (Table A6). The Cost Supplement excludes facility, hospice and institutional events, which fall mostly in the D and L states.

**Other sources.** Mortality benchmarks are the 2023 US period life tables (Arias and Xu, 2025), selected ages in Table A7. HI depletion timing, the payable share and cost growth rates are from the 2026 Trustees Report. The standard Part B premium is $174.70 a month in 2024 (CMS, 2023).

## 4. Model

### 4.1 Transition intensities

Let $S = \{H, C, D, L, X\}$ and let $q_{jk}(x, z)$ be the intensity of moving from $j$ to $k$ at age $x$ for covariates $z$. Twelve transitions are allowed (Figure 1): H to C, D, X; C to D, L, X; D to H, C, L, X; L to D, X. Each intensity is log-linear,

$$\log q_{jk}(x, z) = \beta_{0,jk} + \beta_{1,jk}\,\frac{x - 65}{10} + \gamma_{jk}^{\top} z,$$

a Gompertz form in age, with $z$ = (female, any college, nonwhite or Hispanic). The intensity matrix $Q(x, z)$ has off-diagonal entries $q_{jk}$ and rows summing to zero. Over an interval of length $d$ starting at age $x$, $Q$ is held at the midpoint age, so $P(x, x + d) = \exp\{Q(x + d/2, z)\, d\}$, the solution of the Kolmogorov forward equation for piecewise-constant intensities.

![Figure 1. State space and allowed transitions.](output/figures/fig_state_diagram.png)

For person $i$ observed in state $r$ at age $x$ and in state $s$ after $d$ years, the likelihood contribution is $P_{rs}(x, x + d)$. For a death at time $d$ after the last interview in state $r$, the state just before death is unobserved and the contribution is

$$\sum_{k \neq X} P_{rk}(x, x + d)\, q_{kX}(x + d, z).$$

The log likelihood is maximized with gradients from automatic differentiation through the matrix exponential; standard errors come from the inverse observed information. Estimation is unweighted, the usual convention for panel multi-state models, with sex, education and race-ethnicity entering as covariates; weighted prevalence is used for validation. Starting values come from crude rates. The fitted model is checked against a simulated panel with known intensities in the released tests.

### 4.2 Population at 65 and mortality calibration

A simulated 65-year-old is drawn from the weighted joint distribution of state, education and race-ethnicity among HRS respondents aged 64 to 66, with nursing-home residents included through their own weight. For men the state mix is 14.6% H, 73.5% C, 8.9% D and 3.0% L; for women 14.4%, 72.3%, 9.2% and 4.0%.

The fitted model pools deaths from 1998 to 2022. Its life expectancy at 65 for the entry mix is 16.72 years for men and 19.54 for women, against 18.19 and 20.71 in the 2023 table (Table 3). Rather than change the relative mortality of the states, which the data identify, we scale every death intensity by

$$\lambda(x) = \exp\{c_0 + c_1 (x - 65)/10\},$$

by sex, with $(c_0, c_1)$ minimizing the $l_x$-weighted squared difference between the model's and the table's $\log q_x$ at ages 65 to 99. The multiplier runs from 0.70 at 65 to 0.92 at 95 for men and from 0.64 to 1.05 for women. The uncalibrated model is kept as a robustness variant.

### 4.3 State costs

Medicare cost in state $j$ and age band $b$ (65-74, 75+) is the MCBS cell mean for band $b$ averaged over the distribution of chronic-condition counts among HRS respondents in $j$ and $b$. The HRS counts eight conditions and the MCBS a longer list, so this mapping places HRS respondents in lighter cells than the Medicare population they represent: the cohort's implied Medicare spending per person-year is 0.846 and 0.866 of the MCBS mean in the two bands (Table A4). We keep the state relativities and scale the level in each band so the weighted HRS average equals the MCBS mean, factors of 1.20 and 1.17. After scaling, the model cohort reproduces the MCBS means to within 1.6%.

Out-of-pocket cost in a year alive in state $j$ is drawn from the weighted empirical HRS distribution for $j$, the age band and sex. In the year of death the draw is replaced by one from the exit-interview distribution for the age band and sex. The standard Part B premium is added for each year alive and reported separately.

### 4.4 Lifetime cost and its distribution

Lives step through one-year transition matrices $P(x, x+1)$ from 65 to 110. With costs accruing at the start of each year and discount factor $v = 1/1.03$, the present value of out-of-pocket cost for a life with states $J_t$ at age $65 + t$ is

$$PV^{O} = \sum_{t=0}^{44} v^{t} \Big[ \mathbb{1}\{J_t \neq X\}\, O_{t} + \mathbb{1}\{J_t \neq X, J_{t+1} = X\}\, (E_t - O_t) \Big],$$

where $O_t$ is the ordinary draw and $E_t$ the end-of-life draw; $PV^{M}$ and the premium are defined in the same way. With $\pi(t)$ the state distribution at $65 + t$, $\pi(t+1) = \pi(t) P(65+t, 66+t)$, and $\mu_j$ and $\mu^{E}$ the means of the draws, the expected values have the closed form

$$\mathbb{E}\,PV^{O} = \sum_{t} v^{t} \sum_{j \neq X} \pi_j(t) \big[\mu_j + P_{jX}(65+t, 66+t)\,(\mu^{E} - \mu_j)\big],$$

which the simulation means must match. Tail risk is summarized by $\mathrm{VaR}_\alpha$, the $\alpha$ quantile of $PV^{O}$, and $\mathrm{CVaR}_\alpha = \mathbb{E}[PV^{O} \mid PV^{O} \geq \mathrm{VaR}_\alpha]$ at $\alpha$ = 0.90, 0.95 and 0.99 (Rockafellar and Uryasev, 2000). We simulate 100,000 lives for each sex and each health state at 65, and 100,000 from the population mix. Parameter uncertainty is the spread of the exact expected values over 200 draws of the intensity parameters from their asymptotic normal distribution.

For income, household income is ranked into weighted tertiles within interview wave and age group. A life in tertile $k$ starts from the entry mix of tertile $k$ at 64 to 66 and draws out-of-pocket costs from tertile $k$ at every age.

### 4.5 Financing scenarios

The scenarios apply to a cohort turning 65 in 2026, so calendar year is 2026 plus years since 65. Part A's share of each state's Medicare cost is the MCBS inpatient-plus-home-health share within each chronic-condition cell, weighted by the state's condition mix.

- S0: benefits paid in full, the Trustees' convention.
- S1: from 2033 Part A pays 89% of scheduled benefits, and a share $s$ of the shortfall becomes out-of-pocket cost, for $s$ = 0 (a pure provider payment cut), 25%, 50% and 100%.
- S2: the whole cohort shortfall falls on person-years in long-term-care need, as a service-specific cut to post-acute coverage would.
- S3: S1 with $s$ = 50% plus real cost growth at the Trustees' Part B per-beneficiary rate of 1.7% a year.

Asset exhaustion compares cumulative undiscounted out-of-pocket cost with household net assets at 65 by income tertile, with no investment returns or income. It measures exposure, the point at which Medicaid eligibility would come into view, not a forecast of Medicaid enrollment.

## 5. Validation

**Mortality.** Calibration brings life expectancy at 65 to 18.31 years for men and 20.87 for women, within 0.16 years of the table (Table 3). One-year death probabilities match closely from 70 to 85. The log-linear multiplier cannot follow the table's steep rise past 90: at 95 the calibrated model gives 0.1939 for men against 0.2563 in the table, so survival at the oldest ages, and costs there, are somewhat overstated.

**Prevalence.** Figure 2 and Table A3 compare the calibrated model's state distribution among survivors with the weighted HRS cross-section. Agreement is within 3 percentage points in every state up to age 80 for both sexes. The model understates H at older ages, because it follows a cohort from 65 while the cross-section includes people interviewed with missing condition histories, and understates L among women over 90 (29.1% against 34.4%).

![Figure 2. State prevalence by age: weighted HRS cross-section (solid) and calibrated model (dashed).](output/figures/fig_prevalence.png)

**Spending.** After the level scaling in Section 4.3 the model's Medicare spending per person-year is 1.013 and 1.016 times the MCBS mean in the two age bands (Table A4). The simulation means agree with the exact recursion: population-mix lifetime out-of-pocket cost is $37,660 simulated against $37,703 exact for men.

## 6. Results

### 6.1 Transitions (RQ1)

Table 2 reports the intensities; the likelihood-ratio test for the education and race-ethnicity terms is 1,512.4 on 24 degrees of freedom. Death intensities rise with age in every state, by a factor of 2.35 per decade from H and 2.07 from C, and more slowly from D (1.42) and L (1.54), the flattening expected when frailer people leave the at-risk group first. Women die at 0.42 to 0.68 of men's rate from each state, and are 12% more likely than men to move from C to D. Any college lowers the rate of moving from C to D (hazard ratio 0.75) and from C to L (0.40), and lowers mortality from H (0.46) and C (0.80). Being nonwhite or Hispanic raises the rate from C to D (1.34) and from C to L (2.35), while mortality from D and L is lower (0.64 and 0.76), a pattern consistent with selection into those states. The direct C to L intensity falls with age (0.16 per decade, interval 0.12 to 0.22): with two-year intervals, the model attributes most moves from C to L at older ages to a path through D, whose intensities rise with age. One-year probabilities are in Table A2 and Figure 3.

![Figure 3. One-year probability of death by state at ages 65, 75 and 85, fitted model, reference covariates.](output/figures/fig_transitions.png)

### 6.2 Health expectancies

A 65-year-old man drawn from the population can expect 18.3 more years: 1.15 healthy, 13.15 with chronic illness, 2.45 with disability and 1.58 in long-term-care need (Table 5b and Figure 4). A woman can expect 20.8 years, with 3.09 in disability and 2.60 in long-term-care need. Starting healthy adds about two years of life for either sex against the population mix; starting in L cuts life expectancy to 12.5 years for men and 15.7 for women. By covariate profile before calibration (Table A5), education moves life expectancy at 65 by more than race-ethnicity does.

![Figure 4. Expected years in each state from 65, by health state at 65.](output/figures/fig_health_expectancy.png)

### 6.3 Annual costs by state

Medicare spending per year rises from $5,291 in H to $14,048 in L at ages 65 to 74, and from $7,010 to $14,527 at 75 and over (Table 4). Out-of-pocket spending is where the states differ most. Mean annual spending is about $1,200 in H, $2,000 to $2,300 in C and $2,600 to $3,100 in D, but $9,228 for men and $10,829 for women in L at 75 and over, with a 99th percentile of $101,341 and $122,600 (Table 4b). Out-of-pocket spending in the last year of life averages $9,913 for men and $12,641 for women who die at 75 or older, and its 99th percentile is $125,678 and $151,655 (Table 4c).

### 6.4 Expected lifetime cost (RQ2)

Table 5 gives expected lifetime costs from 65. For the population mix the present value of Medicare spending is $153,316 for men (95% parameter interval $151,948 to $154,224) and $172,481 for women. Out-of-pocket spending on care is $37,660 for men (interval $37,398 to $38,002) and $48,975 for women, with medians of $31,282 and $38,684. The Part B premium adds $29,224 and $32,221. The end-of-life step contributes $2,663 and $3,072 of the out-of-pocket total. Parameter uncertainty is small relative to the spread across lives: the intervals for expected values are within about 1% of the mean.

Health at 65 changes expected lifetime Medicare cost less than it changes annual cost. A man who is healthy at 65 is expected to cost Medicare $140,295 over his life; one in long-term-care need, whose annual costs are more than twice as high at 65, is expected to cost $126,204, because he is expected to live 12.5 years rather than 20.4. The highest expected cost is for men and women with chronic illness but no limitation at 65, $157,627 and $176,905, who combine long lives with high annual cost. Expected out-of-pocket cost varies even less: $35,373 for men healthy at 65 and $38,065 for men in L.

Income changes the composition more than the total. Low-income 65-year-olds are more often in L at entry (6.8% of men and 8.0% of women in the lowest tertile, against 0.8% in the highest) and more often reach it (51.1% of men against 43.6%), but live shorter lives and draw on lower out-of-pocket spending in each state, partly because Medicaid pays. Their expected lifetime out-of-pocket cost is $30,387 for men and $42,713 for women, against $44,277 and $59,647 in the highest tertile (Table 5c). Because the transition model has no income term, the life-expectancy gap by income (17.4 against 19.1 years for men) is understated.

### 6.5 The tail (RQ3)

Figure 5 shows the distribution of lifetime out-of-pocket cost for the population mix. For men, VaR95 is $92,761 and CVaR95 is $127,541, 3.4 times the mean; CVaR99 is $188,051. For women, VaR95 is $122,555, CVaR95 $174,866 and CVaR99 $282,008 (Table 6).

![Figure 5. Distribution of the present value of lifetime out-of-pocket cost from 65, population mix, with Value-at-Risk at 90%, 95% and 99%.](output/figures/fig_lifetime_oop.png)

The tail is a long-term-care phenomenon. Among men in the worst 5% of outcomes, 77.8% passed through L, against 46.4% of all men; for women 88.3% against 60.6%. People in the tail also live longer, dying at 87.4 on average against 83.3 for all men, since a long stay in L requires survival. The end-of-life draw accounts for 19.8% of the tail's present value for men and 16.1% for women. Starting in L raises CVaR95 to $158,274 for men and $197,908 for women even though expected cost barely moves (Figure 6): health at 65 matters for the tail more than for the mean.

![Figure 6. Expected lifetime out-of-pocket cost and CVaR95 by health state at 65.](output/figures/fig_entry_states.png)

### 6.6 Financing scenarios (RQ4)

Table 7 and Figure 7 report the scenarios. A pure provider payment cut (S1 at 0%) leaves household cost unchanged by construction, and its effect would come through access, which the model does not capture. Passing a quarter of the Part A shortfall to beneficiaries raises expected lifetime out-of-pocket cost by $436 for men and $521 for women; half raises it by $872 and $1,042; the whole shortfall by $1,743 and $2,084, and CVaR95 by $2,403 and $2,732. Concentrating the shortfall on person-years in long-term-care need (S2) leaves the mean change the same but raises CVaR95 by $5,945 for men and $6,380 for women, more than twice the effect of spreading it. Real cost growth at the Trustees' Part B rate with half the shortfall shifted (S3) raises the mean by $9,428 and $13,781 and CVaR95 by $36,990 and $55,219.

![Figure 7. Change in the mean and in CVaR95 of lifetime out-of-pocket cost under the financing scenarios.](output/figures/fig_scenarios.png)

These effects are modest because Part A is a small part of Medicare spending in community settings: inpatient and home health are 17.6% of all-payer spending in the Cost Supplement, which excludes skilled nursing facilities. The shortfall scenarios are therefore lower bounds, and the growth scenario shows where the larger household risk lies.

Asset exhaustion is concentrated at low income (Table 7b). In the lowest income tertile, 19.0% of households have no positive assets at 65, and of the rest 32.2% of men and 36.9% of women spend their assets on out-of-pocket care costs, at a median age of 70 and 71. In the middle tertile the shares are 11.3% and 14.4%, and in the highest 3.6% and 4.8%. Shifting half the shortfall raises these shares by at most half a percentage point.

### 6.7 Robustness

Table 8 reports variants for the population mix with 40,000 lives per sex, so its baseline row differs from Table 5 by simulation error. The discount rate matters most for the tail: men's CVaR95 is $146,755 at 2% and $113,192 at 4%, against $128,011 at 3%, and real cost growth at the Trustees' Part B rate raises it to $163,364. A 25% uplift to Medicare cost in D and L, for the facility and hospice events the Cost Supplement omits, raises lifetime Medicare spending for men from $153,106 to $162,628; without the level scaling to MCBS it would be $129,102. Without mortality calibration, life expectancy at 65 falls to 16.7 years for men and CVaR95 to $122,640. Without the end-of-life step CVaR95 is $121,323, so exit-interview costs add about 5% to the tail.

The refits change the state definitions or the sample, rebuild the entry mix, costs and calibration, and are compared with the sex-only model, whose CVaR95 for men is $131,093. Defining L as two or more ADL limitations raises the share ever in L to 60% of men and 72% of women but moves men's expected out-of-pocket cost by $134 and CVaR95 by $116. Not counting nursing-home residence as L changes both by less than 1%. Restricting the panel to waves 9 to 16 (2008 to 2022) lowers expected out-of-pocket cost to $35,392 for men and $44,363 for women and CVaR95 to $118,334 and $155,362. In every variant CVaR95 stays between 3.3 and 3.6 times the mean for men and between 3.5 and 3.7 times for women.

## 7. Discussion

**For Medicare policy.** How the HI gap is closed matters less to the average household than to the few who need long-term care. A cut that falls on post-acute and long-term-care services concentrates the burden where out-of-pocket risk is already highest. The calculator reports these distributional effects, which aggregate solvency measures cannot show. The growth scenario is a reminder that the cost trend, not the 2033 date, drives most of the household risk.

**For insurers and planners.** Expected lifetime out-of-pocket cost is similar across health states at 65, but the tail is not, and it is driven by long-term-care paths and by the final year of life. Products that cover long-term-care need or end-of-life costs address the part of the distribution that households cannot self-insure through ordinary saving. The model's state intensities, calibrated to current mortality, can be used directly in pricing and reserving work with the covariate structure shown in Table 2, and the relatively flat lifetime Medicare cost across entry states supports the finding of Lubitz et al. (2003) with more recent data and a payer split.

**For households.** A typical 65-year-old should expect a present value of out-of-pocket care costs near $38,000 for men and $49,000 for women, plus about $30,000 of Part B premiums, but should plan for the possibility of several times that. For low-income households with modest assets, the realistic outcome in the bad case is spending down to Medicaid.

**Limitations.** Five matter most. First, the MCBS Cost Supplement excludes facility, hospice and institutional events, so Medicare cost in D and L is understated, and the Part A share omits skilled nursing; the robustness uplift gives a sense of scale. Second, HRS out-of-pocket draws are independent across years within a state, so persistence beyond what the states capture is missing and the tail is understated. Third, the model is Markov in age with a log-linear age effect and no calendar trend; duration dependence in disability and mortality improvement after 2023 are not modeled, and calibration to a period table understates the longevity of a cohort turning 65 in 2026. Fourth, out-of-pocket spending excludes premiums other than Part B and, by design, nursing-home costs paid by Medicaid; the asset-exhaustion measure ignores income, investment returns and spouses. Fifth, the condition-count bridge between HRS and MCBS is approximate, and the level scaling assumes the HRS state relativities carry over. Linked HRS-Medicare claims would address the first and last and are the natural next step.

## 8. Conclusion

A five-state model fitted to 24 years of HRS panel data, calibrated to current mortality and linked to payer-specific costs, shows that the expected lifetime cost of aging varies little with health at 65 while its tail varies a great deal, that the tail is made of long-term-care paths and the last year of life, and that a partial pass-through of Medicare's Part A shortfall matters far less to households than the long-run growth of costs. The released code rebuilds every number, and the calculator puts the results in front of the people who carry the risk.

---

## Declarations

**Data availability.** The RAND HRS Longitudinal File and HRS exit data are available to registered users from the Health and Retirement Study; the MCBS Cost Supplement public use files from the Centers for Medicare & Medicaid Services; the life tables and Trustees Report are public. None is redistributed. The HRS (Health and Retirement Study) is sponsored by the National Institute on Aging (grant numbers NIA U01AG009740 and NIA R01AG073289) and is conducted by the University of Michigan.

**Code availability.** The seeded pipeline is at https://github.com/tosin-babs/medicare-cost-of-aging; `python/run_all.py` rebuilds every table and figure and `pytest tests` runs the checks. The public calculator is at https://medicare-cost-of-aging.vercel.app.

**Competing interests.** None declared.

**Ethics.** The analysis uses de-identified public-use survey data and did not require ethical approval.

**AI-assistance disclosure.** Generative AI (Claude, Anthropic) was used to assist with code development, code review and language editing. The author designed the study, specified all models and parameters, verified and interpreted all results, and takes full responsibility for the content. AI systems are not authors.

**CRediT statement.** **Oluwatosin Dorcas Babalola**: conceptualization, methodology, software, formal analysis, data curation, visualization, writing (original draft), writing (review and editing).

---

## References

1. Ameriks, J., Briggs, J., Caplin, A., Shapiro, M. D., & Tonetti, C. (2020). Long-term-care utility and late-in-life saving. *Journal of Political Economy*, 128(6), 2375–2451. doi:10.1086/706686
2. Arias, E., & Xu, J. (2025). United States life tables, 2023. *National Vital Statistics Reports*, 74(6). Hyattsville, MD: National Center for Health Statistics.
3. Boards of Trustees, Federal Hospital Insurance and Federal Supplementary Medical Insurance Trust Funds (2026). *2026 Annual Report of the Boards of Trustees of the Federal Hospital Insurance and Federal Supplementary Medical Insurance Trust Funds*. Washington, DC.
4. Brown, J. R., & Finkelstein, A. (2008). The interaction of public and private insurance: Medicaid and the long-term care insurance market. *American Economic Review*, 98(3), 1083–1102. doi:10.1257/aer.98.3.1083
5. Bugliari, D., Birnbaum, D. A., Carroll, J., Hayes, J., Hollister, B., Hurd, M. D., Lee, S., Main, R., Meijer, E., Pantoja, P., & Rohwedder, S. (2025). *RAND HRS Longitudinal File 2022 (V1) Documentation*. Santa Monica, CA: RAND Center for the Study of Aging.
6. Centers for Medicare & Medicaid Services (2023). *2024 Medicare Parts A & B Premiums and Deductibles*. Fact sheet, 12 October 2023.
7. Centers for Medicare & Medicaid Services. *Medicare Current Beneficiary Survey Cost Supplement Public Use Files, 2019, 2021, 2022 and 2023*. Accessed September 2026.
8. Crimmins, E. M., Hayward, M. D., & Saito, Y. (1994). Changing mortality and morbidity rates and the health status and life expectancy of the older population. *Demography*, 31(1), 159–175. doi:10.2307/2061913
9. De Nardi, M., French, E., & Jones, J. B. (2010). Why do the elderly save? The role of medical expenses. *Journal of Political Economy*, 118(1), 39–75. doi:10.1086/651674
10. De Nardi, M., French, E., Jones, J. B., & McCauley, J. (2016). Medical spending of the US elderly. *Fiscal Studies*, 37(3–4), 717–747. doi:10.1111/j.1475-5890.2016.12106
11. de Wreede, L. C., Fiocco, M., & Putter, H. (2011). mstate: an R package for the analysis of competing risks and multi-state models. *Journal of Statistical Software*, 38(7). doi:10.18637/jss.v038.i07
12. Fong, J. H., Shao, A. W., & Sherris, M. (2015). Multistate actuarial models of functional disability. *North American Actuarial Journal*, 19(1), 41–59. doi:10.1080/10920277.2014.978025
13. Goldman, D. P., Shang, B., Bhattacharya, J., et al. (2005). Consequences of health trends and medical innovation for the future elderly. *Health Affairs*, 24(Suppl. 2), W5-R5–W5-R17. doi:10.1377/hlthaff.w5.r5
14. Haberman, S., & Pitacco, E. (2018). *Actuarial Models for Disability Insurance*. Boca Raton, FL: Chapman and Hall/CRC (first published 1999). doi:10.1201/9781315136622
15. Health and Retirement Study. *RAND HRS Longitudinal File 2022 (V1) public use dataset*. Produced and distributed by the University of Michigan with funding from the National Institute on Aging (grant numbers NIA U01AG009740 and NIA R01AG073289). Ann Arbor, MI (May 2025).
16. Hubbard, R. G., Skinner, J., & Zeldes, S. P. (1995). Precautionary saving and social insurance. *Journal of Political Economy*, 103(2), 360–399. doi:10.1086/261987
17. Hurd, M. D., Martorell, P., Delavande, A., Mullen, K. J., & Langa, K. M. (2013). Monetary costs of dementia in the United States. *New England Journal of Medicine*, 368(14), 1326–1334. doi:10.1056/NEJMsa1204629
18. Hurd, M. D., Michaud, P.-C., & Rohwedder, S. (2017). Distribution of lifetime nursing home use and of out-of-pocket spending. *Proceedings of the National Academy of Sciences*, 114(37), 9838–9842. doi:10.1073/pnas.1700618114
19. Jackson, C. H. (2011). Multi-state models for panel data: the msm package for R. *Journal of Statistical Software*, 38(8). doi:10.18637/jss.v038.i08
20. Jones, J. B., De Nardi, M., French, E., McGee, R., & Kirschner, J. (2018). The lifetime medical spending of retirees. *Federal Reserve Bank of Richmond Economic Quarterly*, 104(3), 103–135. doi:10.21144/eq1040301
21. Kalbfleisch, J. D., & Lawless, J. F. (1985). The analysis of panel data under a Markov assumption. *Journal of the American Statistical Association*, 80(392), 863–871. doi:10.1080/01621459.1985.10478195
22. Kelley, A. S., McGarry, K., Fahle, S., et al. (2013). Out-of-pocket spending in the last five years of life. *Journal of General Internal Medicine*, 28(2), 304–309. doi:10.1007/s11606-012-2199-x
23. Kelley, A. S., McGarry, K., Gorges, R., & Skinner, J. S. (2015). The burden of health care costs for patients with dementia in the last 5 years of life. *Annals of Internal Medicine*, 163(10), 729–736. doi:10.7326/M15-0381
24. Li, Z., Shao, A. W., & Sherris, M. (2017). The impact of systematic trend and uncertainty on mortality and disability in a multistate latent factor model for transition rates. *North American Actuarial Journal*, 21(4), 594–610. doi:10.1080/10920277.2017.1330157
25. Lubitz, J., Cai, L., Kramarow, E., & Lentzner, H. (2003). Health, life expectancy, and health care spending among the elderly. *New England Journal of Medicine*, 349(11), 1048–1055. doi:10.1056/NEJMsa020614
26. Marshall, S., McGarry, K., & Skinner, J. S. (2011). The risk of out-of-pocket health care expenditure at the end of life. In D. A. Wise (Ed.), *Explorations in the Economics of Aging* (pp. 101–128). Chicago: University of Chicago Press. doi:10.7208/chicago/9780226903385.003.0004
27. Palumbo, M. G. (1999). Uncertain medical expenses and precautionary saving near the end of the life cycle. *Review of Economic Studies*, 66(2), 395–421. doi:10.1111/1467-937X.00092
28. Putter, H., Fiocco, M., & Geskus, R. B. (2007). Tutorial in biostatistics: competing risks and multi-state models. *Statistics in Medicine*, 26(11), 2389–2430. doi:10.1002/sim.2712
29. Rockafellar, R. T., & Uryasev, S. (2000). Optimization of conditional value-at-risk. *Journal of Risk*, 2(3), 21–41. doi:10.21314/JOR.2000.038
30. Shao, A. W., Sherris, M., & Fong, J. H. (2017). Product pricing and solvency capital requirements for long-term care insurance. *Scandinavian Actuarial Journal*, 2017(2), 175–208. doi:10.1080/03461238.2015.1095793
31. Sherris, M., & Wei, P. (2021). A multi-state model of functional disability and health status in the presence of systematic trend and uncertainty. *North American Actuarial Journal*, 25(1), 17–39. doi:10.1080/10920277.2019.1708755
32. Sonnega, A., Faul, J. D., Ofstedal, M. B., Langa, K. M., Phillips, J. W. R., & Weir, D. R. (2014). Cohort profile: the Health and Retirement Study (HRS). *International Journal of Epidemiology*, 43(2), 576–585. doi:10.1093/ije/dyu067
33. Titman, A. C., & Sharples, L. D. (2010). Model diagnostics for multi-state models. *Statistical Methods in Medical Research*, 19(6), 621–651. doi:10.1177/0962280209105541
34. van den Hout, A. (2016). *Multi-State Survival Models for Interval-Censored Data*. Boca Raton, FL: Chapman and Hall/CRC. doi:10.1201/9781315374321

*DOIs were verified against the Crossref REST API on 15 September 2026.*
