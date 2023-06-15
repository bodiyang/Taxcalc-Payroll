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


def BenefitPrograms(calc):
    """
    Calculate total government cost and consumption value of benefits
    delivered by non-repealed benefit programs.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline

    Returns
    -------
    None:
        The function modifies calc
    """
    # zero out benefits delivered by repealed programs
    zero = np.zeros(calc.array_len)
    if calc.policy_param('BEN_housing_repeal'):
        calc.array('housing_ben', zero)
    if calc.policy_param('BEN_ssi_repeal'):
        calc.array('ssi_ben', zero)
    if calc.policy_param('BEN_snap_repeal'):
        calc.array('snap_ben', zero)
    if calc.policy_param('BEN_tanf_repeal'):
        calc.array('tanf_ben', zero)
    if calc.policy_param('BEN_vet_repeal'):
        calc.array('vet_ben', zero)
    if calc.policy_param('BEN_wic_repeal'):
        calc.array('wic_ben', zero)
    if calc.policy_param('BEN_mcare_repeal'):
        calc.array('mcare_ben', zero)
    if calc.policy_param('BEN_mcaid_repeal'):
        calc.array('mcaid_ben', zero)
    if calc.policy_param('BEN_oasdi_repeal'):
        calc.array('e02400', zero)
    if calc.policy_param('BEN_ui_repeal'):
        calc.array('e02300', zero)
    if calc.policy_param('BEN_other_repeal'):
        calc.array('other_ben', zero)
    # calculate government cost of all benefits
    cost = np.array(
        calc.array('housing_ben') +
        calc.array('ssi_ben') +
        calc.array('snap_ben') +
        calc.array('tanf_ben') +
        calc.array('vet_ben') +
        calc.array('wic_ben') +
        calc.array('mcare_ben') +
        calc.array('mcaid_ben') +
        calc.array('e02400') +
        calc.array('e02300') +
        calc.array('ubi') +
        calc.array('other_ben')
    )
    calc.array('benefit_cost_total', cost)
    # calculate consumption value of all benefits
    # (assuming that cash benefits have full value)
    value = np.array(
        calc.array('housing_ben') * calc.consump_param('BEN_housing_value') +
        calc.array('ssi_ben') +
        calc.array('snap_ben') * calc.consump_param('BEN_snap_value') +
        calc.array('tanf_ben') * calc.consump_param('BEN_tanf_value') +
        calc.array('vet_ben') * calc.consump_param('BEN_vet_value') +
        calc.array('wic_ben') * calc.consump_param('BEN_wic_value') +
        calc.array('mcare_ben') * calc.consump_param('BEN_mcare_value') +
        calc.array('mcaid_ben') * calc.consump_param('BEN_mcaid_value') +
        calc.array('e02400') +
        calc.array('e02300') +
        calc.array('ubi') +
        calc.array('other_ben') * calc.consump_param('BEN_other_value')
    )
    calc.array('benefit_value_total', value)


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


@iterate_jit(nopython=True)
def RefundablePayrollTaxCredit(was_plus_sey_p, was_plus_sey_s,
                               RPTC_c, RPTC_rt,
                               rptc_p, rptc_s, rptc):
    """
    Computes refundable payroll tax credit amounts.

    Parameters
    ----------
    was_plus_sey_p: float
        Wage and salary income plus taxable self employment income for taxpayer
    was_plus_sey_s: float
        Wage and salary income plus taxable self employment income for spouse
    RPTC_c: float
        Maximum refundable payroll tax credit
    RPTC_rt: float
        Refundable payroll tax credit phasein rate
    rptc_p: float
        Refundable Payroll Tax Credit for taxpayer
    rptc_s: float
        Refundable Payroll Tax Credit for spouse
    rptc: float
        Refundable Payroll Tax Credit for filing unit

    Returns
    -------
    rptc_p: float
        Refundable Payroll Tax Credit for taxpayer
    rptc_s: float
        Refundable Payroll Tax Credit for spouse
    rptc: float
        Refundable Payroll Tax Credit for filing unit
    """
    rptc_p = min(was_plus_sey_p * RPTC_rt, RPTC_c)
    rptc_s = min(was_plus_sey_s * RPTC_rt, RPTC_c)
    rptc = rptc_p + rptc_s
    return (rptc_p, rptc_s, rptc)

