import collections as _collections
import logging as _logging

_logger = _logging.getLogger(__name__)


def _filter_pvl_val_to_type(val):
    """Filter v to int, float, or lead as string."""
    try:
        # Try to make val and integer
        val = int(val)
    except:
        try:
            # Try to make val a float
            val = float(val)
        except:
            # Val remains a string
            val = val.strip('"')

    return val

def read_from_pvl(fname,param_in=None):
    """Function to read parameter values from a pvl (parameter value language)
    file named "fname".  If the param_in value is specified (case sensitive),
    it reads to all matching records from the dictionary in a list.  If
    param_in is not specified, it return the full pvl file in an
    OrderedDictionary.  I've followed rules outlined in the DigitalGlobe
    Image Support Data Format document, but the parser has not been
    extensively validated.  Nesting of lists, sets, and groups is
    technically allowed by the PVL spec but is not supported in this parser.

    The output will be a list of requested value types - i.e. a list of length
    one that contains an OrderedDict.  If there is only one instance of the
    requested key word, then the list will be a length one.
    """

    #Create Ordered Dictionary to populate
    if param_in == None:
        #Create Ordered Dictionary to populate
        out = _collections.OrderedDict()
    else:
        param_in = param_in.strip()

    # Set initial variables
    comment = False
    cont_line = False
    param_hold = None
    val_hold = None
    group_name = None
    group_cont = False
    tmp_od = None
    param_in_vals = []

    # Open file and go to work
    with open(fname,'r') as f:
        for l in f:
            ## Skip blank lines, strip extra spaces, and skip "END;" line
            l = l.strip()
            if not l:
                #print "blank line skip"
                continue
            if l=="END;":
                continue

            #print l

            ## Handle comments
            if ("*/" in l) or ("/*" in l):
                #ipdb.set_trace()
                if l.startswith("/*"):
                    #print "comment true"
                    comment = True
                    continue
                elif l.endswith("/*"):
                    raise SyntaxWarning('A start comment symbol at the end '
                                        'of a line is a bit ambiguous.')
                elif l.startswith("*/") or l.endswith("*/"):
                    #print "comment false"
                    comment = False
                    continue
                else:
                    raise SyntaxWarning('Comment symbols are not allowed in'
                                        ' the middle of a line - at least not '
                                        'in this parser.  =)')
            if comment or l.startswith("#"):
                #print "comment skip"
                continue

            ## Handle parameter/value pairs
            if l.endswith(";"):
                # ... ends with a ;
                # options:
                # -a single good line
                # -the end of (a) previous line(s)
                # -malformed line
                try:
                    (param,val) = l.split("=")
                    param = param.strip()
                    val = val.strip().strip(";")
                except ValueError as e:
                    if (("need more than 1 value to unpack" in str(e)) or
                        ("not enough values to unpack" in str(e))):
                        if not cont_line:
                            raise SyntaxWarning('Line seems to be malformed.')
                        else:
                            param = param_hold
                            val = val_hold+l.strip().strip(";")
                            cont_line = False
                            param_hold = None
                            val_hold = None
            else:
                # ... not ends with a ;
                # options:
                # -start of a line that continues
                # -continuation of a previous line
                # -malformed line
                # -begining/ending of a group
                try:
                    (param,val) = l.split("=")
                    param = param.strip()
                    val = val.strip()
                    if param == "BEGIN_GROUP":
                        group_name = val
                        group_cont = True
                        pass
                    elif param == "END_GROUP":
                        group_cont = False
                        pass
                    else:
                        cont_line = True
                        param_hold = param
                        val_hold = val
                        continue
                except ValueError as e:
                    if ("not enough values to unpack" in str(e)):
                        if not cont_line:
                            raise SyntaxWarning('Line seems to be malformed.')
                        else:
                            param = param_hold
                            val_hold = val_hold+l
                            continue

            # Parse the params and vals for lines and convert formats
            if val.startswith("("):
                # Build list
                #... until crap hapens
                val = val.strip("(").strip(")").split(",")
                val = [_filter_pvl_val_to_type(x) for x in val]
            elif val.startswith("{"):
                # Build set
                _logger.debug("This parser was written without sets defined, "
                             "so they are treated like lists for now.")
                val = val.strip("{").strip("}").split(",")
                val = [_filter_pvl_val_to_type(x) for x in val]
            else:
                val = _filter_pvl_val_to_type(val)

            #Continue building the dictionary unless searching for param_in
            if group_cont and (tmp_od == None):
                # Make the empty dictionary to collect group values
                tmp_od = _collections.OrderedDict()
            elif group_cont and (tmp_od != None):
                # Add to the temp dictionary
                if param_in and (param == param_in):
                    param_in_vals.append(val)
                else:
                    tmp_od[param] = val
            elif not group_cont and (tmp_od != None):
                # Close out tmp dictionary and write to main dictionary
                if param_in:
                    if group_name == param_in:
                        param_in_vals.append(tmp_od)
                else:
                    out[group_name] = tmp_od

                group_name = None
                tmp_od = None
            else:
                #return val
                if param_in:
                    if param == param_in:
                        param_in_vals.append(val)
                else:
                    out[param] = val

    if param_in == None:
        return out
    else:
        if not param_in_vals:
            raise NameError("The parameter '"+str(param_in)+
                            "' was not found "+"in the file "+str(fname))
        else:
            return param_in_vals



