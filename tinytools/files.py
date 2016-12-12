import os as _os
import fnmatch as _fnmatch
import numpy as _np
import warnings as _warnings
import csv as _csv

def search(dir,search_strings,ret_relative_paths=False,depth=1,
              ret_files=True,ret_dirs=False,ret_hidden=False,
              case_sensitive=None):
    """
    Utility to provide recursive search.

    Args:
        dir (str): path to the search directory
        search_strings (str or list of strings): String pattern or a list of
                string patterns to search against.
        ret_relataive_paths (bool): Return full paths or relative paths?
        depth (int): Number of levels to decend in search (0 = no limit).
        ret_files (bool): should search return files matching pattern?
        ret_dirs (bool): should search return directories matching pattern?
        case_sensitive (bool/None): should searches be case sensitive (bool)
                or left to the platform default (None)?

    Returns:
        List of strings (files and/or directories) matching requested search
        parameters.  If both files and directories are requested, the
        function will return a tuple of lists, one for files and one for
        directories.

    This function uses os.walk and fnmatch (via tinytools.files.filter), to do a
    recursive search using Unix shell-style wildcards.  The search strings can
    use wildcards per fnmatch:

    *	    matches everything
    ?	    matches any single character
    [seq]	matches any character in seq
    [!seq]	matches any character not in seq

    Dynamic return - if you request both directories and files, this function
    will return a tuple of lists.  One request or the other will return a list.
    Note that turning ret_dirs on does not turn off ret_files (which is on by
    defualt).

    Case sensitivity - This uses the native fnmatch to do matching which means
    that the case-sensitivity is os specific.  On Unix, this means that
    searching for *.tif will not find *.TIF.  If that is what you want, you must
    handle it in the input search_strings list.

    Depth variable - depth will limit how far the function decends if it is not
    set to 0 (defaults to 1 to prevent long searches when a deep path is
    specified).

    ret_hidden=True will return hidden files and files in hidden directories.
    """
    # Check that dir is in fact a dir
    assert _os.path.isdir(dir), "The directory string passed in does not " \
                                "pass the os.path.isdir test."
    # If a string is passed in, covert to a list of length one.
    if isinstance(search_strings,str):
        search_strings = [search_strings]

    # Run recursive search and fill found_files
    found_files = []
    found_dirs = []
    # Set base depth value to compare decent against
    base_depth = _os.path.abspath(dir).count(_os.path.sep)
    # Handle the case that a negative number if passed to depth
    if depth < 0:
        depth = 0
    for root, dirs, files in _os.walk(dir):
        # Build directory return variable
        for s in search_strings:
            for dname in filter(dirs,s,case_sensitive=case_sensitive):
                if _os.path.join(root,dname) not in found_dirs:
                    found_dirs.append(_os.path.join(root,dname))

        # check depth traversed and kill dirs if depth is met
        curr_depth = _os.path.abspath(root).count(_os.path.sep)+1
        #print(curr_depth - base_depth)
        if depth != 0:
            if curr_depth-base_depth >= depth:
                del dirs[:]

        if not ret_hidden:
            # Clear hidden dirs
            files[:] = _fnmatch.filter(files,'[!.]*')
            # Clear hidden files
            dirs[:] = _fnmatch.filter(dirs,'[!.]*')

        for s in search_strings:
            for fname in filter(files,s,case_sensitive=case_sensitive):
                if fname not in found_files:
                    if _os.path.join(root,fname) not in found_files:
                        found_files.append(_os.path.join(root,fname))

    if ret_relative_paths == True:
        pass
    else:
        found_files = [_os.path.abspath(f) for f in found_files]
        found_dirs = [_os.path.abspath(f) for f in found_dirs]

    if ret_files and not ret_dirs:
        return found_files
    elif not ret_files and ret_dirs:
        return found_dirs
    elif ret_files and ret_dirs:
        return (found_files,found_dirs)
    else:
        raise ValueError("Not a valid request... You need to return "
                         "files or dirs.")

