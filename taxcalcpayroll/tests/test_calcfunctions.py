"""
Tests for Tax-Calculator calcfunctions.py logic.
"""

# CODING-STYLE CHECKS:
# pycodestyle test_calcfunctions.py
# pylint --disable=locally-disabled test_calcfunctions.py

import os
import re
import ast
from taxcalcpayroll import Records  # pylint: disable=import-error
from taxcalcpayroll import calcfunctions
import numpy as np
import pytest


class GetFuncDefs(ast.NodeVisitor):
    """
    Return information about each function defined in the functions.py file.
    """

    def __init__(self):
        """
        GetFuncDefs class constructor
        """
        self.fname = ""
        self.fnames = list()  # function name (fname) list
        self.fargs = dict()  # lists of function arguments indexed by fname
        self.cvars = dict()  # lists of calc vars in function indexed by fname
        self.rvars = dict()  # lists of function return vars indexed by fname

    def visit_Module(self, node):  # pylint: disable=invalid-name
        """
        visit the specified Module node
        """
        self.generic_visit(node)
        return (self.fnames, self.fargs, self.cvars, self.rvars)

    def visit_FunctionDef(self, node):  # pylint: disable=invalid-name
        """
        visit the specified FunctionDef node
        """
        self.fname = node.name
        self.fnames.append(self.fname)
        self.fargs[self.fname] = list()
        for anode in ast.iter_child_nodes(node.args):
            self.fargs[self.fname].append(anode.arg)
        self.cvars[self.fname] = list()
        for bodynode in node.body:
            if isinstance(bodynode, ast.Return):
                continue  # skip function's Return node
            for bnode in ast.walk(bodynode):
                if isinstance(bnode, ast.Name):
                    if isinstance(bnode.ctx, ast.Store):
                        if bnode.id not in self.cvars[self.fname]:
                            self.cvars[self.fname].append(bnode.id)
        self.generic_visit(node)

    def visit_Return(self, node):  # pylint: disable=invalid-name
        """
        visit the specified Return node
        """
        if isinstance(node.value, ast.Tuple):
            self.rvars[self.fname] = [r_v.id for r_v in node.value.elts]
        elif isinstance(node.value, ast.BinOp):
            self.rvars[self.fname] = []  # no vars returned; only an expression
        else:
            self.rvars[self.fname] = [node.value.id]
        self.generic_visit(node)


def test_calc_and_used_vars(tests_path):
    """
    Runs two kinds of tests on variables used in the calcfunctions.py file:

    (1) Checks that each var in Records.CALCULATED_VARS is actually calculated

    If test (1) fails, a variable in Records.CALCULATED_VARS was not
    calculated in any function in the calcfunctions.py file.  With the
    exception of a few variables listed in this test, all
    Records.CALCULATED_VARS must be calculated in the calcfunctions.py file.

    (2) Check that each variable that is calculated in a function and
    returned by that function is an argument of that function.
    """
    # pylint: disable=too-many-locals
    funcpath = os.path.join(tests_path, "..", "calcfunctions.py")
    gfd = GetFuncDefs()
    fnames, fargs, cvars, rvars = gfd.visit(ast.parse(open(funcpath).read()))
    # Test (1):
    # .. create set of vars that are actually calculated in calcfunctions.py
    all_cvars = set()
    for fname in fnames:
        if fname == "BenefitSurtax":
            continue  # because BenefitSurtax is not really a function
        all_cvars.update(set(cvars[fname]))
    # .. add to all_cvars set variables calculated in Records class
    all_cvars.update(set(["num", "sep", "exact"]))
    # .. add to all_cvars set variables calculated elsewhere
    all_cvars.update(set(["mtr_paytax", "mtr_inctax"]))
    all_cvars.update(set(["benefit_cost_total", "benefit_value_total"]))
    # .. check that each var in Records.CALCULATED_VARS is in the all_cvars set
    records_varinfo = Records(data=None)
    found_error1 = False
    payroll_output = {"sey", "payrolltax", "ptax_was", "setax", "c03260", "ptax_oasdi",
                      "earned", "earned_p", "earned_s", "was_plus_sey_p", "was_plus_sey_s",
                      "ptax_amc"}
    if not payroll_output <= all_cvars:
        msg1 = "all Records.CALCULATED_VARS not calculated " "in calcfunctions.py\n"
        for var in records_varinfo.CALCULATED_VARS - all_cvars:
            found_error1 = True
            msg1 += "VAR NOT CALCULATED: {}\n".format(var)
    # Test (2):
    faux_functions = [
        "EITCamount",
        "ComputeBenefit",
        "BenefitPrograms",
        "BenefitSurtax",
        "BenefitLimitation",
    ]
    found_error2 = False
    msg2 = "calculated & returned variables are not function arguments\n"
    for fname in fnames:
        if fname in faux_functions:
            continue  # because fname is not a genuine function
        crvars_set = set(cvars[fname]) & set(rvars[fname])
        if not crvars_set <= set(fargs[fname]):
            found_error2 = True
            for var in crvars_set - set(fargs[fname]):
                msg2 += "FUNCTION,VARIABLE: {} {}\n".format(fname, var)
    # Report errors for the two tests:
    if found_error1 and found_error2:
        raise ValueError("{}\n{}".format(msg1, msg2))
    if found_error1:
        raise ValueError(msg1)
    if found_error2:
        raise ValueError(msg2)


