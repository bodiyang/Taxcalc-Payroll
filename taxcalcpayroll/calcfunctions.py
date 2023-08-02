"""
Tax-Calculator functions that calculate payroll and individual income taxes.

These functions are imported into the Calculator class.

Note: the parameter_indexing_CPI_offset policy parameter is the only
policy parameter that does not appear here; it is used in the policy.py
file to possibly adjust the price inflation rate used to index policy
parameters (as would be done in a reform that introduces chained-CPI
indexing).
"""
# CODING-STYLE CHECKS:
# pycodestyle calcfunctions.py
# pylint --disable=locally-disabled calcfunctions.py
#
# pylint: disable=too-many-lines
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

import math
import copy
import numpy as np
from taxcalc.decorators import iterate_jit, JIT
import taxcalc as tc



@iterate_jit(nopython=True)
def EI_PayrollTax(SS_Earnings_c, e00200p, e00200s, pencon_p, pencon_s,
                  FICA_ss_trt, FICA_mc_trt, ALD_SelfEmploymentTax_hc,
                  SS_Earnings_thd, SECA_Earnings_thd,
                  e00900p, e00900s, e02100p, e02100s, k1bx14p,
                  k1bx14s, payrolltax, ptax_was, setax, c03260, ptax_oasdi,
                  sey, earned, earned_p, earned_s,
                  was_plus_sey_p, was_plus_sey_s):
    """
    Compute part of total OASDI+HI payroll taxes and earned income variables.

    Parameters
    ----------
    SS_Earnings_c: float
        Maximum taxable earnings for Social Security.
        Individual earnings below this amount are subjected to OASDI payroll tax.
        This parameter is indexed by rate of growth in average wages not by the price inflation rate.
    e00200p: float
        Wages, salaries, and tips for taxpayer net of pension contributions
    e00200s: float
        Wages, salaries, and tips for spouse net of pension contributions
    pencon_p: float
        Contributions to defined-contribution pension plans for taxpayer
    pencon_s: float
        Contributions to defined-contribution pension plans for spouse
    FICA_ss_trt: float
        Social security payroll tax rate, including both employer and employee
    FICA_mc_trt: float
        Medicare payroll tax rate, including both employer and employee
    ALD_SelfEmploymentTax_hc: float
        Adjustment for self-employment tax haircut
        If greater than zero, reduces the employer equivalent portion of self-employment adjustment
        Final adjustment amount = (1-Haircut)*SelfEmploymentTaxAdjustment
    SS_Earnings_thd: float
        Additional taxable earnings threshold for Social Security
        Individual earnings above this threshold are subjected to OASDI payroll tax, in addtion to
        earnings below the maximum taxable earnings threshold.
    SECA_Earnings_thd: float
        Threshold value for self-employment income below which there is
        no SECA tax liability
    e00900p: float
        Schedule C business net profit/loss for taxpayer
    e00900s: float
        Schedule C business net profit/loss for spouse
    e02100p: float
        Farm net income/loss for taxpayer
    e02100s: float
        Farm net income/loss for spouse
    k1bx14p: float
        Partner self-employment earnings/loss for taxpayer (included in e26270 total)
    k1bx14s: float
        Partner self-employment earnings/loss for spouse (included in e26270 total)
    payrolltax: float
        Total (employee and employer) payroll tax liability
        payrolltax = ptax_was + setax + ptax_amc
    ptax_was: float
        Employee and employer OASDI plus HI FICA tax
    setax: float
        Self-employment tax
    c03260: float
        Deductible part of self-employment tax
        c03260 = (1 - ALD_SelfEmploymentTax_hc) * 0.5 * setax
    ptax_oasdi: float
        Employee and employer OASDI FICA tax plus self employment tax
        Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
    sey: float
        Total self-employment income for filing unit
    earned: float
        Earned income for filing unit
    earned_p: float
        Earned income for taxpayer
    earned_s: float
        Earned income for spouse
    was_plus_sey_p: float
        Wage and salary income plus taxable self employment income for taxpayer
    was_plus_sey_s: float
        Wage and salary income plus taxable self employment income for spouse

    Returns
    -------
    sey: float
        Total self-employment income for filing unit
    payrolltax: float
        Total (employee and employer) payroll tax liability
        payrolltax = ptax_was + setax + ptax_amc
    ptax_was: float
        Employee and employer OASDI plus HI FICA tax
    setax: float
        Self-employment tax
    c03260: float
        Deductible part of self-employment tax
        c03260 = (1 - ALD_SelfEmploymentTax_hc) * 0.5 * setax
    ptax_oasdi: float
        Employee and employer OASDI FICA tax plus self employment tax
        Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
    earned: float
        Earned income for filing unit
    earned_p: float
        Earned income for taxpayer
    earned_s: float
        Earned income for spouse
    was_plus_sey_p: float
        Wage and salary income plus taxable self employment income for taxpayer
    was_plus_sey_s: float
        Wage and salary income plus taxable self employment income for spouse
    """
    # compute sey and its individual components
    sey_p = e00900p + e02100p + k1bx14p
    sey_s = e00900s + e02100s + k1bx14s
    sey = sey_p + sey_s  # total self-employment income for filing unit

    # compute gross wage and salary income ('was' denotes 'wage and salary')
    gross_was_p = e00200p + pencon_p
    gross_was_s = e00200s + pencon_s

    # compute taxable gross earnings for OASDI FICA
    txearn_was_p = min(SS_Earnings_c, gross_was_p)
    txearn_was_s = min(SS_Earnings_c, gross_was_s)

    # compute OASDI and HI payroll taxes on wage-and-salary income, FICA
    ptax_ss_was_p = FICA_ss_trt * txearn_was_p
    ptax_ss_was_s = FICA_ss_trt * txearn_was_s
    ptax_mc_was_p = FICA_mc_trt * gross_was_p
    ptax_mc_was_s = FICA_mc_trt * gross_was_s
    ptax_was = ptax_ss_was_p + ptax_ss_was_s + ptax_mc_was_p + ptax_mc_was_s

    # compute taxable self-employment income for OASDI SECA
    sey_frac = 1.0 - 0.5 * (FICA_ss_trt + FICA_mc_trt)
    txearn_sey_p = min(max(0., sey_p * sey_frac), SS_Earnings_c - txearn_was_p)
    txearn_sey_s = min(max(0., sey_s * sey_frac), SS_Earnings_c - txearn_was_s)

    # compute self-employment tax on taxable self-employment income, SECA
    setax_ss_p = FICA_ss_trt * txearn_sey_p
    setax_ss_s = FICA_ss_trt * txearn_sey_s
    setax_mc_p = FICA_mc_trt * max(0., sey_p * sey_frac)
    setax_mc_s = FICA_mc_trt * max(0., sey_s * sey_frac)
    setax_p = setax_ss_p + setax_mc_p
    setax_s = setax_ss_s + setax_mc_s
    setax = setax_p + setax_s
    # # no tax if low amount of self-employment income
    if sey * sey_frac > SECA_Earnings_thd:
        setax = setax_p + setax_s
    else:
        setax = 0.0

    # compute extra OASDI payroll taxes on the portion of the sum
    # of wage-and-salary income and taxable self employment income
    # that exceeds SS_Earnings_thd
    sey_frac = 1.0 - 0.5 * FICA_ss_trt
    was_plus_sey_p = gross_was_p + max(0., sey_p * sey_frac)
    was_plus_sey_s = gross_was_s + max(0., sey_s * sey_frac)
    extra_ss_income_p = max(0., was_plus_sey_p - SS_Earnings_thd)
    extra_ss_income_s = max(0., was_plus_sey_s - SS_Earnings_thd)
    extra_payrolltax = (extra_ss_income_p * FICA_ss_trt +
                        extra_ss_income_s * FICA_ss_trt)

    # compute part of total payroll taxes for filing unit
    # (the ptax_amc part of total payroll taxes for the filing unit is
    # computed in the AdditionalMedicareTax function below)
    payrolltax = ptax_was + setax + extra_payrolltax

    # compute OASDI part of payroll taxes
    ptax_oasdi = (ptax_ss_was_p + ptax_ss_was_s +
                  setax_ss_p + setax_ss_s +
                  extra_payrolltax)

    # compute earned* variables and AGI deduction for
    # "employer share" of self-employment tax, c03260
    # Note: c03260 is the amount on 2015 Form 1040, line 27
    c03260 = (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax
    earned = max(0., e00200p + e00200s + sey - c03260)
    earned_p = max(0., (e00200p + sey_p -
                        (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_p))
    earned_s = max(0., (e00200s + sey_s -
                        (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_s))
    return (sey, payrolltax, ptax_was, setax, c03260, ptax_oasdi,
            earned, earned_p, earned_s, was_plus_sey_p, was_plus_sey_s)



@iterate_jit(nopython=True)
def AdditionalMedicareTax(e00200, MARS,
                          AMEDT_ec, sey, AMEDT_rt,
                          FICA_mc_trt, FICA_ss_trt,
                          ptax_amc, payrolltax):
    """
    Computes Additional Medicare Tax (Form 8959) included in payroll taxes.

    Parameters
    -----
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    AMEDT_ec: list
        Additional Medicare Tax earnings exclusion
    AMEDT_rt: float
        Additional Medicare Tax rate
    FICA_ss_trt: float
        FICA Social Security tax rate
    FICA_mc_trt: float
        FICA Medicare tax rate
    e00200: float
        Wages and salaries
    sey: float
        Self-employment income
    ptax_amc: float
        Additional Medicare Tax
    payrolltax: float
        payroll tax augmented by Additional Medicare Tax

    Returns
    -------
    ptax_amc: float
        Additional Medicare Tax
    payrolltax: float
        payroll tax augmented by Additional Medicare Tax
    """
    line8 = max(0., sey) * (1. - 0.5 * (FICA_mc_trt + FICA_ss_trt))
    line11 = max(0., AMEDT_ec[MARS - 1] - e00200)
    ptax_amc = AMEDT_rt * (max(0., e00200 - AMEDT_ec[MARS - 1]) +
                           max(0., line8 - line11))
    payrolltax += ptax_amc
    return (ptax_amc, payrolltax)