@iterate_jit(nopython=True)
def CTC_new(CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus,
            CTC_new_ps, CTC_new_prt, CTC_new_for_all, CTC_include17,
            CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt,
            CTC_new_refund_limited_all_payroll, payrolltax,
            n24, nu06, age_head, age_spouse, nu18, c00100, MARS, ptax_oasdi,
            c09200, ctc_new):
    """
    Computes new refundable child tax credit using specified parameters.

    Parameters
    ----------
    CTC_new_c: float
        New refundable child tax credit maximum amount per child
    CTC_new_rt: float
        New refundalbe child tax credit amount phasein rate
    CTC_new_c_under6_bonus: float
        Bonus new refundable child tax credit maximum for qualifying children under six
    CTC_new_ps: list
        New refundable child tax credit phaseout starting AGI
    CTC_new_prt: float
        New refundable child tax credit amount phaseout rate
    CTC_new_for_all: bool
        Whether or not maximum amount of the new refundable child tax credit is available to all
    CTC_new_refund_limited: bool
        New child tax credit refund limited to a decimal fraction of payroll taxes
    CTC_new_refund_limit_payroll_rt: float
        New child tax credit refund limit rate (decimal fraction of payroll taxes)
    CTC_new_refund_limited_all_payroll: bool
        New child tax credit refund limit applies to all FICA taxes, not just OASDI
    payrolltax: float
        Total (employee + employer) payroll tax liability
    n24: int
        Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17
    nu06: int
        Number of dependents under 6 years old
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    ptax_oasdi: float
        Employee and employer OASDI FICA tax plus self employment tax
        Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable credits are used, but before refundable credits are applied
    ctc_new: float
        New refundable child tax credit

    Returns
    -------
    ctc_new: float
        New refundable child tax credit
    """
    if CTC_include17:
            tu18 = int(age_head < 18)   # taxpayer is under age 18
            su18 = int(MARS == 2 and age_spouse < 18)  # spouse is under age 18
            childnum = n24 + max(0, nu18 - tu18 - su18 - n24)
    else:
        childnum = n24
    if childnum > 0:
        posagi = max(c00100, 0.)
        ctc_new = CTC_new_c * childnum + CTC_new_c_under6_bonus * nu06
        if not CTC_new_for_all:
            ctc_new = min(CTC_new_rt * posagi, ctc_new)
        ymax = CTC_new_ps[MARS - 1]
        if posagi > ymax:
            ctc_new_reduced = max(0.,
                                  ctc_new - CTC_new_prt * (posagi - ymax))
            ctc_new = min(ctc_new, ctc_new_reduced)
        if ctc_new > 0. and CTC_new_refund_limited:
            refund_new = max(0., ctc_new - c09200)
            if not CTC_new_refund_limited_all_payroll:
                limit_new = CTC_new_refund_limit_payroll_rt * ptax_oasdi
            if CTC_new_refund_limited_all_payroll:
                limit_new = CTC_new_refund_limit_payroll_rt * payrolltax
            limited_new = max(0., refund_new - limit_new)
            ctc_new = max(0., ctc_new - limited_new)
    else:
        ctc_new = 0.
    return ctc_new


@iterate_jit(nopython=True)
def IITAX(c59660, c11070, c10960, personal_refundable_credit, ctc_new, rptc,
          c09200, payrolltax, CDCC_refund, recovery_rebate_credit,
          eitc, c07220, CTC_refundable, refund, iitax, combined):
    """
    Computes final taxes.

    Parameters
    ----------
    c59660: float
        EITC amount
    c11070: float
        Child tax credit (refunded) from Form 8812
    c10960: float
        American Opportunity Credit refundable amount from Form 8863
    personal_refundable_credit: float
        Personal refundable credit
    ctc_new: float
        New refundable child tax credit
    rptc: float
        Refundable Payroll Tax Credit for filing unit
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable
        credits are used, but before refundable credits are applied
    payrolltax: float
        Total (employee + employer) payroll tax liability
    eitc: float
        Earned Income Credit
    refund: float
        Total refundable income tax credits
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax

    Returns
    -------
    eitc: float
        Earned Income Credit
    refund: float
        Total refundable income tax credits
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    """
    eitc = c59660
    if CTC_refundable:
        ctc_refund = c07220
    else:
        ctc_refund = 0.
    refund = (eitc + c11070 + c10960 + CDCC_refund + recovery_rebate_credit +
              personal_refundable_credit + ctc_new + rptc + ctc_refund)
    iitax = c09200 - refund
    combined = iitax + payrolltax
    return (eitc, refund, iitax, combined)


