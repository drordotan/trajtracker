"""

TrajTracker - movement package - private utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import numbers
import numpy as np

from expyriment.misc import geometry


#--------------------------------------------------------------------------
class ErrMsg(object):

    _invalid_attr_type = "trajtracker error: invalid attempt to set {0}.{1} to a non-{2} value ({3})"
    _set_to_non_positive = "trajtracker error: invalid attempt to set {0}.{1} to a non-positive value ({2})"
    _set_to_negative = "trajtracker error: invalid attempt to set {0}.{1} to a negative value ({2})"
    _set_to_invalid_value = "trajtracker error: {0}.{1} was set to an invalid value ({2})"

    @staticmethod
    def attr_invalid_type(class_name, attr_name, expected_type, arg_value):
        return "trajtracker error: {0}.{1} was set to a non-{2} value ({3})".format(class_name, attr_name, expected_type, arg_value)

    @staticmethod
    def attr_invalid_value(class_name, attr_name, arg_value):
        "trajtracker error: {0}.{1} was set to an invalid value ({2})".format(class_name, attr_name, arg_value)


    @staticmethod
    def invalid_func_arg_type(method_name, expected_type, arg_name, arg_value):
        return "trajtracker error: {0}() was called with a non-{1} {2} ({3})".format(method_name, expected_type, arg_name, arg_value)

    @staticmethod
    def invalid_method_arg_type(class_name, method_name, expected_type, arg_name, arg_value):
        return "trajtracker error: {0}.{1}() was called with a non-{2} {3} ({4})".format(class_name, method_name, expected_type, arg_name, arg_value)


#============================================================================
#   Validate attributes
#============================================================================

NoneValues = Enum("NoneValues", "Invalid Valid ChangeTo0")


#--------------------------------------
def _get_type_name(t):
    if isinstance(t, (list, tuple)):
        return "/".join([_get_type_name(tt) for tt in t])
    if t == numbers.Number:
        return "number"
    else:
        return t.__name__


#--------------------------------------
def validate_attr_type(obj, attr_name, value, attr_type, none_allowed=False, type_name=None):

    if (value is None and not none_allowed) or (value is not None and not isinstance(value, attr_type)):
        if type_name is None:
            type_name = _get_type_name(attr_type)

        raise ValueError(ErrMsg.attr_invalid_type(type(obj).__name__, attr_name, type_name, value))

#--------------------------------------
def validate_attr_rgb(obj, attr_name, value, accept_single_num=False):

    if accept_single_num and isinstance(value, int) and 0 <= value < 2**24:
        return (int(np.floor(value / 2 ** 16)), int(np.floor(value / 256)) % 256, value % 256)

    validate_attr_type(obj, attr_name, value, tuple, type_name="(red,green,blue)")
    if len(value) != 3 or \
            not isinstance(value[0], int) or not (0 <= value[0] < 256) or \
            not isinstance(value[1], int) or not (0 <= value[1] < 256) or \
            not isinstance(value[2], int) or not (0 <= value[2] < 256):
        raise ValueError("trajtracker error: {:}.{:} was set to an invalid value ({:}) - expecting (red,green,blue)".format(type(obj).__name__, attr_name, value))

    return value

#--------------------------------------
def validate_attr_is_coord(obj, attr_name, value, change_none_to_0=False):

    if value is None and change_none_to_0:
        return (0, 0)

    if isinstance(value, geometry.XYPoint):
        value = (value.x, value.y)

    validate_attr_type(obj, attr_name, value, (tuple, list))
    if len(value) != 2:
        raise ValueError("trajtracker error: {:}.{:} was set to an invalid value ({:}) - expecting (x,y) coordinates".format(type(obj).__name__, attr_name, value))
    validate_attr_type(obj, "{:}[0]".format(attr_name), value[0], int)
    validate_attr_type(obj, "{:}[1]".format(attr_name), value[1], int)

    return value


#--------------------------------------
def validate_attr_numeric(obj, attr_name, value, none_value=NoneValues.Invalid):
    if value is None:
        if none_value == NoneValues.Invalid:
            raise ValueError(ErrMsg.attr_invalid_type(type(obj).__name__, attr_name, "numeric", "None"))
        elif none_value == NoneValues.Valid:
            pass
        elif none_value == NoneValues.ChangeTo0:
            value = 0

    if value is not None and not isinstance(value, numbers.Number):
        raise ValueError(ErrMsg.attr_invalid_type(type(obj).__name__, attr_name, "numeric", value))

    return value

#--------------------------------------
def validate_attr_not_negative(obj, attr_name, value):
    if value is not None and value < 0:
        msg = "trajtracker error: {0}.{1} was set to a negative value ({2})".format(type(obj).__name__, attr_name, value)
        raise ValueError(msg)

#--------------------------------------
def validate_attr_positive(obj, attr_name, value):
    if value is not None and value <= 0:
        msg = "trajtracker error: {0}.{1} was set to a negative/0 value ({2})".format(type(obj).__name__, attr_name, value)
        raise ValueError(msg)


#============================================================================
#   Validate function arguments
#============================================================================

#-------------------------------------------------------------------------
def validate_func_arg_type(obj, func_name, arg_name, value, arg_type, none_allowed=False, type_name=None):

    if (value is None and not none_allowed) or (value is not None and not isinstance(value, arg_type)):
        if type_name is None:
            type_name = _get_type_name(arg_type)

        if obj is None:
            raise ValueError(ErrMsg.invalid_func_arg_type(func_name, type_name, arg_name, value))
        else:
            raise ValueError(ErrMsg.invalid_method_arg_type(type(obj).__name__, func_name, type_name, arg_name, value))

#--------------------------------------
def validate_func_arg_not_negative(obj, func_name, arg_name, value):

    if value is not None and value < 0:
        if obj is None:
            msg = "trajtracker error: Argument '{1}' of {0}() has a negative value ({2})".format(func_name, arg_name, value)
        else:
            msg = "trajtracker error: Argument '{2}' of {0}.{1}() has a negative value ({3})".format(type(obj).__name__, func_name, arg_name, value)

        raise ValueError(msg)

#--------------------------------------
def validate_func_arg_positive(obj, func_name, arg_name, value):

    if value is not None and value <= 0:
        if obj is None:
            msg = "trajtracker error: Argument '{1}' of {0}() has a negative/0 value ({2})".format(func_name, arg_name, value)
        else:
            msg = "trajtracker error: Argument '{2}' of {0}.{1}() has a negative/0 value ({3})".format(type(obj).__name__, func_name, arg_name, value)

        raise ValueError(msg)


