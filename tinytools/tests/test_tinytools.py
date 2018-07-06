import unittest
import shutil
import filecmp
import os
import glob
import sys
import collections
import numpy as np
import tinytools
from tinytools.bunch import *

class TestCsvTools(unittest.TestCase):
    """Testing for :
    move_first_col_to_last_in_csv
    """
    # Run defined method setUp to setup the test environment
    def setUp(self):
        testpath = os.path.dirname(os.path.realpath(__file__))
        normcsv = os.path.join(testpath,os.pardir,'data','csvfiles',
                               "classification_flat_file.csv")
        self.workingcsv = os.path.join(testpath,'temp.csv')
        shutil.copy(normcsv,self.workingcsv)
        self.colmovedcsv = os.path.join(os.path.dirname(normcsv),
                                "classification_flat_file_firstColToBack.csv")

    def tearDown(self):
        os.remove(self.workingcsv)

    def test_move_first_col_to_last_in_csv(self):
        tinytools.class_csv.move_first_col_to_last(self.workingcsv)
        self.assertTrue(filecmp.cmp(self.colmovedcsv,self.workingcsv))

class TestForNumpyManipulations(unittest.TestCase):
    """Testing for:
    conv_img_to_bandsfirst
    conv_img_to_bandslast
    """
    def setUp(self):
        self.a = np.random.randint(0,2**11,size=(8,174,246)).astype('uint16')

    def tearDown(self):
        self.f = None

    def test_conv_img_to_bandsfirst_shape(self):
        # If rotation worked, the shape locations should be the same
        b = tinytools.np_img.conv_to_bandslast(self.a)
        self.assertEqual(self.a.shape[0],b.shape[-1])

    def test_conv_img_to_bandsfirst_data(self):
        # If rotation worked, the tested arrays should be exactly the same
        b = tinytools.np_img.conv_to_bandslast(self.a)
        self.assertEqual((self.a[0,:,:]-b[:,:,0]).max(),0)

    def test_conv_img_to_bandslast(self):
        b = tinytools.np_img.conv_to_bandslast(self.a)
        c = tinytools.np_img.conv_to_bandsfirst(b)
        self.assertFalse((self.a-c).any())

