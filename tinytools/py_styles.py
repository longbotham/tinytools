import collections as _collections

def _print_dict(d):
    for i in zip(list(d.keys()),list(d.values())):
        print("%-18s : %s" % i)

def _create_my_dict_based_on_pep8():
    """This is what I've been coding to - it is based on the pep8 guidelines
    with a few more noun/verb suggestions.
    Naming Conventions from:
    http://www.ntu.edu.sg/home/ehchua/programming/webprogramming/Python1_Basics.html#zz-3.1
    Variable names: use a noun in lowercase words joined with underscore, e.g., num_students.
    Function names: use a verb in lowercase words joined with underscore, e.g., get_area().
    Class names: use a noun in camel-case (initial-cap all words), e.g., MyClass, IndexError.
    Constant names: use a noun in uppercase words joined with underscore, e.g., PI, MAX_STUDENTS.
    """
    mine = _collections.OrderedDict()
    mine['pypackage'] = "short name, all lowercase, underscore discouraged"
    mine['module_name'] = "short name, all lowercase, underscore with " \
                          "improved readability"
    mine['function_names'] = "lowercase with words separated by " \
                               "underscores " \
                           "to improve readability"
    mine['global_vars'] = "Same convention as functions"
    mine['local_vars'] = "Same convention as functions"
    mine['ClassNames'] = "use CapWords convention"
    mine['make_method_names'] = "Same convention as functions but use " \
                                     "a verb to start"
    mine['noun_instance_vars'] = "Same convention as functions but use a " \
                                 "noun to start"
    mine['ExceptionNames'] = "CapWords - use " \
                             "Error as a suffix if the exception is an error"
    mine['CONSTANT_NAMES'] = "capital letters with underscores separating " \
                             "words"

    return mine

def _create_early_google_style_dict():
    """Found on a google code site based on pre-pep8 styles...
    https://code.google.com/p/soc/wiki/PythonStyleGuide#Access_control
    """
    g = _collections.OrderedDict()
    g['py_package'] = "lower_with_under"
    g['module_name'] = "lower_with_under"
    g['functionNames'] = "firstLowerCapWords"
    g['global_vars'] = "lower_with_under"
    g['local_vars'] = "lower_with_under"
    g['ClassNames'] = "CapWords"
    g['methodNames'] = "firstLowerCapWords"
    g['instance_vars'] = "lower_with_under"
    g['ExceptionNames'] = "CapWords"
    g['CONSTANT_NAMES'] = "CAPS_WITH_UNDER"

    return g

def _create_pep8_dict():
    """Based on pep8:
    http://legacy.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions
    """
    pep8 = _collections.OrderedDict()
    pep8['pypackage'] = "short name, all lowercase, underscore discouraged"
    pep8['module_name'] = "short name, all lowercase, underscore with " \
                          "improved readability"
    pep8['function_names'] = "lowercase with words separated by underscores " \
                           "to improve readability"
    pep8['global_vars'] = "Same convention as functions"
    pep8['local_vars'] = "Same convention as functions"
    pep8['ClassNames'] = "use CapWords convention"
    pep8['method_names'] = "Same convention as functions"
    pep8['instance_vars'] = "Same convention as functions"
    pep8['ExceptionNames'] = "CapWords - use " \
                             "Error as a suffix if the exception is an error"
    pep8['CONSTANT_NAMES'] = "UPPER_CASE_WITH_UNDERSCORES"

    return pep8

def _create_style_dicts():
    dmine = _create_my_dict_based_on_pep8()
    dpep8 = _create_pep8_dict()
    dgoogle = _create_early_google_style_dict()

    return (dmine,dpep8,dgoogle)

def print_all_styles_to_screen():
    """This function calls hidden functions that create examples of
    different Python naming conventions.  One based on PEP8 (the
    "standard"), one based on an earlier recommendation on google code,
    and one that I currently try to write to.  The biggest difference is
    that I want to be able to easily see the different between methods and
    data members when I tab-complete in IPython.
    """

    (dmine,dpep8,dgoogle) = _create_style_dicts()

    print('')
    print("### My Formatting ###")
    _print_dict(dmine)
    print('')
    print("### pep8 Formatting ###")
    _print_dict(dpep8)
    print('')
    print("### Older formatting suggstion ###")
    _print_dict(dgoogle)