#!/usr/bin/env python

""" OrderedBunch is a subclass of OrderedDict with attribute-style access.

    ordered_un/bunchify provide dictionary conversion; Bunches can also be
    converted via OrderedBunch.to/fromOrderedDict().

    original source:
    https://pypi.python.org/pypi/bunch
"""

import collections as _collections
import textwrap as _textwrap
#import inspect as _inspect


class OrderedBunch(_collections.OrderedDict):
    """ A dictionary that provides attribute-style access.
        A OrderedBunch is a subclass of dict; it supports all the methods a dict does...

        See ordered_unbunchify/OrderedBunch.toOrderedDict, ordered_bunchify/OrderedBunch.fromOrderedDict for notes about conversion.
    """

    _initialized = False

    def __init__(self,*args,**kwarg):
        """ initializes the ordered dict
        """
        super(OrderedBunch,self).__init__(*args,**kwarg)
        self._initialized = True

    def __contains__(self, k):
        try:
            return hasattr(self, k) or dict.__contains__(self, k)
        except:
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        """ Gets key if it exists, otherwise throws AttributeError.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        """ Sets attribute k if it exists, otherwise sets key k. A KeyError
            raised by set-item (only likely if you subclass OrderedBunch) will
            propagate as an AttributeError instead.
        """

        if not self._initialized:
            # for OrderedDict initialization
            return object.__setattr__(self, k, v)

        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        """ Deletes attribute k if it exists, otherwise deletes key k. A KeyError
            raised by deleting the key--such as when the key is missing--will
            propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def _repr_pretty_(self,p,cycle):
        """ Pretty print for this class.  Will only trigger in ipython."""
        p.text(_print_recursive_start(self))

    def __dir__(self):
        """ Overload the tab-complete operation so that it is easier to dynamically explore the bunch.
        """
        return list(self.keys())

def ordered_bunchify(x,level=0):
    """ Recursively transforms a dictionary into a OrderedBunch via copy.
    """

    # if x == [[[1, 2], [3, 4]]]:
    #     import ipdb; ipdb.set_trace()

    speak = False
    if speak: print('*'*(level+1)+' x is:  '+str(x))
    if isinstance(x, dict):
        return OrderedBunch((k, ordered_bunchify(v)) for k,v in x.items())
#    # elif isinstance(x, (list, tuple)):
        # y = list(x)
        # for i,v in enumerate(y):
        #     y[i] = ordered_bunchify(y[i],level=level+1)
        # if speak: print '*'*(level+1)+' OrderedBunch request is:  '+repr(y)
        # try:
        #     out = OrderedBunch(y)
        #     if isinstance(y[0],str):
        #         raise ValueError("This catches when the OrderedDict " \
        #                          "(underneath OrderedBunch) broadcasts" \
        #                          "a single key to mutiple dict entries.  See" \
        #                          "unittests 'nested_bunches'.")
        #     if speak: print '*'*(level+1)+ 'Bunchify worked, out is:  '+str(out)
        #     return out
        # except Exception as e:
        #     print('the error is:')
        #     print(e)
        #     if speak: print '*'*(level+1)+' exception raised, out is:  '+str(y)
        #     return y
    else:
        return x

def ordered_dictionarify(x,level=0):
    """Take a crack at parsing lists of lists or tuples of tuples into nested
    ordered dictionaries.  This can be coupled with ordered_bunchify to
    create nested ordered bunches from non-dictionary input."""
    speak = False
    if speak: print('*' * (level + 1) + ' x is:  ' + str(x))
    if isinstance(x, dict):
        return _collections.OrderedDict((k, ordered_dictionarify(v)) for k, v in x.items())
    elif isinstance(x, (list, tuple)):
        y = list(x)
        for i,v in enumerate(y):
            y[i] = ordered_dictionarify(y[i],level=level+1)
        if speak: print('*'*(level+1)+' OrderedBunch request is:  '+repr(y))
        try:
            out = _collections.OrderedDict(y)
            if isinstance(y[0],str):
                raise ValueError("This catches when the OrderedDict " \
                                 "(underneath OrderedBunch) broadcasts" \
                                 "a single key to mutiple dict entries.  See" \
                                 "unittests 'nested_bunches'.")
            if any([isinstance(x,int) for x in list(out.keys())]) or \
                any([isinstance(x,float) for x in list(out.keys())]):
                raise ValueError('This catches when using passing floats or '
                                 'strings as dictionary keys.  You should '
                                 'pass on the dictionarify function if that is'
                                 'really what you want.')
            if speak: print('*'*(level+1)+ 'Bunchify worked, out is:  '+str(out))
            return out
        except:
            if speak: print('*'*(level+1)+' exception raised, out is:  '+str(y))
            return y
    else:
        return x

