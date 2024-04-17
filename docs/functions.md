Functions
=======================

## Functions

Core functions of Taxcalc-Payroll are consisted of the payroll tax liability calculation functions and the employer side payroll offset function. The functions are are hosted in `calcfunctions.py` and `payrolloffset.py`. 

Payroll tax liability functions can be used to calculate the FICA and SECA tax liability. These functions are inherited from Tax-Calculator and the usage remain the same. Please refer to this [recipe 1](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe1.html), as the guide for tax revenue estimations and projections.

Employer side payroll offset function can be used to measure the effect of employee side tax revenue offset, from a policy reform of the employer side payroll tax. Please refer to [recipe 2](https://bodiyang.github.io/Taxcalc-Payroll/recipes/recipe2.html).


## Employer Side Payroll Offset Function


### Brief

Whenever government has a policy reform to raise the payroll tax rate from the employer, it is expected that more revenue would be collected from the employer side. However, another effect would happen at the same time, that there would be a decrease of the tax revenue from the employee side. This is known to be the employer side payroll offset effect.


### Methodology

Modeling method follows the JCT article [THE INCOME AND PAYROLL TAX OFFSET TO CHANGES IN PAYROLL TAX REVENUES](https://www.jct.gov/publications/2016/jcx-89-16/).

We hold the assumption that total compensation from the employer to the employee always remain the same regardless of any implemented policy reforms.

Under this assumption, an increase on the employer side payroll tax rate will result in a decrease in the employee's wages. The decrease of wages will then result in a decrease of tax revenue from the employee side, both income tax revenue and payroll tax revenue.

$\
Total Compensation = Wage + Employer Side Payroll Tax Liability + Non-Taxable Benefit
$
 

Note:
- Pension is included in the Wage variable  
- Payroll tax is consisted of OASDI social security tax and HI medicare hospital insurance tax
- Non-taxable benefit is not considered in our model, because our data sets (PUF & CPS) do not capture the information of this item. (The overall contribution from non-taxable benefit to the value of total compensation should also not be very significant). 


So we consider the following components for total compensation calculation: 

$$\
Wages: wages and pension, from employer paid to employee
FICA_ss_employer: employer side OASDI social security tax liability 
FICA_mc_employer: employer side HI medicare hospital insurance tax liability
$$

$$\
Total Compensation = Wage + FICA_ss_employer + FICA_mc_employer
$$

To be noticed, OASDI social security tax have a maximum taxable value, $118500 in 2016. For wages below this value, the wages will be taxed by the actual value of the wages; for wages above this value, the employee will be taxed by this OASID maximum taxable value.

(1) For employee whose wage is below the OASDI taxable maximum value:

Under the baseline policy:

$$
Total Compensation_{base} = Wage_{base} + Wage_{base} * FICA_ss_employer tax rate_{base} + Wage_{base} * FICA_mc_employer tax rate_{base}
$$

Under the reform policy:

$$
Total Compensation_{policy} = Wage_{policy} + Wage_{policy} * FICA_ss_employer tax rate_{policy} + Wage_{policy} * FICA_mc_employer tax rate_{policy}
$$

By combining the two equations above, we have:

$$
Wage_{policy} = \frac{Wage_base * (1 + FICA_ss_employer tax rate_base+ FICA_mc_employer tax rate_base)}{1 + FICA_ss_employer tax rate_policy + FICA_mc_employer tax rate_policy}
$$

    
(2) For employee whose wage is above the OASDI taxable maximum value:

Under the baseline policy:

$$
Total Compensation_{base} = Wage_{base} + OASDI max taxable amount * FICA_ss_employer tax rate_{base} + Wage_{base} * FICA_mc_employer tax rate_{base}
$$

Under the reform policy:

$$
Total Compensation_{policy} = Wage_{policy} + OASDI max taxable amount * FICA_ss_employer tax rate_{policy} + Wage_{policy} * FICA_mc_employer tax rate_{policy}
$$

By combining the two equations above, we have:

$$
Wage_{policy} = \frac{Total Compensation - FICA_ss_employer tax rate_policy * OASDI max taxable amount}{1 + FICA_mc_employer tax rate_policy}
$$


    





### Performance 