class TestFileOperations(unittest.TestCase):
    """Testing for:
    recursive_search
    clean_tmp_files
    clean_temp_files
    """
    def setUp(self):
        temp_dirname = "testtmp"
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.dirname = os.path.join(self.path,temp_dirname)
        os.mkdir(self.dirname)
        temp_list = ["temp.csv","tmp.csv","temp.txt","tmp.txt",
                      "testtemp.csv","testtmp.csv"]
        self.flist_full = [os.path.join(self.dirname,i) for i in temp_list]
        self.flist_rel = [os.path.join(os.path.curdir,i) for i in temp_list]
        csv_loc = os.path.join(self.path,os.pardir,'data','csvfiles',
                               "classification_flat_file.csv")
        for f in self.flist_full:
            shutil.copy(csv_loc,f)

    def tearDown(self):
        for f in self.flist_full:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(self.dirname)

    def test_search_full(self):
        flist = tinytools.files.search(self.path,["*temp*","*tmp*"])
        self.assertEqual(flist.sort(),self.flist_full.sort())

    def test_search_relative(self):
        flist = tinytools.files.search(self.path,["*temp*","*tmp*"],
                                           ret_relative_paths=True)
        self.assertEqual(flist.sort(),self.flist_rel.sort())

    def test_search_dir_only(self):
        dlist = tinytools.files.search(self.path,["*temp*","*tmp*"],
                                            ret_files=False,ret_dirs=True)
        self.assertEqual(dlist[0],self.dirname)

    def test_search_dir_and_files(self):
        (flist,dlist) = tinytools.files.search(self.path,["*temp*","*tmp*"],
                                               ret_files=True,ret_dirs=True)
        self.assertEqual(flist.sort(),self.flist_full.sort())
        self.assertEqual(dlist[0],self.dirname)

    def test_search_dir_and_files_outtype(self):
        out = tinytools.files.search(self.path,["*temp*","*tmp*"],
                                            ret_files=True,ret_dirs=True)
        self.assertIsInstance(out,tuple)

    def test_filter_file_endings_nocase_strings(self):
        endings = '*.txt'
        files = ['hello.txt']
        tmp = tinytools.files.filter(files,endings,case_sensitive=False)
        self.assertEqual(tmp,files)

    def test_filter_file_endings_nocase_lists(self):
        endings = ['*.txt','*.TXT','*.tif']
        files = ['/mnt/here/hello.txt','/new/place/now.txt','howdy.txt']
        tmp = tinytools.files.filter(files,endings,case_sensitive=False)
        self.assertEqual(tmp,files)

    def test_filter_file_endings_nocase_stringandlist(self):
        endings = '*.txt'
        files = ['/mnt/here/hello.txt','/new/place/now.txt']
        tmp = tinytools.files.filter(files,endings,case_sensitive=False)
        self.assertEqual(tmp,files)

    def test_filter_file_endings_nocase_listandstring(self):
        endings = ['*.txt','*.tif']
        files = '/mnt/here/hello.txt'
        tmp = tinytools.files.filter(files,endings,case_sensitive=False)
        self.assertEqual(tmp,[files])

    def test_filter_file_endings_nocase_mixedcase(self):
        endings = ['*.tXt','*.tiF']
        files = '/mnt/here/hello.txt'
        tmp = tinytools.files.filter(files,endings,case_sensitive=False)
        self.assertEqual(tmp,[files])

    def test_filter_file_endings_nocase_dupending(self):
        endings = ['*.txt','*.TxT','*.TXT','*.tif','*.TiF']
        files = ['/mnt/here/hello.txT','/again/two.tif']
        tmp = tinytools.files.filter(files,endings,case_sensitive=False)
        self.assertEqual(tmp,files)

    def test_filter_file_endings_casetrue(self):
        endings = ['*.txT']
        files = ['/mnt/here/hello.txT','/mnt/againt.txt','/again/two.tif']
        tmp = tinytools.files.filter(files,endings,case_sensitive=True)
        self.assertEqual(tmp,[files[0]])

    def test_filter_file_endings_casetrue_retindex(self):
        endings = ['*.txT']
        files = ['/mnt/here/hello.txT','/mnt/againt.txt','/again/two.tif']
        (tmp1,tmp2) = tinytools.files.filter(files,endings,case_sensitive=True,
                                     ret_index=True)
        self.assertEqual(tmp1,[files[0]])
        self.assertEqual(tmp2,[True,False,False])

    def test_filter_file_endings_casetrue_retindex(self):
        # This explodes the element-wise or so there is an explict
        # short-circut in the code now
        tmp = tinytools.files.filter([],['*.tif'])
        self.assertTrue(len(tmp)==0)

