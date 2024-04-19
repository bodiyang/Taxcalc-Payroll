Model Interaction 
=======

Taxcalc-Payroll is the microsimulation model conducting the static analysis of federal individual income and payroll taxes, it interacts with other models to conduct higher level analysis, like revenue estimation and non-static analysis. 

Taxcalc-Payroll takes the input data (reweighted PUF and CPS data) from [Tax-Data](https://github.com/PSLmodels/taxdata) to conduct tax revenue estimation. Taxcalc-Payroll works with [Behavior Response Package](https://github.com/PSLmodels/Behavioral-Responses) to conduct the conventional analysis. 

To be noticed, Tax-Calculator and Taxcalc-Payroll are highly integrated. Users can call most of Tax-Calculator's functions from Taxcalc-Payroll. This means the user can do both income tax and payroll tax analysis from the model. (this also holds for Tax-Calculator)

Please refer to [AEI OSPC webpage](https://www.ospc.org/taxmodels/) for a more detailed documentation.