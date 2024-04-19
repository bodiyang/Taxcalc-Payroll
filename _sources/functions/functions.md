Functions & Methodology
=======================

## Functions

Core functions of Taxcalc-Payroll are consisted of the payroll tax liability calculation functions and the employer side payroll offset function. The functions are are hosted in `calcfunctions.py` and `payrolloffset.py`. 


## Payroll Tax Calculation Functions

### Brief

Payroll tax calculation functions are located in [`calcfunctions.py`](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/calcfunctions.py). The functions are used to calculate FICA and SECA tax liability.

`EI_PayrollTax`: Compute part of total OASDI+HI payroll taxes and earned income variables.

`AdditionalMedicareTax`: Computes Additional Medicare Tax (Form 8959) included in payroll taxes.

The payroll tax calculation functions are inherited from Tax-Calculator and the usage remain the same. 
Please refer to this [recipe 1](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe1.html), as the guide for tax revenue estimations and projections.

## Employer Side Payroll Offset Function

### Brief

Whenever government has a policy reform to raise the payroll tax rate from the employer, it is expected that more revenue would be collected from the employer side. However, another effect would happen at the same time, that there would be a decrease of the tax revenue from the employee side. This is known to be the employer side payroll offset effect.

Core function `employer_payroll_offset` is located in [payrolloffset.py](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/payrolloffset.py). Employer side payroll offset function can be used to measure the effect of employee side tax revenue offset, from a policy reform of the employer side payroll tax. 

Please refer to [recipe 2](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe2.html) for the usage.


### Methodology

Modeling method follows the JCT article [THE INCOME AND PAYROLL TAX OFFSET TO CHANGES IN PAYROLL TAX REVENUES](https://www.jct.gov/publications/2016/jcx-89-16/).

We hold the assumption that total compensation from the employer to the employee always remain the same regardless of any implemented policy reforms.

Under this assumption, an increase on the employer side payroll tax rate will result in a decrease in the employee's wages. The decrease of wages will then result in a decrease of tax revenue from the employee side, both income tax revenue and payroll tax revenue.

Total Compensation = Wage + Employer Side Payroll Tax Liability + Non-Taxable Benefit
 
Note:
- Pension is included in the Wage variable  
- Payroll tax is consisted of OASDI social security tax and HI medicare hospital insurance tax
- Non-taxable benefit is not considered in our model, because our data sets (PUF & CPS) do not capture the information of this item. (The overall contribution from non-taxable benefit to the value of total compensation should also not be very significant). 


So we consider wage and employer side payroll for total compensation calculation.

Total Compensation = Wage + Employer side FICA Social Security Tax Liability + Employer side FICA Medicare Tax Liability 

We will use the short note for variables below:
- Wages: wages and pension, from employer paid to employee
- OASDIrate: employer side OASDI social security tax rate
- HIrate: employer side HI medicare hospital insurance tax rate
- OASDImax: OASDI social security tax maximum taxable value


To be noticed, OASDI social security tax have a maximum taxable value, $118500 in 2016. For wages below this value, the wages will be taxed by the actual value of the wages; for wages above this value, the employee will be taxed by this OASDI maximum taxable value.


(1) For employee whose wage is below the OASDI taxable maximum value:

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

    
(2) For employee whose wage is above the OASDI taxable maximum value:

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


We will then use the Wage after the reform & offset effect to calculate the new income and payroll tax liability.


### Case Analysis

This [recipe 3](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe3.html) will be helpful to learn the effect from offset. The recipe is a comparison between a payroll tax reform implemented upon the employer side versus the employee side. Result shows the latter reform will raise more revenue.

### Performance

It is known that Congressional Budget Office take the offset effect into consideration when producing revenue projections. Taxcalc-Payroll's performance is in line with the CBO's estimation.

As a reference, this [document of budget options](https://www.cbo.gov/budget-options/54805) shows CBO's estimation of revenue change from the rise of Social Security payroll tax rate by 1% (0.5% on each side of employer and employee). Please be noted that this document is produced in 2018. So we need to be aware of the inflation effect when we compare Taxcalc-Payroll's estimation (current year) with this CBO document (2018).