class TestCmdLineTools(unittest.TestCase):
    """Testing for:
    is_tool
    exec_cmd
    """

    def setUp(self):
        self.istool_cross_platform = 'dir'
        if os.name == 'posix':
            self.istool_str_good = 'sh'
            self.istool_str_bad = 'badcommand'
            self.arg_string_bad = 'ls -e'
            self.arg_list_bad = ['ls','-e']
            self.arg_string_good = 'ls -al'
            self.arg_list_good = ['ls','-al']
            self.args_string_return = 'echo hi'
            self.args_list_return = ['echo','hi']
        elif os.name == 'nt':
            self.istool_str_good = 'cmd' #this is a Windows "external" command
            self.istool_str_bad = 'badcommand'
            self.arg_string_bad = 'dir -e'
            self.arg_list_bad = ['dir','-e']
            self.arg_string_good = 'dir -al'
            self.arg_list_good = ['ls','-al']
            self.args_string_return = 'echo hi'
            self.args_list_return = ['echo','hi']

    def test_is_tool_false(self):
        self.assertFalse(tinytools.cmd_line.is_tool(self.istool_str_bad))

    def test_is_tool_true(self):
        self.assertTrue(tinytools.cmd_line.is_tool(self.istool_str_good))

    @unittest.skip("I'm not really sure how to test that this tool accurately "
                   "finds alias programs through a unittest.")
    def test_is_tool_alias(self):
        pass
        # I'm not really sure how to test this

    @unittest.skip("dir is not really cross platform (Mac)")
    def test_exec_cmd_cross_platform(self):
        fname = os.path.realpath(__file__)
        (testdname,testfname) = os.path.split(fname)
        dirhold = os.getcwd()
        os.chdir(testdname)
        flist = tinytools.cmd_line.exec_cmd(self.istool_cross_platform,
                                            shell=True,ret_output=True)
        os.chdir(dirhold)
        self.assertIn(testfname,flist)

    ### Test the exec_cmd fails with bad args and the different inputs ###
    @unittest.skip("This check of shell fails on Mac")
    def test_exec_cmd_fail_string_true(self):
        raised = False
        try:
            tinytools.cmd_line.exec_cmd(self.arg_string_bad,shell=True)
        except:
            raised = True
        self.assertTrue(raised, 'Exception raised')

    @unittest.skip("This check of shell fails on Mac")
    def test_exec_cmd_fail_string_false(self):
        raised = False
        try:
            tinytools.cmd_line.exec_cmd(self.arg_string_bad,shell=False)
        except:
            raised = True
        self.assertTrue(raised, 'Exception raised')

    @unittest.skip("This check of shell fails on Mac")
    def test_exec_cmd_fail_list_true(self):
        raised = False
        try:
            tinytools.cmd_line.exec_cmd(self.arg_list_bad,shell=True)
        except:
            raised = True
        self.assertTrue(raised, 'Exception raised')

    @unittest.skip("This check of shell fails on Mac")
    def test_exec_cmd_fail_list_false(self):
        raised = False
        try:
            tinytools.cmd_line.exec_cmd(self.arg_list_bad,shell=False)
        except:
            raised = True
        self.assertTrue(raised, 'Exception raised')

    ### Test the exec_cmd suceeds with different inputs ###
    def test_exec_cmd_succeed_string_true(self):
        raised = False
        try:
            tinytools.cmd_line.exec_cmd(self.arg_string_good,shell=True)
        except:
            raised = True
        self.assertFalse(raised)

    def test_exec_cmd_succeed_string_false(self):
        raised = False
        try:
            tinytools.cmd_line.exec_cmd(self.arg_string_good,shell=False)
        except:
            raised = True
        self.assertFalse(raised)

    def test_exec_cmd_succeed_list_true(self):
        raised = False
        try:
            print(self.arg_list_good)
            tinytools.cmd_line.exec_cmd(self.arg_list_good,shell=True)
        except:
            raised = True
        self.assertFalse(raised)

    def test_exec_cmd_succeed_list_false(self):
        raised = False
        try:
            print(self.arg_list_good)
            tinytools.cmd_line.exec_cmd(self.arg_list_good,shell=False)
        except:
            raised = True
        self.assertFalse(raised)

    ### Test the exec_cmd returns coorect ###
    def test_exec_cmd_return_string_true(self):
        out = tinytools.cmd_line.exec_cmd(self.args_string_return,shell=True,
                                ret_output=True)
        self.assertEqual(out,b'hi\n')

    def test_exec_cmd_return_string_false(self):
        out = tinytools.cmd_line.exec_cmd(self.args_string_return,shell=False,
                                ret_output=True)
        self.assertEqual(out,b'hi\n')

    def test_exec_cmd_return_list_true(self):
        out = tinytools.cmd_line.exec_cmd(self.args_list_return,shell=True,
                                ret_output=True)
        self.assertEqual(out,b'hi\n')

    def test_exec_cmd_return_list_false(self):
        out = tinytools.cmd_line.exec_cmd(self.args_list_return,shell=False,
                                ret_output=True)
        self.assertEqual(out,b'hi\n')

