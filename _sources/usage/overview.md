Structural overview
===================

Taxcalc-Payroll has been designed using [object-oriented programming (OOP)](https://www.programiz.com/python-programming/object-oriented-programming)
principles.
There are seven classes and a collection of global utility functions,
but most Python programming involves using only a few methods in three classes.

## Quick summary

Typical Taxcalc-Payroll usage involves creating two Calculator class objects:
both containing the same sample of filing units (that is, Records class object),
but each containing a different tax policy (that is, Policy class object).
The idea is to compare the calculated tax liabilities of the sample units under
the two different tax policies,
one of which is usually current-law policy and the other is a tax reform of
interest.

*   `rec` → Records class object.  
    Created by `Records()` when containing IRS-SOI-PUF-derived filing-unit data
    or created by `Records.cps_constructor()` when containing CPS-derived
    filing-unit data.

*   `clp` → `Policy` class object containing parameters that characterize
current-law policy.  
    Created by `Policy()`.

*   `ref` → `Policy` class object containing parameters that characterize a tax
reform.  
    Created using a Python dictionary `refdict` representing the reform by
    using the `implement_reform(refdict)` method on a `Policy` object created
    by `Policy()`.
    Or created using a JSON file `filename` representing the reform by using
    the `implement_reform(Policy.read_json_reform(filename))` method on a
    `Policy` object created by `Policy()`.

*   `calc_clp` → Calculator class object for current-law policy.  
    Created by `Calculator(records=rec, policy=clp)`.

*   `calc_ref` → Calculator class object for reform policy.  
    Created by `Calculator(records=rec, policy=ref)`.

*   `calc_all()` → Calculator class method that computes tax liability
(and many intermediate variables such as AGI) for each filing-unit.

*   `itax_clp` → Variable containing aggregate income tax liability under
current-law policy.  
    Created by `weighted_total('iitax')` method called on `calc_clp` object
    after `calc_all()` called.

*   `diff_table` → Pandas DataFrame object containing reform-minus-current-law
difference table for income tax liability by expanded-income deciles.  
    Created by
    `calc_clp.difference_table(calc_ref, 'weighted_deciles', 'iitax')` method
    called after `calc_all()` has been called on both Calculator objects.

For examples of Python scripts that use these classes and methods, see
{doc}`../recipes/index`.

For detailed documentation and source code for these three classes, see:

*   [records.py](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py)
for Records class and all its methods.
*   [policy.py](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py)
for Policy class and all its methods.
*   [calculator.py](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py)
for Calculator class and all its methods.

## Complete story

Taxcalc-Payroll contains a series of basic classes and global utility
functions, that together provide the full range of Taxcalc-Payroll capabilities.
Here is a description of their role in Taxcalc-Payroll and a link to each the
detailed documentation and source code for each class and all its methods.

### Classes

*   `Records` → Derived from `Data` and contains attributes of each tax filing
unit.  
    Documentation and source code are in
    [records.py](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/records.py).

*   `Policy` → Derived from `Parameters` and contains tax policy parameters.  
    Documentation and source code are in
    [policy.py](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/policy.py).

*   `Calculator` → Contains a `Policy` class object, a `Records` class object,
and a `Consumption` class object, plus functions that contain the logic
required to calculate income and payroll tax liability for each filing unit.  
    Documentation and source code are in
    [calculator.py](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/calculator.py) and in
    [calcfunctions.py](https://github.com/bodiyang/Taxcalc-Payroll/blob/master/taxcalcpayroll/calcfunctions.py).