def BenefitSurtax(calc):
    """
    Computes itemized-deduction-benefit surtax and adds the surtax amount
    to income tax, combined tax, and surtax liabilities.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline

    Returns
    -------
    None:
        The function modifies calc
    """
    if calc.policy_param('ID_BenefitSurtax_crt') != 1.:
        ben = ComputeBenefit(calc,
                             calc.policy_param('ID_BenefitSurtax_Switch'))
        agi = calc.array('c00100')
        ben_deduct = calc.policy_param('ID_BenefitSurtax_crt') * agi
        ben_exempt_array = calc.policy_param('ID_BenefitSurtax_em')
        ben_exempt = ben_exempt_array[calc.array('MARS') - 1]
        ben_dedem = ben_deduct + ben_exempt
        ben_surtax = (calc.policy_param('ID_BenefitSurtax_trt') *
                      np.where(ben > ben_dedem, ben - ben_dedem, 0.))
        # add ben_surtax to income & combined taxes and to surtax subtotal
        calc.incarray('iitax', ben_surtax)
        calc.incarray('combined', ben_surtax)
        calc.incarray('surtax', ben_surtax)


def BenefitLimitation(calc):
    """
    Limits the benefits of select itemized deductions to a fraction of
    deductible expenses.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline

    Returns
    -------
    None:
        The function modifies calc
    """
    if calc.policy_param('ID_BenefitCap_rt') != 1.:
        benefit = ComputeBenefit(calc,
                                 calc.policy_param('ID_BenefitCap_Switch'))
        # Calculate total deductible expenses under the cap
        deduct_exps = 0.
        if calc.policy_param('ID_BenefitCap_Switch')[0]:  # medical
            deduct_exps += calc.array('c17000')
        if calc.policy_param('ID_BenefitCap_Switch')[1]:  # statelocal
            one_minus_hc = 1. - calc.policy_param('ID_StateLocalTax_hc')
            deduct_exps += (one_minus_hc *
                            np.maximum(calc.array('e18400_capped'), 0.))
        if calc.policy_param('ID_BenefitCap_Switch')[2]:  # realestate
            one_minus_hc = 1. - calc.policy_param('ID_RealEstate_hc')
            deduct_exps += one_minus_hc * calc.array('e18500_capped')
        if calc.policy_param('ID_BenefitCap_Switch')[3]:  # casualty
            deduct_exps += calc.array('c20500')
        if calc.policy_param('ID_BenefitCap_Switch')[4]:  # misc
            deduct_exps += calc.array('c20800')
        if calc.policy_param('ID_BenefitCap_Switch')[5]:  # interest
            deduct_exps += calc.array('c19200')
        if calc.policy_param('ID_BenefitCap_Switch')[6]:  # charity
            deduct_exps += calc.array('c19700')
        # Calculate cap value for itemized deductions
        benefit_limit = deduct_exps * calc.policy_param('ID_BenefitCap_rt')
        # Add the difference between the actual benefit and capped benefit
        # to income tax and combined tax liabilities.
        excess_benefit = np.maximum(benefit - benefit_limit, 0)
        calc.incarray('iitax', excess_benefit)
        calc.incarray('surtax', excess_benefit)
        calc.incarray('combined', excess_benefit)


@iterate_jit(nopython=True)
def FairShareTax(c00100, MARS, ptax_was, setax, ptax_amc,
                 FST_AGI_trt, FST_AGI_thd_lo, FST_AGI_thd_hi,
                 fstax, iitax, combined, surtax):
    """
    Computes Fair Share Tax, or "Buffet Rule", types of reforms.

    Parameters
    ----------
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    ptax_was: float
        Employee and employer OASDI plus HI FICA tax
    setax: float
        Self-employment tax
    ptax_amc: float
        Additional Medicare Tax
    FST_AGI_trt: float
        New minimum tax; rate as a decimal fraction of AGI
    FST_AGI_thd_lo: list
        Minimum AGI needed to be subject to the new minimum tax
    FST_AGI_thd_hi: list
        AGI level at which the New Minimum Tax is fully phased in
    fstax: float
        Fair Share Tax amount
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    surtax: float
        Individual income tax subtotal augmented by fstax

    Returns
    -------
    fstax: float
        Fair Share Tax amount
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    surtax: float
        Individual income tax subtotal augmented by fstax
    """
    if FST_AGI_trt > 0. and c00100 >= FST_AGI_thd_lo[MARS - 1]:
        employee_share = 0.5 * ptax_was + 0.5 * setax + ptax_amc
        fstax = max(c00100 * FST_AGI_trt - iitax - employee_share, 0.)
        thd_gap = max(FST_AGI_thd_hi[MARS - 1] - FST_AGI_thd_lo[MARS - 1], 0.)
        if thd_gap > 0. and c00100 < FST_AGI_thd_hi[MARS - 1]:
            fstax *= (c00100 - FST_AGI_thd_lo[MARS - 1]) / thd_gap
        iitax += fstax
        combined += fstax
        surtax += fstax
    else:
        fstax = 0.
    return (fstax, iitax, combined, surtax)


