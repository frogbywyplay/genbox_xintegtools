#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

def readfile(file, oneline=False):
        fd_in = open(file, 'r')
        if oneline:
                ret = fd_in.readline()
        else:
                ret = fd_in.readlines()
        fd_in.close()
        return ret
