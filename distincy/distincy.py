# -*- coding: utf-8 -*-
from sys import argv
import numpy
import os
import hashlib

def WalkFiles(input_dir, file_list):
  print(input_dir)
  for parent,dirnames,filenames in os.walk(input_dir):
    for dirname in  dirnames:
      print("the full name of the dir is:" + os.path.join(parent,dirname))
      #WalkFiles(os.path.join(parent, dirname), file_list)
      #print("parent is:" + parent)
      #print("dirname is" + dirname)

    for filename in filenames:
      #print("parent is:" + parent)
      #print("filename is:" + filename)
      #print("the full name of the file is:" + os.path.join(parent,filename))
      file_list.append(os.path.join(parent,filename))


if (__name__ == '__main__'):
  dir = argv[1]
  file_list = []
  WalkFiles(dir, file_list)

  md5_dict = {}
  for file_path in file_list:

    md5file = open(file_path,'rb')
    md5 = hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    if md5_dict.has_key(md5):
      print '%s has same md5 with %s' % (file_path, md5_dict[md5])
      os.remove(file_path)
      file_list.remove(file_path)
    else:
      md5_dict[md5] = file_path



  file_count = 0
  total_line_count = 0.0
  for file_path in file_list:
    if not file_path.endswith('.java'):
      continue;
    file_count = file_count + 1
    line_count = len(open(file_path, 'rU').readlines())
    total_line_count = total_line_count + line_count

  average_line_count = total_line_count / file_count
  print "average_line_count %f" % average_line_count

  standard_deviation = 0.0
  for file_path in file_list:
    if not file_path.endswith('.java'):
      continue;

    line_count = len(open(file_path, 'rU').readlines())
    standard_deviation = standard_deviation + pow(line_count - average_line_count, 2)
  standard_deviation = pow(standard_deviation / file_count, 0.5)
  print ("standard_deviation %f" % standard_deviation)
