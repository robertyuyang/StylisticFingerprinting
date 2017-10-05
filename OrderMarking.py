# -*- coding: utf-8 -*-
from sys import argv
import numpy
import os
import hashlib
import getopt
import shutil

def WalkFiles(input_dir, file_list, ex):
  print(input_dir)
  for parent,dirnames,filenames in os.walk(input_dir):
    for dirname in  dirnames:
      print("the full name of the dir is:" + os.path.join(parent,dirname))
      #WalkFiles(os.path.join(parent, dirname), file_list)
      #print("parent is:" + parent)
      #print("dirname is" + dirname)

    for filename in filenames:
      if not filename.endswith(ex):
        continue;
      #print("parent is:" + parent)
      #print("filename is:" + filename)
      #print("the full name of the file is:" + os.path.join(parent,filename))
      file_list.append(os.path.join(parent,filename))

class OrderMarking:
  def __init__(self, args):
    try:
      (opts, filenames) = getopt.getopt(args, '', ['help',
                                                   'input-dir=',
                                                   'analyzer=',
                                                   'project='
                                                   ])
    except getopt.GetoptError:
      print 'Invalid arguments.'

    for(key, val) in opts:
      if key == '--input-dir':
        self.input_dir = val
      elif key == '--analyzer':
        self.analyzer = str(val).lower()
      elif key == '--project':
        self.project = val

  def createFileWithClass(self, file_path, file_path_with_class):
    f = open(file_path)
    tmp_file = open(file_path_with_class, 'w')
    tmp_file.write('public class TestClass {' + os.linesep + f.read() + os.linesep + '}')
    f.close()
    tmp_file.close()

  def checkstyleMark(self, file_path):
    violation_count = 0

    tmp_file_path = './tmp_file.java'
    self.createFileWithClass(file_path, tmp_file_path)


    output_lines = []
    output_lines.extend(os.popen('java -jar ./analyzer/checkstyle-8.2-all.jar -c /google_checks.xml ' + tmp_file_path).readlines())
    output_lines.extend(os.popen('java -jar ./analyzer/checkstyle-8.2-all.jar -c /sun_checks.xml ' + tmp_file_path).readlines())
    for line in output_lines:
      if line.startswith('['):
        violation_count = violation_count + 1

    print file_path + '   checkstyle violation count :' + str(violation_count)
    return violation_count



  def pmdMark(self, file_path):
    violation_count = 0
    output_lines = []
    tmp_file_path = './tmp_file.java'
    self.createFileWithClass(file_path, tmp_file_path)

    cmd = './analyzer/pmd-bin-5.8.1/bin/run.sh pmd -d ' + tmp_file_path +' -R rulesets/java/basic.xml,rulesets/java/design.xml,rulesets/java/braces.xml,rulesets/java/comments.xml,rulesets/java/codesize.xml,rulesets/java/controversial.xml,rulesets/java/naming.xml -f csv'
    output_lines.extend(os.popen(cmd).readlines())
    violation_count = len(output_lines) - 1
    print file_path + '   pmd violation count :' + str(violation_count)
    return violation_count

  def markfile(self, file_path):
      return self.checkstyleMark(file_path) + self.pmdMark(file_path)
  def mark(self):
    file_list = []
    file_mark = {}
    WalkFiles(self.input_dir, file_list, '.java')

    dir_for_marking = 'dir_for_marking'
    if not (os.path.isdir(dir_for_marking) and os.path.exists(dir_for_marking)):
      os.mkdir(dir_for_marking)
    for file_path in file_list:
      new_file_path = dir_for_marking + os.sep + os.path.basename(file_path)
      self.createFileWithClass(file_path, new_file_path)


    index = 0
    total_file_count = len(file_list)
    for file_path in file_list:
      file_mark[file_path] = self.markfile(file_path)
      index = index + 1
      print "%d / %d" %(index, total_file_count)

    sorted_file_marks = sorted(file_mark.items(), key=lambda x: x[1], reverse=False)

    count = len(sorted_file_marks)
    top_file_marks = sorted_file_marks[0: count/4]
    bottom_file_marks = sorted_file_marks[count * 3/4:]
    print top_file_marks
    print bottom_file_marks

    top_file_dir = self.project + '_top'
    if not (os.path.isdir(top_file_dir) and os.path.exists(top_file_dir)):
      os.mkdir(top_file_dir)
    for (top_file_path, mark) in top_file_marks:
      shutil.copy(top_file_path, top_file_dir+ os.sep+ os.path.basename(top_file_path))

    bottom_file_dir = self.project + '_bottom'
    if not (os.path.isdir(bottom_file_dir) and os.path.exists(bottom_file_dir)):
      os.mkdir(bottom_file_dir)
    for (bottom_file_path, mark) in bottom_file_marks:
      shutil.copy(bottom_file_path, bottom_file_dir+ os.sep+ os.path.basename(bottom_file_path))







if (__name__ == '__main__'):

  orderMarking = OrderMarking(argv[1:])
  orderMarking.mark()


