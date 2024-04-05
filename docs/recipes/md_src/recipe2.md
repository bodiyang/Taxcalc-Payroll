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

# Recipe2: Employer side Payroll Tax Offset 

+++

This recipe is to introduce the usage of ` employer_payroll_offset` function from `payrolloffset.py`, when calling the function to conduct analysis upon employer side payroll tax reform

```{code-cell} ipython3
import taxcalcpayroll as tcp
import taxcalc as tc
from taxcalcpayroll.payrolloffset import employer_payroll_offset
```

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol = tcp.Policy()
calc0 = tcp.Calculator(policy = pol, records = recs)
```

### policy reform: increase the employer side FICA social security payroll tax rate to 0.072, for the year 2025 

```{code-cell} ipython3
reform1 = {'FICA_ss_trt_employer': {"2025": 0.072}}
```

### (1) Calculate the total tax revenue after the reform (without offset)

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol1 = tcp.Policy()
pol1.implement_reform(reform1, print_warnings=True, raise_errors=True)
calc1 = tcp.Calculator(policy = pol1, records = recs)

calc1.advance_to_year(2025)
calc1.calc_all()
print("In 2025, combined tax revenue under reformed policy (without offset) is: ", calc1.weighted_total('combined') / 10**9)
```

### (2) Calculate the total tax revenue after the reform, considering the offset

```{code-cell} ipython3
calc0.advance_to_year(2025)
calc0.calc_all()
```

### Function usage:
Input for offset function: baseline calculator (its policy and records object) and reform policy 

Output for offset function: returns a dataframe of output variables

```{code-cell} ipython3
offdf = employer_payroll_offset(reform1, calc0, pol, recs, dump=False)    
```

print the result of calculated combined tax revenue

```{code-cell} ipython3
print("In 2025, combined tax revenue under reformed policy, after the offset, is: ", (offdf['combined'] * offdf['s006']).sum() / 10**9)
```

## Muti year usage

+++

### Comparison of total tax revenue calculation of baseline policy, reform policy (without offset), and reform policy considering offset

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol = tcp.Policy()
calc0 = tcp.Calculator(policy = pol, records = recs)

recs = tcp.Records(data = 'puf.csv')
pol1 = tcp.Policy()
pol1.implement_reform(reform1, print_warnings=True, raise_errors=True)
calc1 = tcp.Calculator(policy = pol1, records = recs)
```

```{code-cell} ipython3
for year in range(2023, 2031):   
    print("year: ", year)
    calc0.advance_to_year(year)
    calc0.calc_all()
    itax_rev0 = calc0.weighted_total('combined')
    print("current law combined tax revenue: $", (itax_rev0/10**9).round(2), "Billions")
    calc1.advance_to_year(year)
    calc1.calc_all()
    itax_rev1 = calc1.weighted_total('combined')
    print("reformed law combined tax revenue: $", (itax_rev1/10**9).round(2), "Billions")
    offset_df = employer_payroll_offset(reform1, calc0, pol, recs, dump=False)
    itax_revbr = (offset_df['combined'] * offset_df['s006']).sum()
    print("offset combined tax revenue: ", (itax_revbr/10**9).round(2), "Billions")
    print(" ")
    
```
