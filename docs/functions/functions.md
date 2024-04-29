Functions and Methodology
=======================

## Functions

Taxcalc-Payroll’s core functions are consisted of payroll tax liability calculation functions and the employer-side payroll offset function. The functions are hosted in `calcfunctions.py` and `payrolloffset.py`. 


## Payroll Tax Calculation Functions

### Brief

Payroll tax calculation functions are located in [`calcfunctions.py`](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/calcfunctions.py). The functions are used to calculate FICA and SECA tax liability.

`EI_PayrollTax`: Computes Old-Age, Survivors, and Disability Insurance (OASDI) and Hospital Insurance (HI) payroll taxes and earned income variables.

`AdditionalMedicareTax`: Computes additional Medicare tax (form 8959) included in payroll taxes.

The payroll tax calculation functions are inherited from Tax-Calculator and the usage remain the same. 
Please refer to this [recipe 1](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe1.html), as the guide for tax revenue estimations and projections.

## Employer Side Payroll Offset Function

### Brief

Whenever the government raises the payroll tax rate for the employers, it is expected that more revenue will be collected from the employer side. However, another effect happens simultaneously: a decrease in tax revenue from the employee side. This is known as the employer-side payroll offset effect.

The core function `employer_payroll_offset` is located in [payrolloffset.py](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/payrolloffset.py). The employer-side payroll offset function can be used to measure how reforming employer-side payroll tax policy would affect employee-side tax revenue.

Please refer to [Recipe 2](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe2.html) for the usage.


### Methodology

The modeling method follows the Joint Committee on Taxation’s document [THE INCOME AND PAYROLL TAX OFFSET TO CHANGES IN PAYROLL TAX REVENUES](https://www.jct.gov/publications/2016/jcx-89-16/).

We assume that total compensation from the employer to the employee always remains the same regardless of any implemented policy reforms.

Under this assumption, an increase on the employer-side payroll tax rate will result in a decrease in the employee's wages. The decrease in wages will then result in decreased of tax revenue from the employee side -- both income tax revenue and payroll tax revenue.

Total Compensation = Wage + Employer Side Payroll Tax Liability + Non-Taxable Benefit
 
Notes:
- Pension is included in the Wage variable.  
- Payroll tax consists of OASDI Social Security tax and Medicare HI tax.
- Non-taxable benefit is not considered in our model, because the PUF and CPS data sets do not capture the information of this item. (Non-taxable benefit's overall contribution to the value of total compensation should also not be very significant). 


So we consider wage and employer-side payroll for the total compensation calculation.

Total Compensation = Wage + Employer-side FICA Social Security Tax Liability + Employer-side FICA Medicare Tax Liability 

We will use the short note for variables below:
- Wages: Wages and pension, from employer paid to employee
- OASDIrate: Employer-side OASDI social security tax rate
- HIrate: Employer-side Medicare HI tax rate
- OASDImax: OASDI Social Security tax maximum taxable value


Note that OASDI Social Security tax had a maximum taxable value of $118,500 in 2016. Wages below this value will be taxed by their actual value; for wages above this value, the employee will be taxed by this OASDI maximum taxable value.


(1) For an employee whose wage is below the OASDI taxable maximum value,

Under the baseline policy:

$$
Total Compensation_{base} = Wage_{base} + Wage_{base} * OASDIrate_{base} + Wage_{base} * HIrate_{base}
$$

Under the reform policy:

$$
Total Compensation_{policy} = Wage_{policy} + Wage_{policy} * OASDIrate_{policy} + Wage_{policy} * HIrate_{policy}
$$

By combining the two equations above, we have:

$$
Wage_{policy} = \frac{Wage_{base} * (1 + OASDIrate_{base}+ HIrate_{base})}{1 + OASDIrate_{policy} + HIrate_{policy}}
$$

    
(2) For an employee whose wage is above the OASDI taxable maximum value,

Under the baseline policy:

$$
Total Compensation_{base} = Wage_{base} + OASDImax * OASDI_{base} + Wage_{base} * HI_{base}
$$

Under the reform policy:

$$
Total Compensation_{policy} = Wage_{policy} + OASDImax * OASDI_{policy} + Wage_{policy} * HI_{policy}
$$

By combining the two equations above, we have:

$$
Wage_{policy} = \frac{Total Compensation - OASDI_{policy} * OASDImax}{1 + HI_{policy}}
$$


We will then use the Wage after the reform and the offset effect to calculate the new income and payroll tax liability.


### Case Analysis

[Recipe 3](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe3.html) explains the offset effect. The recipe compares a payroll tax reform implemented upon the employer side versus the employee side. The result shows the latter reform will raise more revenue.

### Performance

It is known that Congressional Budget Office (CBO) considers offset effect when projecting revenues. Taxcalc-Payroll's performance is in line with the CBO's estimation.

For reference, this [document describing budget options](https://www.cbo.gov/budget-options/54805) shows CBO's estimation of revenue change from raising the Social Security payroll tax rate by 1 percent (0.5 percent on the employer and employee sides each). Note that this document was produced in 2018, so be aware of the inflation effect when comparing Taxcalc-Payroll's estimation (based on current year) with this CBO document (estimations based on 2018).
