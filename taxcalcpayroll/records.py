"""
Taxcalc-Payroll tax-filing-unit Records class.
"""
# CODING-STYLE CHECKS:
# pycodestyle records.py
# pylint --disable=locally-disabled records.py

from taxcalc.records import Records as TCRec


class Records(TCRec):
    """
    Records is a subclass of Tax-Calculator's Records class.
    In fact, Taxcalc-Payroll's Records class is excatly the same as 
    the Tax-Calculator's Records class.
    Therefore, inherits its methods (none of which are shown here).

    Constructor for the tax-filing-unit Records class.

    Returns
    -------
    class instance: Records

    Notes
    -----
    Typical usage when using PUF input data is as follows::

        recs = Records()

    which uses all the default parameters of the constructor, and
    therefore, imputed variables are generated to augment the data and
    initial-year grow factors are applied to the data.  There are
    situations in which you need to specify the values of the Record
    constructor's arguments, but be sure you know exactly what you are
    doing when attempting this.

    Use Records.cps_constructor() to get a Records object instantiated
    with CPS input data.
    """
    # suppress pylint warning about constructor having too many arguments:
    # pylint: disable=too-many-arguments
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    pass