class TestDiskIoTools(unittest.TestCase):
    """Testing for:
    test_disk_io_with_binaryfile_copy
    """
    def setUp(self):
        print("Setting up:")
        # Name of source/destination directories
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.source_loc = []
        self.source_loc.append(os.path.join(this_dir,'tmp_source_loc1'))
        self.source_loc.append(os.path.join(this_dir,'tmp_source_loc2'))
        self.dest_loc = []
        self.dest_loc.append(os.path.join(this_dir,'tmp_dest_loc1'))
        self.dest_loc.append(os.path.join(this_dir,'tmp_dest_loc2'))

        # Make the source/destination directories if they don't exist
        for i in self.source_loc:
            if not os.path.exists(i):
                os.mkdir(i)
        for i in self.dest_loc:
            if not os.path.exists(i):
                os.mkdir(i)

        # Test if temp.bin files are already exist and, if so, remove
        for i in self.source_loc:
            tfile = os.path.join(i,"temp.bin")
            if os.path.exists(tfile):  print("removing"); os.remove(tfile)
        for i in self.dest_loc:
            tfile = os.path.join(i,"temp.bin")
            if os.path.exists(tfile):  print("removing"); os.remove(tfile)

    def tearDown(self):
        print("Tearing down:")
        # Test if temp.bin files are already exist and, if so, remove
        for i in self.source_loc:
            tfile = os.path.join(i,"temp.bin")
            if os.path.exists(tfile):  print("removing"); os.remove(tfile)
        for i in self.dest_loc:
            tfile = os.path.join(i,"temp.bin")
            if os.path.exists(tfile):  print("removing"); os.remove(tfile)

        # Remove the source/destination directories
        for i in self.source_loc:
            if os.path.exists(i):
                os.rmdir(i)
        for i in self.dest_loc:
            if os.path.exists(i):
                os.rmdir(i)

    def test_test_disk_io_with_binaryfile_copy(self):
        tinytools.diskio.test_with_binaryfile_copy(self.source_loc[0],
                                                   self.dest_loc[0],fsize=.1)
        ## If test ran sucessfully, the temp.bin files shouldn't still exist
        ## they will be cleaned up in tearDown, but this should be valid now.
        # temp.bin not in start_loc
        t1 = "temp.bin" in glob.glob(
            os.path.join(self.source_loc[0],"temp.bin"))
        # temp.bin not id end_loc
        t2 = "temp.bin" in glob.glob(
            os.path.join(self.dest_loc[0],"temp.bin"))
        # test ran without failure
        t3 = True # The test should fail if the function fails - so there is no
                  # need to explicitly test that the function succeeded.
        self.assertTrue((not t1) & (not t2) & t3)

    def test_test_disk_io_with_binaryfile_copy_lists(self):
        tinytools.diskio.test_with_binaryfile_copy(self.source_loc,
                                                   self.dest_loc,fsize=.1)
        ## If test ran sucessfully, the temp.bin files shouldn't still exist
        ## they will be cleaned up in tearDown if not, but this should
        ## be valid now.
        # temp.bin not in start_loc
        t1 = True
        for i in self.source_loc:
            if "*temp.bin" in glob.glob(os.path.join(i,"temp.bin")):
                t1 = False
        # temp.bin not id end_loc
        t2 = True
        for i in self.dest_loc:
            if "*temp.bin" in glob.glob(os.path.join(i,"temp.bin")):
                t2 = False
        # test ran without failure
        t3 = True # The test should fail if the function fails - so there is no
                  # need to explicitly test that the function succeeded.
        self.assertTrue(t1 & t2 & t3)