def test_function_args_usage(tests_path):
    """
    Checks each function argument in calcfunctions.py for use in its
    function body.
    """
    funcfilename = os.path.join(tests_path, "..", "calcfunctions.py")
    with open(funcfilename, "r") as funcfile:
        fcontent = funcfile.read()
    fcontent = re.sub("#.*", "", fcontent)  # remove all '#...' comments
    fcontent = re.sub("\n", " ", fcontent)  # replace EOL character with space
    funcs = fcontent.split("def ")  # list of function text
    msg = "FUNCTION ARGUMENT(S) NEVER USED:\n"
    found_error = False
    for func in funcs[1:]:  # skip first item in list, which is imports, etc.
        fcode = func.split("return ")[0]  # fcode is between def and return
        match = re.search(r"^(.+?)\((.*?)\):(.*)$", fcode)
        if match is None:
            msg = (
                "Could not find function name, arguments, "
                "and code portions in the following text:\n"
            )
            msg += "--------------------------------------------------------\n"
            msg += "{}\n".format(fcode)
            msg += "--------------------------------------------------------\n"
            raise ValueError(msg)
        fname = match.group(1)
        fargs = match.group(2).split(",")  # list of function arguments
        fbody = match.group(3)
        if fname == "Taxes":
            continue  # because Taxes has part of fbody in return statement
        for farg in fargs:
            arg = farg.strip()
            if fbody.find(arg) < 0:
                found_error = True
                msg += "FUNCTION,ARGUMENT= {} {}\n".format(fname, arg)
    if found_error:
        raise ValueError(msg)


tuple1 = (
    120000,
    10000,
    15000,
    100,
    2000,
    0.06,
    0.06,
    0.015,
    0.015,
    0,
    99999999999,
    400,
    0,
    0,
    0,
    0,
    0,
    0,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)
tuple2 = (
    120000,
    10000,
    15000,
    100,
    2000,
    0.06,
    0.06,
    0.015,
    0.015,
    0,
    99999999999,
    400,
    2000,
    0,
    10000,
    0,
    0,
    3000,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)
tuple3 = (
    120000,
    150000,
    15000,
    100,
    2000,
    0.06,
    0.06,
    0.015,
    0.015,
    0,
    99999999999,
    400,
    2000,
    0,
    10000,
    0,
    0,
    3000,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)
tuple4 = (
    120000,
    500000,
    15000,
    100,
    2000,
    0.06,
    0.06,
    0.015,
    0.015,
    0,
    400000,
    400,
    2000,
    0,
    10000,
    0,
    0,
    3000,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)
tuple5 = (
    120000,
    10000,
    15000,
    100,
    2000,
    0.06,
    0.06,
    0.015,
    0.015,
    0,
    99999999999,
    400,
    300,
    0,
    0,
    0,
    0,
    0,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)
tuple6 = (
    120000,
    10000,
    15000,
    100,
    2000,
    0.06,
    0.06,
    0.015,
    0.015,
    0,
    99999999999,
    400,
    0,
    0,
    0,
    0,
    -40000,
    0,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)
expected1 = (0, 4065, 4065, 0, 0, 3252, 25000, 10000, 15000, 10100, 17000)
expected2 = (
    15000,
    6146.25,
    4065,
    2081.25,
    1040.625,
    4917,
    38959.375,
    21167.5,
    17791.875,
    21380,
    19820,
)
expected3 = (
    15000,
    22202.25,
    21453,
    749.25,
    374.625,
    16773,
    179625.375,
    161833.5,
    17791.875,
    161380,
    19820,
)
expected4 = (
    15000,
    46067.85,
    31953,
    749.25,
    374.625,
    30138.6,
    529625.375,
    511833.5,
    17791.875,
    511380,
    19820,
)
expected5 = (300, 4065, 4065, 0, 0, 3285.3, 25300, 10279.1875, 15000, 10382, 17000)
expected6 = (-40000, 4065, 4065, 0, 0, 3252, 0, 0, 15000, 10100, 17000)


@pytest.mark.parametrize(
    "test_tuple,expected_value",
    [
        (tuple1, expected1),
        (tuple2, expected2),
        (tuple3, expected3),
        (tuple4, expected4),
        (tuple5, expected5),
        (tuple6, expected6),
    ],
    ids=["case 1", "case 2", "case 3", "case 4", "case 5", "case 6"],
)
def test_EI_PayrollTax(test_tuple, expected_value, skip_jit):
    """
    Tests the EI_PayrollTax function
    """
    test_value = calcfunctions.EI_PayrollTax(*test_tuple)
    print("Test value = ", test_value)

    assert np.allclose(test_value, expected_value)