def write_dict_to_pvl(fname,dict_in):
    """Function to write a python dictionary to a parameter value
    language file.  Input the name of the file to write and the
    OrderedDictionary to write to the file.  This is mean to be used
    in conjunction with the 'read_from_pvl' function in this same
    packaged.  Nesting of lists, sets, and groups is technically allowed by
    the PVL spec but is not supported in this writer.
    """

    # Convert dictionary to strings in the pvl standard
    sseq = _conv_dict_to_pvl_strings(dict_in)

    # Write string to the file
    with open(fname,'w') as f:
        #f.writelines(['one two\n','three four\n','five'])
        f.writelines(sseq)

def _conv_dict_to_pvl_strings(d,ntabs=-1):
    ntabs = ntabs+1
    slist = []
    for k,v in d.items():
        if isinstance(v,dict):
            slist.append('\t'*ntabs+'BEGIN_GROUP = '+k+'\n')
            slist.append(_conv_dict_to_pvl_strings(v,ntabs))
            slist.append('\t'*ntabs+'END_GROUP = '+k+'\n')
        elif isinstance(v,_collections.OrderedDict):
            slist.append('\t'*ntabs+'BEGIN_GROUP = '+k+'\n')
            slist.append(_conv_dict_to_pvl_strings(v,ntabs))
            slist.append('\t'*ntabs+'END_GROUP = '+k+'\n')
        else:
            # Make a pvl string
            if (isinstance(v,list) or isinstance(v,tuple)):
                slist.append(_build_list_str_for_pvl(k,v,ntabs))
            elif isinstance(v,str):
                slist.append('\t'*ntabs+'%s = "%s";\n' % (k,v))
            else:
                slist.append('\t'*ntabs+"%s = %s;\n" % (k,v))

    if ntabs==0:
        slist.append('END;')

    return ''.join(slist)

def _build_list_str_for_pvl(k,l,ntabs,lwrap=['(',')']):
    slist = []
    #Create first line of list in pvl format
    slist.append('\t'*ntabs+k+" = "+lwrap[0]+"\n")
    #Loop through list to creat strings in pvl format - with quoates around
    # value if they are strings.
    for x in l:
        if isinstance(x,str):
            slist.append('\t'*ntabs+'  "'+str(x)+'",\n')
        else:
            slist.append('\t'*ntabs+'  '+str(x)+',\n')

    #Go back and fix last list to close in pvl format
    if isinstance(l[-1],str):
        slist[-1] = '\t'*ntabs+'  "'+l[-1]+'" '+lwrap[1]+';\n'
    else:
        slist[-1] = '\t'*ntabs+'  '+str(l[-1])+' '+lwrap[1]+';\n'

    return ''.join(slist)

def replace_in_dict(dict,dkey,values):
    """Replace items in a (possibly nested) dictionary.  Values in the list
    "values" are inserted for the dictionary items of name "key".
    """

    assert isinstance(values,list)

    values = _collections.deque(values)
    (dict,values) = _nested_dict_replace(dict,dkey,values)

    if values:
        raise ValueError('More values were passed than were used in the '
                         'dictionary value replace.')

    return dict

def _nested_dict_replace(d,key,values):
    """Iterate replace of values in instance of key in dictionary k."""
    for k,v in d.items():
        if k == key:
            try:
                d[k] = values.popleft()
            except IndexError:
                raise ValueError("There were fewer values passed in than "
                                 "there were instances of key in dict.")
        elif isinstance(v,dict):
            (d[k],values)=_nested_dict_replace(v,key=key,values=values)
        elif isinstance(v,_collections.OrderedDict):
            (d[k],values)=_nested_dict_replace(v,key=key,values=values)
        else:
            pass

    return (d,values)