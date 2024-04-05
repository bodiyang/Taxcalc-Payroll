---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Recipe1: Payroll Tax Calculation

+++

This recipe is to introduce how to calculate income & payroll tax liabilities from Taxcalc-Payroll. 

To be noticed, most functions from Tax-Calculator can be called from Taxcalc-Payroll. Usages are the same for two models.

+++

### Package Import

```{code-cell} ipython3
import taxcalcpayroll as tcp
import taxcalc as tc
```

### Setup
#### construct a Calculator object with Records and Policy

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol = tcp.Policy()
calc1 = tcp.Calculator(policy = pol, records = recs)
```

### Calculate & Results
#### Calculate income and payroll tax liabilites for the indicated year 

+++

#### single year usage

```{code-cell} ipython3
calc1.advance_to_year(2024)
calc1.calc_all()

print("Year 2024")
totiitax = calc1.weighted_total('iitax')
totpayroll = calc1.weighted_total('payrolltax')
print("total income tax revenue is: $", (totiitax/(10**9)).round(2), "Billion")
print("total payroll tax revenue is: $", (totpayroll/(10**9)).round(2), "Billion")
```

#### multi year usage

```{code-cell} ipython3
# multi year usage
for cyr in range(2024,2032):
    # advance to and calculate for specified cyr
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    print("Year ", cyr, ": total payroll tax revenue is ")
    totpayroll = calc1.weighted_total('payrolltax')
    print("$", (totpayroll/(10**9)).round(2), "Billions")
```
