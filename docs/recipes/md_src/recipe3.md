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

# Recipe3: Comparison of Different Payroll Tax Reforms 

+++

This Receipe is to compare the difference between the payroll tax reforms implemented upon the employer side and the employee side. The payroll tax reform implemented upon the employer side will come with an offset, while the reform on employee side will not come with offset. The hypothesis is that the employee side reform will generate more revenue.

```{code-cell} ipython3
import taxcalcpayroll as tcp
import taxcalc as tc
from taxcalcpayroll.payrolloffset import employer_payroll_offset
```

#### reform 1: rise 1% employer side FICA social security
#### reform 2: rise 1% employee side FICA social security

+++

baseline policy

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol = tcp.Policy()
calc0 = tcp.Calculator(policy = pol, records = recs)
```

reform 1: to rise 1% employer side FICA social security 

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol1 = tcp.Policy()
reform1 = {'FICA_ss_trt_employer': {"2025": 0.072}}
pol1.implement_reform(reform1, print_warnings=True, raise_errors=True)
calc1 = tcp.Calculator(policy = pol1, records = recs)
```

reform 2: to rise 1% employee side FICA social security 

```{code-cell} ipython3
recs = tcp.Records(data = 'puf.csv')
pol2 = tcp.Policy()
reform2 = {'FICA_ss_trt_employee': {"2025": 0.072}}
pol2.implement_reform(reform2, print_warnings=True, raise_errors=True)
calc2 = tcp.Calculator(policy = pol2, records = recs)
```

## Calculated total tax revenue for the future years 

```{code-cell} ipython3
for year in range(2023, 2031):   
    print("year: ", year)
    calc0.advance_to_year(year)
    calc0.calc_all()
    itax_rev0 = calc0.weighted_total('combined')
    print("current law combined tax revenue: $", (itax_rev0/10**9).round(2), "Billions")
    print(" ")
    print("reform 1 to rise 1% employer side FICA social security ")
    calc1.advance_to_year(year)
    calc1.calc_all()
    itax_rev1 = calc1.weighted_total('combined')
    print("reformed law combined tax revenue: $", (itax_rev1/10**9).round(2), "Billions")
    offset_df = employer_payroll_offset(reform1, calc0, pol, recs, dump=False)
    itax_revbr = (offset_df['combined'] * offset_df['s006']).sum()
    print("offset combined tax revenue: ", (itax_revbr/10**9).round(2), "Billions")
    print(" ")
    print("reform 2 to rise 1% employee side FICA social security ")
    calc2.advance_to_year(year)
    calc2.calc_all()
    itax_rev2 = calc2.weighted_total('combined')
    print("reformed law combined tax revenue: $", (itax_rev2/10**9).round(2), "Billions")
    offset_df2 = employer_payroll_offset(reform2, calc0, pol, recs, dump=False)
    itax_revbr2 = (offset_df2['combined'] * offset_df2['s006']).sum()
    print("offset combined tax revenue: ", (itax_revbr2/10**9).round(2), "Billions")
    print(" ")
```

### Case example, for the year 2030:

#### Baseline Policy: 
combined tax revenue: $ 5139.73 Billions

#### Reform 1 to rise 1% employer side FICA social security
combined tax revenue (before offset applied): $ 5262.54 Billions

combined tax revenue with offset applied:  5221.78 Billions

#### Reform 2 to rise 1% employee side FICA social security 
combined tax revenue (before offset applied): $ 5262.54 Billions

combined tax revenue with offset applied:  5262.54 Billions