def ordered_unbunchify(x,out_type=0):
    """ Recursively converts a OrderedBunch into a dictionary, list of tuples, or list of lists
    """
    if isinstance(x,OrderedBunch):
        if out_type==0:
            return _collections.OrderedDict( (k, ordered_unbunchify(v)) for k,v in x.items() )
        elif out_type==1:
            return [(k, ordered_unbunchify(v,out_type=1)) for k,v in x.items()]
        elif out_type==2:
            return [[k, ordered_unbunchify(v,out_type=2)] for k,v in x.items()]
    else:
        return x

def print_recursive(x):
    """Formatted print of OrderedBunch objects or things that can be cast to one."""
    print(_print_recursive_start(x))

def _print_recursive_start(x):
    '''If the incoming object isn't an OrderedBunch, let ordered_bunchify
    take care of formatting for the print'''
    try:
        if not isinstance(x,OrderedBunch):
            ob = ordered_bunchify(ordered_dictionarify(x))
        else:
            ob = x
    except:
        raise SyntaxError("The object passed in can't be cast to an ordered bunch.")

    return _print_recursive_loop(ob)

def _print_recursive_loop(ob,depth=0):
    """Return string to be used in the formatted printing of OrderedBunch objects.
    """

    # Put together the string to return
    sss = ''
    d1 = 7
    d2 = 25
    # If incoming object is empty, return sss as an empty string.
    if len(ob) == 0:
        return sss
    # Gen max length of labels to set prefix length
    prelen = max([len(x) for x in list(ob.keys())])
    depmarks = '-'*depth
    width_set = 80

    for k,v in ob.items():
        prefix = depmarks + k + ' '*(prelen-len(k))+' : '
        wrapper = _textwrap.TextWrapper(initial_indent=prefix,
                                        width=width_set,
                                        replace_whitespace=False,
                                        subsequent_indent=' '*len(prefix))
        if isinstance(v,OrderedBunch):
            message = str(type(v))

            # Handle different message formats:
            # If message contains new lines, just pass those through to print.
            if message.find('\n') != -1:
                sss = sss + prefix + message.replace('\n','\n'+' '*prelen)+'\n'
            # Else if message is not empty, pass to wrapper.fill
            elif message:
                sss = sss + wrapper.fill(message) + '\n'
            # Else just pass the empty message along with prefix
            else:
                sss = sss + prefix + '\n'

            sss = sss + _print_recursive_loop(v,depth=depth+1)
        else:
            message = str(v)

            # Handle different message formats:
            # If message contains new lines, just pass those through to print.
            if message.find('\n') != -1:
                sss = sss + prefix + message.replace('\n','\n'+' '*prelen)+'\n'
            # Else if message is not empty, pass to wrapper.fill
            elif message:
                sss = sss + wrapper.fill(message) + '\n'
            # Else just pass the empty message along with prefix
            else:
                sss = sss + prefix + '\n'

    return sss

def guess_dtype_convert_dict(x):
    """Guesses the type of the entries in a dictionary (recursive) and
    writes the guesses into the dictionary (no need to return a var)."""
    for k,v in x.items():
        if isinstance(v,dict):
            guess_dtype_convert_dict(v)
        else:
            x[k] = guess_dtype_convert_var(v)

def guess_dtype_convert_var(x):
    """Guess at the type of a string and pass that type back."""
    # If the variable is not a string of some sort, then just return it.
    if not isinstance(x,str):
        return x
    # If the string looks like a list of numbers, then chop it up and convert.
    # BE CAREFUL WITH THIS... THIS IS BEST SUITED TO HANDLE PVL TYPE FILES -
    #  IF SET ON A DESCRIPTION STRING, THIS COULD REALLY MESS IT UP.  This
    # has been protected pretty well, but if you pass in a string that starts
    # with a number, stuff could go bad.
    if len(x.split(',')) > 1:
        xx = x.split(',')
        try:
            float(xx[0])
            return [guess_dtype_convert_var(y.strip()) for y in xx]
        except:
            pass
    elif len(x.split()) > 1:
        xx = x.split()
        try:
            float(xx[0])
            return [guess_dtype_convert_var(y.strip()) for y in xx]
        except:
            pass
    # Convert the variable is you can, if you can't, pass it out.
    try:
        return float(x) if '.' in x else int(x)
    except:
        try:
            return str(x)
        except:
            return x
