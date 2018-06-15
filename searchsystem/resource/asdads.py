'''
Created on 2018年6月14日

@author: hsw
'''
from docutils.parsers.rst.directives import encoding
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
fp = open(r'/Volumes/zhz/WSM_project/CH/生命中的过客_生活随笔_短文学_7297.txt')
a = fp.readlines()
print(a)