class TestStyleIllustrations(unittest.TestCase):
    """Testing for:
    print_all_styles_to_screen
    """

    def test_print_all_styles_to_screen(self):
        tinytools.py_styles.print_all_styles_to_screen()
        # This is basically testing the the function runs without errors
        self.assertTrue(True)

class TestPvlTools(unittest.TestCase):
    """Testing for:
    _filter_pvl_val_to_type
    read_from_pvl
    """
    def setUp(self):
        self.pvl_file = os.path.dirname(
                        os.path.dirname(os.path.realpath(__file__)))+ \
                        os.sep+"data"+os.sep+"test.IMD"
        self.test_out_loc = os.path.dirname(
                            os.path.dirname(os.path.realpath(__file__)))+ \
                            os.sep+"tests"+os.sep+"tmp.IMD"

    def tearDown(self):
        try:
            os.remove(self.test_out_loc)
        except OSError:
            pass

    def test_read_from_pvl_to_dict(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file)
        self.assertIsInstance(out,collections.OrderedDict)

    def test_read_from_pvl_to_subdict(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file)
        self.assertIsInstance(out['BAND_B'],collections.OrderedDict)

    def test_read_from_pvl_param_passed_no_output(self):
        with self.assertRaises(NameError):
            tinytools.pvl.read_from_pvl(self.pvl_file,"Not_match_value")

    def test_filter_pvl_val_int(self):
        out = tinytools.pvl._filter_pvl_val_to_type("1")
        self.assertIsInstance(out,int)

    def test_filter_pvl_val_float(self):
        out = tinytools.pvl._filter_pvl_val_to_type("1.1")
        self.assertIsInstance(out,float)

    def test_filter_pvl_val_str(self):
        out = tinytools.pvl._filter_pvl_val_to_type("string")
        self.assertIsInstance(out,str)

    def test_filter_pvl_val_str_w_quotes(self):
        out = tinytools.pvl._filter_pvl_val_to_type('"string"')
        self.assertEqual(out,'string')

    def test_read_from_pvl_param_passed_int(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file,"mapZone")
        self.assertEqual(out,[13])

    def test_read_from_pvl_param_passed_float(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file,"meanSatEl")
        self.assertEqual(out,[68.6])

    def test_read_from_pvl_param_passed_str(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file,"datumName")
        self.assertEqual(out,["WE"])

    def test_read_from_pvl_param_passed_nested(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file,"BAND_B")
        self.assertIsInstance(out[0],collections.OrderedDict)

    def test_read_from_pvl_param_passed_multiline(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file,"datumOffset")
        self.assertEqual(out,[[0.000, 0.000, 0.000]])

    def test_read_from_pvl_param_passed_mutliinstance(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file,"ULLon")
        self.assertTrue(len(out)==8)

    def test_write_dict_to_pvl_exists(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file)
        tinytools.pvl.write_dict_to_pvl(self.test_out_loc,out)
        self.assertTrue(os.path.exists(self.test_out_loc))

    def test_write_dict_to_pvl_read_write_loop(self):
        out1 = tinytools.pvl.read_from_pvl(self.pvl_file)
        tinytools.pvl.write_dict_to_pvl(self.test_out_loc,out1)
        out2 = tinytools.pvl.read_from_pvl(self.test_out_loc)
        self.assertTrue(out1['version']==out2['version'])
        self.assertTrue(out1['generationTime']==out2['generationTime'])
        self.assertTrue(out1['BAND_C']['ULLon']==out2['BAND_C']['ULLon'])

    @unittest.skip("I write out time strings as... strings.  However, the factory"
                   "puts out PVL files with time as non-string objects.  I'm leaving"
                   "this test turned off for now because I think I'm going to just"
                   "leave as is until I find a reason not to.")
    def test_write_dict_to_pvl_write_time(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file)
        tinytools.pvl.write_dict_to_pvl(self.test_out_loc,out)
        with open(self.pvl_file,"r") as f:
            counter = 0
            for line in f:
                counter+=1
                if counter == 2:
                    time_line1 = line
        with open(self.test_out_loc,"r") as f:
            counter = 0
            for line in f:
                counter+=1
                if counter == 2:
                    time_line2 = line
        self.assertTrue(time_line1 == time_line2)

    def test_replace_value_in_dict(self):
        out = tinytools.pvl.read_from_pvl(self.pvl_file)
        tinytools.pvl.replace_in_dict(out,'ULLon',[1,1,1,1,1,1,1,1])
        self.assertTrue(out['BAND_C']['ULLon']==1)
        self.assertTrue(out['BAND_N2']['ULLon']==1)