@iterate_jit(nopython=True)
def LumpSumTax(DSI, num, XTOT,
               LST,
               lumpsum_tax, combined):
    """
    Computes lump-sum tax and add it to combined taxes.

    Parameters
    ----------
    DSI: int
        1 if claimed as dependent on another return, otherwise 0
    num: int
        2 when MARS is 2 (married filing jointly); otherwise 1
    XTOT: int
        Total number of exemptions for filing unit
    LST: float
        Dollar amount of lump-sum tax
    lumpsum_tax: float
        Lumpsum (or head) tax
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax

    Returns
    -------
    lumpsum_tax: float
        Lumpsum (or head) tax
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    """
    if LST == 0.0 or DSI == 1:
        lumpsum_tax = 0.
    else:
        lumpsum_tax = LST * max(num, XTOT)
    combined += lumpsum_tax
    return (lumpsum_tax, combined)


@iterate_jit(nopython=True)
def ExpandIncome(e00200, pencon_p, pencon_s, e00300, e00400, e00600,
                 e00700, e00800, e00900, e01100, e01200, e01400, e01500,
                 e02000, e02100, p22250, p23250, cmbtp, ptax_was,
                 benefit_value_total, expanded_income):
    """
    Calculates expanded_income from component income types.

    Parameters
    ----------
    e00200: float
        Wages, salaries, and tips for filing unit net of pension contributions
    pencon_p: float
        Contributions to defined-contribution pension plans for taxpayer
    pencon_s: float
        Contributions to defined-contribution pension plans for spouse
    e00300: float
        Taxable interest income
    e00400: float
        Tax-exempt interest income
    e00600: float
        Ordinary dividends included in AGI
    e00700: float
        Taxable refunds of state and local income taxes
    e00800: float
        Alimony received
    e00900: float
        Schedule C business net profit/loss for filing unit
    e01100: float
        Capital gain distributions not reported on Schedule D
    e01200: float
        Other net gain/loss from Form 4797
    e01400: float
        Taxable IRA distributions
    e01500: float
        Total pensions and annuities
    e02000: float
        Schedule E total rental, royalty, partnership, S-corporation, etc, income/loss
    e02100: float
        Farm net income/loss for filing unit from Schedule F
    p22250: float
        Schedule D net short term capital gains/losses
    p23250:float
        Schedule D net long term capital gains/losses
    cmbtp: float
        Estimate of inome on (AMT) Form 6251 but not in AGI
    ptax_was: float
        Employee and employer OASDI and HI FICA tax
    benefit_value_total: float
        Consumption value of all benefits received by tax unit, which is included in expanded income
    expanded_income: float
        Broad income measure that includes benefit_value_total

    Returns
    -------
    expanded_income: float
        Broad income measure that includes benefit_value_total
    """
    expanded_income = (
        e00200 +  # wage and salary income net of DC pension contributions
        pencon_p +  # tax-advantaged DC pension contributions for taxpayer
        pencon_s +  # tax-advantaged DC pension contributions for spouse
        e00300 +  # taxable interest income
        e00400 +  # non-taxable interest income
        e00600 +  # dividends
        e00700 +  # state and local income tax refunds
        e00800 +  # alimony received
        e00900 +  # Sch C business net income/loss
        e01100 +  # capital gain distributions not reported on Sch D
        e01200 +  # Form 4797 other net gain/loss
        e01400 +  # taxable IRA distributions
        e01500 +  # total pension & annuity income (including DB-plan benefits)
        e02000 +  # Sch E total rental, ..., partnership, S-corp income/loss
        e02100 +  # Sch F farm net income/loss
        p22250 +  # Sch D: net short-term capital gain/loss
        p23250 +  # Sch D: net long-term capital gain/loss
        cmbtp +  # other AMT taxable income items from Form 6251
        0.5 * ptax_was +  # employer share of FICA taxes on wages/salaries
        benefit_value_total  # consumption value of all benefits received;
        # see the BenefitPrograms function in this file for details on
        # exactly how the benefit_value_total variable is computed
    )
    return expanded_income


@iterate_jit(nopython=True)
def AfterTaxIncome(combined, expanded_income, aftertax_income):
    """
    Calculates after-tax expanded income.

    Parameters
    ----------
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    expanded_income: float
        Broad income measure that includes benefit_value_total
    aftertax_income: float
        After tax income is equal to expanded_income minus combined

    Returns
    -------
    aftertax_income: float
        After tax income is equal to expanded_income minus combined
    """
    aftertax_income = expanded_income - combined
    return aftertax_income