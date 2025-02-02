"""
Todo:
* Split and write Runtxt correctly

#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2012 Deltares
#       Gerben J. de Boer
#
#       gerben.deboer@deltares.nl
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------

# https://github.com/Carlisle345748/Delft3D-Toolbox/blob/master/delft3d/MdfFile.py
"""
from pyd3d.utils import formatSci
from collections import OrderedDict

class Mdf(object):
    """
    Read/write Delft3D-FLOW *.mdf input files to/from dictionary
    
    Examples
    --------
    >>> from pyd3d.input.mdf import Mdf
    >>> mdf = pyd3d.Mdf('example/example1.mdf')
    
    TODO
    ----
    * Separate file writing and format conversion
    """
    def __init__(self, filename):
        self.filename = filename
        self.data = self.read()
    
    def __RHS2val__(self, line, verbose=False):
        """parse 1(!) RHS line value from *.mdf file to a str, '' or float"""

        if verbose: print("__RHS2val__:", line)

        if "#" in line:
            # its a string!
            _, value, _ = line.split("#", 2)
        elif "[" in line:
            value = ""
        else:
            value = line.strip()
            split_value = value.split()

            if verbose: print("split value", split_value) 

            value = [float(value) for value in split_value]

        return value
    
    def __val2RHS__(self, keyword, value):
        """parse a list of str, '' or floats to multiple (if needed) RHS *.mdf lines"""
        # values that need to be written column-wise rather than row wise (although short row vectors are allowed)
        columnwise_list = [
            "Thick",
            "Rettis",
            "Rettib",
            "u0",
            "v0",
            "s0",
            "t0",
            "C01",
            "C02",
            "C03",
            "C04",
        ]

        # keywords of values should be written as int's
        int_keys = ['MNKmax', 'Iter', 'ncFormat', 'ncDeflate', 'Dt', 'Tzone', 'Restid_timeindex', 'Ktemp','Ivapop', 'Irov', 'Iter']

        if type(value) is str:
            if keyword == "Runtxt":
                # Mangles the runtext
                width = 30
                f.write(f"{keyword.ljust(7)}= #{str(value[:width])}#\n")
                for i in range(width, len(value), width):
                    return f"         #{value[i : i + width]}#\n"
            else:
                # Write these as strings
                return f"{keyword.ljust(7)}= #{value}#\n"
        else:
            # Write these in scientific notation and column-wise
            if keyword in columnwise_list:
                return f"{keyword.ljust(7)}=  {formatSci(value[0])}\n"
                for val in value[1:]:
                    return f"          {formatSci(val)}\n"
            else: 
                # Write these values as simple integers
                if keyword in int_keys:
                    joined_integer_values = " ".join(("%g" % x) for x in value)
                    integer_string_to_write = f"{keyword.ljust(7)}= {joined_integer_values}\n"
                    return integer_string_to_write
                    
                # Write these values in scientific notation
                joined_values = "  ".join(formatSci(x) for x in value)
                sci_string_to_write = f"{keyword.ljust(7)}=  {joined_values}\n"
                return sci_string_to_write

    def read(self, verbose=False):
        """Read Delft3D-FLOW .mdf file into dictionary.
       Note that all comment lines and keyword formatting are not preserved.
       
        Examples
        --------
        >> inp = mdf.read('a.mdf')

        """

        keywords = OrderedDict()

        with open(self.filename, "r") as mdf_file:
            for line in mdf_file.readlines():
                if "=" in line:
                    # make new entry in dict
                    keyword, value = line.split("=", 1)
                    keyword = keyword.strip()

                    value = value.strip()
                    keywords[keyword] = []
                    new = True

                elif not (keyword == "Commnt"):
                    value = line.lstrip()
                    new = False

                if not (keyword == "Commnt"):
                    value = self.__RHS2val__(value)
                    if new:
                        keywords[keyword] = value # either do [value] here
                    else:
                        if type(value) is str:
                            keywords[keyword] = keywords[keyword] + value
                        else:
                            # append a single value to existing keyword
                            keywords[keyword].append(value[0])

            return keywords

    def write(self, keywords, mdf_filename=None, exclude=[]):

        """Write dictionary to Delft3D-FLOW *.mdf file.
       The keywords are written in order,
          >> mdf.write(inp, 'b.mdf')
          >> inp = mdf.read('a.mdf')
          >> mdf.write(keywords, 'b.mdf')

       To ignore a keyword use keyword 'exclude' with list of keywords to ignore, e.g. to enforce cold start:
          >> mdf.write(inp,'c.mdf',exclude=['Restid']) 

       Example: modify time step Dt of collection Delft3D-FLOW simulations:
          >> import mdf, glob, os
          >> mdf_list = glob.glob('*.mdf');
          >> for mdf_file in mdf_list:
          >>    inp = mdf.read(mdf_file)
          >>    inp['Dt'] = [1]
          >>    mdf_base, ext = os.path.splitext(mdf_file)
          >>    mdf.write(inp, mdf_base + '_dt=1' + ext)
          """
        if not mdf_filename:
            print("No filename provided, file will be written is new.mdf in current folder")
            mdf_filename = "new.mdf"

        with open(mdf_filename, "w") as f: 
            lines = []
            
            for keyword in keywords:
                if not (keyword in exclude):
                    value = keywords[keyword]
                    lines.append(self.__val2RHS__(keyword, value))

    
    
