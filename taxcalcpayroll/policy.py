"""
Taxcalc-Payroll federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pycodestyle policy.py
# pylint --disable=locally-disabled policy.py

from taxcalc.policy import Policy as TCPol


class Policy(TCPol):
    """
    Policy is a subclass of the Tax-Calculator's Policy class, 
    In fact, Taxcalc-Payroll's Policy class is excatly the same as 
    the Tax-Calculator's Policy class.
    Therefore, inherits its methods (none of which are shown here).

    Constructor for the federal tax policy class.

    Returns
    -------
    class instance: Policy
    """
    pass