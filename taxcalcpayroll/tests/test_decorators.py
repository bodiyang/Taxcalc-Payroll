# CODING-STYLE CHECKS:
# pycodestyle test_decorators.py

import os
import sys
import pytest
import importlib
import numpy as np
from pandas import DataFrame
from pandas.testing import assert_frame_equal
import taxcalc
from taxcalc.decorators import *


def test_create_apply_function_string():
    ans = create_apply_function_string(['a', 'b', 'c'], ['d', 'e'], [])
    exp = ("def ap_func(x_0,x_1,x_2,x_3,x_4):\n"
           "  for i in range(len(x_0)):\n"
           "    x_0[i],x_1[i],x_2[i] = jitted_f(x_3[i],x_4[i])\n"
           "  return x_0,x_1,x_2\n")
    assert ans == exp


def test_create_apply_function_string_with_params():
    ans = create_apply_function_string(['a', 'b', 'c'], ['d', 'e'], ['d'])
    exp = ("def ap_func(x_0,x_1,x_2,x_3,x_4):\n"
           "  for i in range(len(x_0)):\n"
           "    x_0[i],x_1[i],x_2[i] = jitted_f(x_3,x_4[i])\n"
           "  return x_0,x_1,x_2\n")
    assert ans == exp


def test_create_toplevel_function_string_mult_outputs():
    ans = create_toplevel_function_string(['a', 'b'], ['d', 'e'],
                                          ['pm', 'pm', 'pf', 'pm'])
    exp = ''
    exp = ("def hl_func(pm, pf):\n"
           "    from pandas import DataFrame\n"
           "    import numpy as np\n"
           "    import pandas as pd\n"
           "    def get_values(x):\n"
           "        if isinstance(x, pd.Series):\n"
           "            return x.values\n"
           "        else:\n"
           "            return x\n"
           "    outputs = \\\n"
           "        (pm.a, pm.b) = \\\n"
           "        applied_f(get_values(pm.a[0]), get_values(pm.b[0]), "
           "get_values(pf.d), get_values(pm.e[0]), )\n"
           "    header = ['a', 'b']\n"
           "    return DataFrame(data=np.column_stack(outputs),"
           "columns=header)")

    assert ans == exp


def test_create_toplevel_function_string():
    ans = create_toplevel_function_string(['a'], ['d', 'e'],
                                          ['pm', 'pf', 'pm'])
    exp = ''
    exp = ("def hl_func(pm, pf):\n"
           "    from pandas import DataFrame\n"
           "    import numpy as np\n"
           "    import pandas as pd\n"
           "    def get_values(x):\n"
           "        if isinstance(x, pd.Series):\n"
           "            return x.values\n"
           "        else:\n"
           "            return x\n"
           "    outputs = \\\n"
           "        (pm.a) = \\\n"
           "        applied_f(get_values(pm.a[0]), get_values(pf.d), "
           "get_values(pm.e[0]), )\n"
           "    header = ['a']\n"
           "    return DataFrame(data=outputs,"
           "columns=header)")
    assert ans == exp


def some_calc(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


def test_make_apply_function():
    ans_do_jit = make_apply_function(some_calc, ['a', 'b'], ['x', 'y', 'z'],
                                     [], do_jit=True, no_python=True)
    assert ans_do_jit
    ans_no_jit = make_apply_function(some_calc, ['a', 'b'], ['x', 'y', 'z'],
                                     [], do_jit=False, no_python=True)
    assert ans_no_jit


@apply_jit(["a", "b"], ["x", "y", "z"], nopython=True)
def Magic_calc(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


def Magic(pm, pf):
    # Adjustments
    outputs = pf.a, pf.b = Magic_calc(pm, pf)
    header = ['a', 'b']
    return DataFrame(data=np.column_stack(outputs), columns=header)


@iterate_jit(nopython=True)
def Magic_calc2(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


class Foo(object):
    pass


@iterate_jit(nopython=True)
def faux_function(MARS):
    if MARS == 1:
        var = 2
    else:
        var = 1
    return var


@iterate_jit(nopython=True)
def ret_everything(a, b, c, d, e, f):

    c = a + b
    d = a + b
    e = a + b
    f = a + b

    return (c, d, e,
            f)


def test_magic_apply_jit():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=["a", "b"])
    assert_frame_equal(xx, exp)


def test_magic_apply_jit_swap():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic(pf, pm)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=["a", "b"])
    assert_frame_equal(xx, exp)


def test_magic_iterate_jit():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic_calc2(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=["a", "b"])
    assert_frame_equal(xx, exp)


def test_faux_function_iterate_jit():
    pm = Foo()
    pf = Foo()
    pf.MARS = np.ones((5,))
    pf.var = np.ones((5,))
    ans = faux_function(pm, pf)
    exp = DataFrame(data=[2.0] * 5, columns=['var'])
    assert_frame_equal(ans, exp)


def test_ret_everything_iterate_jit():
    pm = Foo()
    pf = Foo()
    pf.a = np.ones((5,))
    pf.b = np.ones((5,))
    pf.c = np.ones((5,))
    pf.d = np.ones((5,))
    pf.e = np.ones((5,))
    pf.f = np.ones((5,))
    ans = ret_everything(pm, pf)
    exp = DataFrame(data=[[2.0, 2.0, 2.0, 2.0]] * 5,
                    columns=["c", "d", "e", "f"])
    assert_frame_equal(ans, exp)


@iterate_jit(nopython=True)
def Magic_calc3(x, y, z):
    a = x + y
    b = a + z
    return (a, b)


def test_function_takes_kwarg():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc3(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)


@iterate_jit(nopython=True)
def Magic_calc4(x, y, z):
    a = x + y
    b = a + z
    return (a, b)


def test_function_no_parameters_listed():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc4(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)


@iterate_jit(parameters=['w'], nopython=True)
def Magic_calc5(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z
    return (a, b)


def test_function_parameters_optional():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pm.w = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc5(pm, pf)
    exp = DataFrame(data=[[2.0, 4.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)


def unjittable_function1(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z


def unjittable_function2(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z
    return (a, b, c)


def test_iterate_jit_raises_on_no_return():
    with pytest.raises(ValueError):
        ij = iterate_jit(parameters=['w'], nopython=True)
        ij(unjittable_function1)


def test_iterate_jit_raises_on_unknown_return_argument():
    ij = iterate_jit(parameters=['w'], nopython=True)
    uf2 = ij(unjittable_function2)
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pm.w = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    with pytest.raises(AttributeError):
        ans = uf2(pm, pf)


def Magic_calc6(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z
    return (a, b)


def test_force_no_jit():
    """
    Force execution of code for "DO_JIT = False", which tests the
    id_wrapper function in the decorators.py file.
    """
    # set environment variable that turns off JIT decorator logic
    os.environ['NOTAXCALCJIT'] = 'NOJIT'
    # reload the decorators module
    importlib.reload(taxcalc.decorators)
    # verify Magic_calc6 function works as expected
    Magic_calc6_ = iterate_jit(parameters=['w'], nopython=True)(Magic_calc6)
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pm.w = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc6_(pm, pf)
    exp = DataFrame(data=[[2.0, 4.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)
    # restore normal JIT operation of decorators module
    del os.environ['NOTAXCALCJIT']
    importlib.reload(taxcalc.decorators)
