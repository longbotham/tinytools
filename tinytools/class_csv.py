import csv as _csv
import os as _os

### Classification object of labeled samples
### -- include write to csv
### -- include filter class
### -- include remove feature
### -- include create ndi ratios code
def move_first_col_to_last(fcsv):
    """Change a csv file to a fomat that may be more useful by moving the
    first column to the end of the file.  Input is a csv file on disk that
    is overwritten.
    """
    # Read into table
    with open(fcsv,"r") as f:
        reader = _csv.reader(f)
        table = [row for row in reader]
    # Cycle through table and write rows back with first column moved
    with open(fcsv,"w") as f:
        writer = _csv.writer(f,lineterminator=_os.linesep)
        for row in table:
            writer.writerow(row[1:]+[row[0]])
    #csv = pd.read_csv(fcsv)
    #new = pd.concat([csv.iloc[:,1:],csv.iloc[:,0]],axis=1)
    # new = [csv.iloc[:,1:],csv.iloc[:,0]][0]  # another way to do prev line
    #new.to_csv(fcsv,index=False)
