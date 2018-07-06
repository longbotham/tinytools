import sys as _sys
import itertools as _itertools
import posixpath as _pp
import os as _os
import timeit as _timeit
import numpy as _np

def test_with_binaryfile_copy(src,dest,fsize=100,ncopies=5):
    """This function creates a binary file and then runs copy statistics to
    multiple locations.  This should produce a reliable estimate of disk I/O
    performance, though, it is limited to mounted disks (it does not
    support http, ftp, etc.).

    Locations should be specified with a linux style "/" separator if
    possible.  The function will attempt to handle windows style file paths,
    but they are not well supported in Python when passed in as string.  See:
    http://gis.stackexchange.com/questions/63816/python-formatting-path-strings-and-checking-if-a-path-exists
    http://pythonconquerstheuniverse.wordpress.com/2008/06/04/gotcha-%E2%80%94-backslashes-in-windows-filenames/

    src   : The location where the file will be created and copied from.  If
            src is a list, multiple tests are run from each location.
    dest  : The lcation(s) where the binary file will be copied to.  If dest
            is a list, multiple tests are run to each location.
    fsize : size of the file to use - in MB (default is 100 MB)
    """

    # Just handle all paths with linux style separators.  This seems to work
    # in timeit.  Passing in correctly formatted windows paths, didn't work.
    if hasattr(src,'__iter__'):
        for i,v in enumerate(src):
            if _sys.platform == "win32" and ('\\' in v):
                src[i] = repr(v)[1:-1].replace("\\","/").replace("//","/")
    else:
        if _sys.platform == "win32" and ('\\' in src):
            src = repr(src)[1:-1].replace("\\","/").replace("//","/")
    if hasattr(dest,'__iter__'):
        for i,v in enumerate(dest):
            if _sys.platform == "win32" and ('\\' in v):
                dest[i] = repr(v)[1:-1].replace("\\","/").replace("//","/")
    else:
        if _sys.platform == "win32" and ('\\' in dest):
            dest = repr(dest)[1:-1].replace("\\","/").replace("//","/")

    tf = "temp.bin"
    if isinstance(src,str):
        src = [_pp.join(*i) for i in _itertools.product([src],[tf])]
    elif hasattr(src,'__iter__'):
        src = [_pp.join(*i) for i in _itertools.product(src,[tf])]
    else:
        raise TypeError

    if isinstance(dest,str):
        dest = [_pp.join(*i) for i in _itertools.product([dest],[tf])]
    elif hasattr(src,'__iter__'):
        dest = [_pp.join(*i) for i in _itertools.product(dest,[tf])]
    else:
        raise TypeError

    ### Start looping through tests
    for enu,i in enumerate(src):
        # Make binary file
        print('')
        print("***** Source "+str(enu+1)+" of " \
                +str(len(src))+" *****")
        print("Creating a binary file to copy from at:")
        print(i)
        with open(i,'wb') as fout:
            fout.write(_os.urandom(int(1024*1024*fsize)))

        for ind,j in enumerate(dest):

            print('')
            print("*** Copy destination "+str(ind+1)+" of " \
                    +str(len(dest))+" ***")
            print("Destination location: %s" % j)
            #print "Source location : %s" % i
            # copy to destination and record stats

            cmd = "shutil.copy('"+i+"','"+j+"')"
            #print i
            #print j
            #print cmd
            tvec = _timeit.repeat(cmd,setup="import shutil",
                                 repeat=ncopies,number=1)

            print("Average copy time is:  %s" % _np.mean(tvec))
            print("Standard deviation of copy time is:  %s" % _np.std(tvec))

            print("Removing file %s" % j)
            _os.remove(j)

        print("Removing file %s" % i)
        _os.remove(i)

# def test_with_dd(test_path):
#     """
#     ####################################################################
#     WARNING - IF YOU RUN THIS COMMAND IN A BAD SPOT AND/OR WITH ELEVATED
#     PERMISSIONG, IT WILL RUIN YOUR WORLD.  YOU HAVE BEEN WARNED!
#     ####################################################################
#     :param test_path:
#     :return:
#     """
#
#     # Test read/write with built in file creation/reading/writing.
#     # Linux only - I guess you could get this going with cygwin if you
#     # really want.
#     # $ dd if=/dev/zero of=testfile0 bs=8k count=10000; sync;
#     # 10000+0 records in
#     # 10000+0 records out
#     # 81920000 bytes (82 MB) copied, 0.830531 s, 98.6 MB/s
#     # $ dd if=testfileR of=/dev/null
#     # 135552+0 records in
#     # 135552+0 records out
#     # 69402624 bytes (69 MB) copied, 0.123926 s, 560 MB/s
#     # $ dd if=/dev/zero of=testfile0 bs=8k count=100000; sync;
#     # 100000+0 records in
#     # 100000+0 records out
#     # 819200000 bytes (819 MB) copied, 8.30592 s, 98.6 MB/s
#     # $ dd if=/dev/urandom of=testfileR bs=8k count=10000; sync;
#     # 10000+0 records in
#     # 10000+0 records out
#     # 81920000 bytes (82 MB) copied, 13.779 s, 5.9 MB/s
#
#     # The above "...; sync;" probably doesn't do anything.
#     # http://linuxaria.com/pills/how-to-properly-use-dd-on-linux-to-benchmark-the-write-speed-of-your-disk
#     #dd bs=1M count=128 if=/dev/zero of=test conv=fdatasync