class TestBunch(unittest.TestCase):
    """Testing for:
    tinytools.bunch
    """
    def setUp(self):
        fill = {'a':1,'b':{'c':'string'}}
        self.dicts = []
        self.dicts.append({'a': 'one', 'b': 'two',
                                        'c': {'aa': 1, 'bb': 1.23}})
        self.dicts.append(collections.OrderedDict([('a', 'one'), ('b', 'two'),
                    ('c', collections.OrderedDict([('aa', 1), ('bb', 1.23)]))]))
        self.dicts.append([('a', 'one'), ('b', 'two'),
                                        ('c', [('aa', 1), ('bb', 1.23)])])
        self.dicts.append([['a', 'one'], ['b', 'two'],
                                        ['c', [['aa', 1], ['bb', 1.23]]]])
        self.dicts.append(collections.OrderedDict([('a','one'),('b','two'),
                                        ('c',[('aa',1),('bb',1.23)])]))
        self.dicts.append([('a', 'one'), ('b', (4,5,6)),
                                        ('c', [('aa', 1), ('bb', [1,2,3,4])])])
        self.dicts.append([('a', 'one'), ('b', (4,5)),
                                        ('c', [('aa', 1), ('bb', [1,2])])])
        self.dicts.append([('bb',['mul','pan','swir']),['aaa',['mul','pan']]])

        self.dicts2 = []
        self.dicts2.append([('b', 1), ('a',['mul','pan'])])
        self.dicts2.append([('b', 1), ('aa',['mul','pan'])])
        self.dicts2.append([('b', 1), ('a', ['mul', 'pan'])])

        self.dicts3 = []
        self.dicts3.append([('b', 1), ('a',[['c',['mul','pan']]])])

        self.dicts3.append([['a', 1], ['c',
                                      [['aa', ['mul', 'pan']],
                                       ['bb', 1.23],
                                       ['cc',['mul2']]]]])

        self.dicts4 = []
        self.dicts4.append(collections.OrderedDict({'a':[[[1,2],[3,4]]]}))

    def test_lists_of_list_length_one(self):
        for li,lv in enumerate(self.dicts4):
            din = self.dicts4[li]
            ob = ordered_bunchify(ordered_dictionarify(din))
            print(repr(ob))

            a = isinstance(ob,OrderedBunch)
            b = isinstance(ob[list(ob.keys())[0]],list)

            self.assertTrue(a & b)

    def test_nested_lists(self):
        for li,lv in enumerate(self.dicts2):
            din = self.dicts2[li]
            ob = ordered_bunchify(ordered_dictionarify(din))
            print(repr(ob))

            a = isinstance(ob,OrderedBunch)
            b = isinstance(ob[list(ob.keys())[1]],list)
            c = list(ob.keys())[1] == din[1][0]

            self.assertTrue(a & b & c)

    def test_nested_bunches(self):
        for li,lv in enumerate(self.dicts3):
            din = self.dicts3[li]
            ob = ordered_bunchify(ordered_dictionarify(din))
            print(repr(ob))

            a = isinstance(ob,OrderedBunch)
            b = isinstance(ob[list(ob.keys())[1]],OrderedBunch)
            c = list(ob.keys())[1] == din[1][0]

            self.assertTrue(a & b & c)

    def test_ordered_bunchify_list_of_strings(self):
        li = 7
        ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
        print(repr(ob))
        a = isinstance(ob,OrderedBunch)
        b = isinstance(ob['aaa'],list)
        c = len(ob['aaa'])==2
        d = len(ob['bb'])==3
        self.assertTrue(a and b and c and d)

    def test_ordered_bunchify_dictsliststuples(self):
        for li in [0,1,2,3,4]:
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
            print(repr(ob))
            a = isinstance(ob,OrderedBunch)
            b = isinstance(ob['c'],OrderedBunch)
            c = len(ob)==3
            self.assertTrue(a and b and c)

    def test_ordered_bunchify_nested_tuples_and_lists(self):
        li = 5
        ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
        print(repr(ob))
        a = isinstance(ob,OrderedBunch)
        b = isinstance(ob['c'],OrderedBunch)
        c = len(ob)==3
        d = len(ob['b'])==3
        e = len(ob['c']['bb'])==4
        self.assertTrue(a and b and c and d and e)

    def test_ordered_bunchify_len2tuples_and_lists(self):
        li = 6
        ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
        print(repr(ob))
        a = isinstance(ob,OrderedBunch)
        b = isinstance(ob['c'],OrderedBunch)
        c = len(ob)==3
        d = len(ob['b'])==2
        e = len(ob['c']['bb'])==2
        self.assertTrue(a and b and c and d and e)

    def test_ordered_bunchify_dot_access(self):
        for li in range(7):
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
            print(repr(ob))
            a = ob.a=='one'
            b = ob.c.aa==1
            self.assertTrue(a and b)

    def test_ordered_bunchify_dot_assign(self):
        for li in range(7):
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
            print(repr(ob))
            ob.d='test'
            a = ob.d=='test'
            ob.a=[1,2,3,4,5]
            b = ob.a==[1,2,3,4,5]
            self.assertTrue(a and b)

    def test_ordered_unbunchify(self):
        oti = [0,1,2]
        otc1 = [collections.OrderedDict,list,list]
        otc2 = [tuple,tuple,list]
        for li in range(7):
            for x in range(len(oti)):
                ob = ordered_bunchify(ordered_dictionarify(self.dicts[li]))
                out = ordered_unbunchify(ob,out_type=oti[x])
                print(repr(ob))
                print(repr(out))
                print(oti[x])
                print(otc1[x])
                print(otc2[x])
                a = isinstance(out,otc1[x])
                if x==0:
                    b = isinstance(list(out.items())[0],otc2[x])
                else:
                    b = isinstance(out[0],otc2[x])
                self.assertTrue(a and b)

    def test_ob_print_recursive_dicts(self):
        for x in range(7):
            d = self.dicts[x]
            self.assertTrue(len(tinytools.bunch._print_recursive_start(d).split('\n'))==6)

    def test_ob_print_recursive_ordered_bunch(self):
        for x in range(7):
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[x]))
            self.assertTrue(len(tinytools.bunch._print_recursive_start(ob).split('\n'))==6)

    def test_ob_print_recursive_ordered_unbunch_type0(self):
        for x in range(7):
            d = self.dicts[x]
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[x]))
            out = ordered_unbunchify(ob,out_type=0)
            self.assertTrue(len(tinytools.bunch._print_recursive_start(out).split('\n'))==6)

    def test_ob_print_recursive_ordered_unbunch_type1(self):
        for x in range(7):
            d = self.dicts[x]
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[x]))
            out = ordered_unbunchify(ob,out_type=1)
            self.assertTrue(len(tinytools.bunch._print_recursive_start(out).split('\n'))==6)

    def test_ob_print_recursive_ordered_unbunch_type2(self):
        for x in range(7):
            d = self.dicts[x]
            ob = ordered_bunchify(ordered_dictionarify(self.dicts[x]))
            out = ordered_unbunchify(ob,out_type=2)
            self.assertTrue(len(tinytools.bunch._print_recursive_start(out).split('\n'))==6)

if __name__ == '__main__':
    unittest.main()


