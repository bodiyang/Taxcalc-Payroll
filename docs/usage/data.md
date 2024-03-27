Data for Taxcalc-Payroll
=======================

A Taxcalc-Payroll `Records` object is created by passing a Pandas DataFrame or a string that provides the path to a CSV file with data you'd like to use in Taxcalc-Payroll.


## TaxData

To make Taxcalc-Payroll more useful out of the box, it ships with two data options for users, both of which are created by the [TaxData](https://github.com/PSLmodels/TaxData) project.  We refer users to that project for more specific documentation of these data, but we provide a brief overview of the two data options provided by TaxData that come with a Taxcalc-Payroll installation.

### Current Population Survey Data

Using the `Records.cps_constructor()` method to create a `Records` class object, Taxcalc-Payroll users will be loading the `taxdata` Current Population Survey (CPS) data file. This file is based on publicly available survey data, which is then weighted via `taxdata` to hit IRS/SOI targets.  The data are then grown out to hit aggregate forecasts through the time horizon available in Taxcalc-Payroll (approximately the next 10 years).

Taxcalc-Payroll provides unit tests to ensure that certain totals are hit with the CPS-based file.  However, users should note that these tests are simply to ensure **the accuracy of Taxcalc-Payroll's tax logic** and **not the accuracy of the CPS-based data file produced by `taxdata`**.  Please see the [TaxData](https://github.com/PSLmodels/TaxData) documentation for any validation of those data.

### The IRS Public Use File

The `taxdata` package also produces a weights file and growth factors file for use with the IRS-SOI Public Use File (PUF).  A given `taxdata` version typically produces these files for a specific vintage of the PUF.  As of `taxdata` v 0.3.1, the 2012 PUF is used.

For users who have purchased their own version of the PUF, the `puf_weights.csv.gz` and `growfactors.csv` files that are included in Taxcalc-Payroll can be used to create a PUF-based dataset suitable for use in Taxcalc-Payroll.

We refer users of the PUF to the IRS limitations on the use of those data and their distribution.  We also refer users of the PUF weights file and grow factors to the [TaxData](https://github.com/PSLmodels/TaxData) documentation for details on how to use these files with the PUF and to see how well the resulting tax calculations hit aggregate targets published by the IRS.  However, we do note that analysis with a PUF-based data file tends to be the most accurate and validation of Taxcalc-Payroll with other microsimulation models often uses a PUF-based data file.

## Using other data in Taxcalc-Payroll

Using other data sources in Taxcalc-Payroll is possible.  Users can pass any csv file to the `Records` class and, so long as it has the appropriate [input variables](https://taxcalc.pslmodels.org/guide/input_vars.html), one may be able to obtain results.  Using Taxcalc-Payroll with custom data takes care and significant understanding of the model and data.  Those interested in using their own data in Taxcalc-Payroll might also look to the [Tax-Cruncher](https://github.com/PSLmodels/Tax-Cruncher) project, which is built as an interface between Taxcalc-Payroll and custom datasets.

