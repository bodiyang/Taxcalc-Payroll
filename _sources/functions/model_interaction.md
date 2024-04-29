Model Interaction 
=======

Taxcalc-Payroll is a microsimulation model that conducts the static analysis of federal individual income and payroll taxes. It interacts with other models to conduct higher-level analysis, such as revenue estimation and non-static analysis. 

Taxcalc-Payroll takes the input data (re-weighted PUF and CPS data) from [Tax-Data](https://github.com/PSLmodels/taxdata) to conduct tax revenue estimation. Taxcalc-Payroll works with the [Behavioral-Responses package](https://github.com/PSLmodels/Behavioral-Responses) to conduct the conventional analysis. 

Note that Tax-Calculator and Taxcalc-Payroll are highly integrated. Users can call most of Tax-Calculator's functions from Taxcalc-Payroll. This means the user can perform both income tax and payroll tax analysis with the model. (this also holds for Tax-Calculator.)

Please refer to [AEI's OSPC webpage](https://www.ospc.org/taxmodels/) for a more detailed documentation.