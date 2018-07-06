import subprocess as _subprocess
import shlex as _shlex
import sys as _sys
import os as _os
import logging as _logging

_logger = _logging.getLogger(__name__)

def is_tool(program):
    """Test if the tool in "program" string is available on the command line.
    This is nearly equivalent to the linux "which" command.  Note that on
    Windows, this tool will not return True on "built-in" commands.  See:
    http://superuser.com/questions/229945/where-are-the-standard-windows-prompt-commands-files
    """
    assert isinstance(program,str), "Input must be a string"

    if _sys.platform == "win32" and not program.endswith(".exe"):
        _logger.debug('Setting windows exe extensions due to platform.')
        program += ".exe"

    fpath, fname = _os.path.split(program)
    # if fpath, then the tools has been given the full path to the command
    # to check, so it should directly check that location.
    if fpath:
        _logger.debug('Checking full path that was passed in...')
        if _is_exe(program):
            _logger.debug('Found tool using passed in path.')
            #return program
            return True
        else:
            _logger.debug('Did not find tool using pass in path.')
            
    # if no fpath, then is_tool was just given the name of the command, so
    # it should go check the PATH env and search for the tool.
    else:
        _logger.debug('Using os.environ["PATH"] to check all possible paths.')
        for path in _os.environ["PATH"].split(_os.pathsep):
            path = path.strip('"')
            exe_file = _os.path.join(path, program)
            if _is_exe(exe_file):
                _logger.debug('Found tool in PATH')
                #return exe_file
                return True
            else:
                _logger.debug('Did not find tool in PATH')
            
    # if this a platform with bash, the requested program might be an alias,
    # so call interactive bash and check to see if the program is there.
    if (_sys.platform == "linux2" or _sys.platform == "darwin"):
        _logger.debug('Running tool check with subprocess.check_call')
        try:
            # .bashrc file needed for aliases and default subprocess is
            # not interactive (so .bashrc is not sourced).
            # _subprocess.check_call('if [ -f ~/.bashrc ]; '
            #                            'then source ~/.bashrc; '
            #                        'fi; '
            #                        'type '+program+' > /dev/null 2>&1',
            #                        shell=True)

            # Hard coding this to bash.  On ubuntu, sh links to dash
            # which doesn't have source.  This is really just guessing as
            # best it can to find bash aliases - so it makes since to just
            # call bash.
            _subprocess.check_call(['/bin/bash','-i','-c',
                                   'type '+program+' > /dev/null 2>&1'])
            return True
        except Exception as e:
            #print e
            pass

    return False

def _is_exe(fpath):
    """Check if fpath is a file with execute."""
    return _os.path.isfile(fpath) and _os.access(fpath, _os.X_OK)

def exec_cmd(cmd_in,shell=False,ret_output=False,**kwargs):
    """DO NOT USE THIS FUNCTION AND "shell=True" WITH ANY USER INPUT WITHOUT
    UNDERSTANDING THE WARNINGS AT:
    https://python.readthedocs.org/en/v2.7.2/library/subprocess.html

    This is a wrapper for subprocess.  It tries to appropriately handle the
    input, output, and shell variables for the user with needing to know the
    vagaries of when subprocess will fail on different platforms. The input
    can be a string or a list of strings.  The function attempts to
    restructure according to what should be cross-platform compatible for
    the various combinations.

    Note that the string/list interpretation by the subprocess module is
    relatively complex.  See:
    http://stackoverflow.com/questions/15109665/subprocess-call-using-string-vs-using-list

    Warning:  gdal does not seem to trigger an exception on errors - it
    prints the error to screen and moves on.  This is at least true in
    Python (see article below) but also seems to be true for command line
    tools.  Don't expect exceptions to be handled in any gdal command.
    Check success other ways - existence of a file, etc.  It is possible to
    set gdal.UseExceptions() in Python code, but that won't work when
    calling from the command line as here.
    http://trac.osgeo.org/gdal/wiki/PythonGotchas
    http://gis.stackexchange.com/questions/73463/gdal-and-python-dont-print-gdal-error-messages
    http://stackoverflow.com/questions/14523150/python-and-gdal-for-image-processing
    http://gis.stackexchange.com/questions/30445/is-there-a-way-to-properly-have-gdal-raise-exceptions-in-python
    """

    # if cmd is string and shell=True:
    if (isinstance(cmd_in,str) and shell==True):
        # shell is true and command is string = ok
        cmd = cmd_in
        cmd_txt = cmd_in
    elif (isinstance(cmd_in,str) and shell==False):
        # shell is false and command is string = slice it up
        cmd = _shlex.split(cmd_in)
        cmd_txt = cmd_in
    elif (isinstance(cmd_in,list) and shell==True):
        # shell is true and command is list = make cmd_in a string
        cmd = ' '.join(cmd_in)
        cmd_txt = ' '.join(cmd_in)
    elif (isinstance(cmd_in,list) and shell==False):
        # shell if false and command is list = ok
        cmd = cmd_in
        cmd_txt = ' '.join(cmd_in)

    # Print information about the command to the screen
    _logger.debug('')
    _logger.debug('##################')
    _logger.debug('Executing command:')
    _logger.debug(cmd_txt)
    _logger.debug('##################')
    _logger.debug('')

    # Choose which subprocess to call based on desired return value
    if ret_output:
        out = _subprocess.check_output(cmd,shell=shell)
        return out
    else:
        _subprocess.check_call(cmd,shell=shell,**kwargs)
