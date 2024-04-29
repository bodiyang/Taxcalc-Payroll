History
=======

## Origins of Taxcalc-Payroll

Taxcalc-Payroll originates from [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator). 

In the past, Tax-Calculator was the only microsimulation model for both income tax analysis and payroll tax analysis. 

However, in the progess of model's expansion, , many payroll tax features were newly developed (for example, employer-side payroll tax offsetting). These developments go beyond the realm of Tax-Calculator, so it has become necessary to build Taxcalc-Payroll as a new platform to host them. 

From the perspective of model management, many research organizations build their tax model systems with an income tax model and payroll tax model. It is thus considered better to have Tax-Calculator and Taxcalc-Payroll separately serveing as an income tax calculator and a payroll tax calculator.

Taxcalc-Payroll inheritted the software infrastructure from Tax-Calculator. These two models are highly integrated, and most of their tax calculation functions can be called by each other. Users can still conduct both income and payroll tax analysis from either model.