def filter(string_list,pattern_list,case_sensitive=None,ret_index=False):
    """...Redone... Need to rewrite this documentation...
    Filter a list of strings with a list of patterns.

    Args:
        string_list (list): List of strings to be filtered.
        pattern_list (list): List of patterns to use as filters
        case_sensitive (bool/None): Should filtering be case_sensitive (bool)
                or left to the platform default (None)?
        ret_index (bool): Should the index list be returned in addition to
                the filtered list.

    Returns:
        Filtered list and/or index list of matched patterns

    The function uses
    fnmatch to compare a list of strings against a list of patterns.  The
    patterns can use wildcards per fnmatch:

    *	matches everything
    ?	matches any single character
    [seq]	matches any character in seq
    [!seq]	matches any character not in seq

    Case sensitivity can be explicitly determined.  If left blank, it uses
    the platform default.  This is useful when searching for files that may
    end in different cases - i.e. .TIF vs .tif when working between windows
    and linux.
    """

    # If input isn't iterable (lists), make them into a list
    if hasattr(pattern_list,'__iter__'):
        pass
    else:
        pattern_list = [pattern_list]

    if hasattr(string_list,'__iter__'):
        pass
    else:
        string_list = [string_list]

    # Assert that a string was passed.  Otherwise, it will explode the
    # element-wise or on the index array union operation below.
    if len(string_list)<1:
        if not ret_index:
            return list()
        else:
            return (list(),list())

    # Create compile re matching objects
    out = _np.zeros(len(string_list),dtype=_np.bool)
    if case_sensitive is None:
        # Use platform case
        for p in pattern_list:
            out=out|_np.array([_fnmatch.fnmatch(s,p) for s in string_list])

    elif case_sensitive is True:
        # Force case sensitive - this kind of doesn't makes sense but the
        # fnmatch documentation makes it sound like you can do case sensitive
        # matching on case-insensitive platforms.
        for p in pattern_list:
            out=out|_np.array([_fnmatch.fnmatchcase(s,p) for s in string_list])

    elif case_sensitive is False:
        # Force no case sensitivity
        for p in pattern_list:
            out=out|_np.array([_fnmatch.fnmatch(s.upper(),p.upper())
                               for s in string_list])

    else:
        raise ValueError('The value of case_sensitive can be True, False, '
                         'or None only.')

    # Either return the filtered list or the filtered list and the index list.
    if not ret_index:
        return list(_np.array(string_list)[out])
    else:
        return (list(_np.array(string_list)[out]),list(out))

def _filter_list_values(x, none_values=None):
    """Filter incoming values for the read_csv below.  It will convert
    floats, ints, boolean, and None values to the python value.  The values
    converted to None by default are '' and 'None'.  NaN values will be
    converted for any string that passes correctly through float(x).
    """
    try:
        x = int(x)
    except ValueError:
        try:
            x = float(x)
        except ValueError:
            pass

    try:
        if x.lower() == 'true':
            x = True
    except AttributeError:
        pass

    try:
        if x.lower() == 'false':
            x = False
    except AttributeError:
        pass

    if none_values == None:
        pass
    elif x in none_values:
        x = None

    return x

def _clean_floats(c_values):
    """The sole purpose of this routine is to catch the case where
    _filter_list_values converts some values to int and some to float.
    That specific case is worrisome since python can act 'unexpectedly'
    with int math.
    """

    c_types = [type(x) for x in c_values]

    if int and float in c_types:
        c_values = [float(x) if isinstance(x,int) else x for x in c_values]

    return c_values

def read_csv(csv_path, none_values=['', 'None']):
    """A very simple csv reader that coverts floats, ints, booleans, and None
    values before passing back a dictionary with keys values equal to the
    values of the first row of the csv.  Filtering of the string values read
    is done with _filter_list_values above.  The values that are passed into
    none_values are converted to python None.  By default converted values
    are empty strings and 'None' strings.
    """

    with open(csv_path, mode='r') as infile:
        reader = _csv.DictReader(infile)
        initialized = False
        for row in reader:
            if not initialized:
                d = {k: [v] for (k, v) in row.iteritems()}
                initialized = True
                continue
            [d[k].append(v) for (k, v) in row.iteritems()]

    # clean the resulting dictionary
    for k in d.iterkeys():
        d[k] = [_filter_list_values(x, none_values=none_values) for x in d[k]]
        d[k] = _clean_floats(d[k])

    return d
