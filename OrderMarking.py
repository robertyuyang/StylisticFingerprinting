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

  def createNewDir(self, dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
      os.popen('rm -rf '+dir_path)
      os.mkdir(dir_path)
    else:
      os.mkdir(dir_path)

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


    print'-----distincy start from %d files -------' % len(file_list)
    self.distincy(file_list)
    print'-----distincy end with %d files -------' % len(file_list)

    marking_file_dict = {}

    dir_for_marking = 'dir_for_marking'

    self.createNewDir(dir_for_marking)

    for file_path in file_list:
      new_file_path = dir_for_marking + os.sep + os.path.basename(file_path)
      self.createFileWithClass(file_path, new_file_path)
      marking_file_dict[os.path.basename(new_file_path)] = file_path


    print '------pmd start-------'
    #pmd
    output_lines = []
    cmd = './analyzer/pmd-bin-5.8.1/bin/run.sh pmd -d ' + dir_for_marking + ' -R rulesets/java/basic.xml,rulesets/java/design.xml,rulesets/java/braces.xml,rulesets/java/comments.xml,rulesets/java/codesize.xml,rulesets/java/controversial.xml,rulesets/java/naming.xml -f text'
    output_lines.extend(os.popen(cmd).readlines())
    for line in output_lines[1:]:#"5","","/Users/robert/Documents/src/python/StylisticFingerprinting/dir_for_marking/java-source_apache-log4j-2.9.1-src_log4j-web_src_test_java_org_apache_logging_log4j_web_WebLookupTest.java_2.java","3","3","publicMethodCommentRequirement Required","Comments","CommentRequired"
      if line.find('Error while parsing') != -1:
        print 'ERROR while runing PMD'
        print line
        continue
      file_path_in_result = line[:line.find(':')]
      file_path_in_result = marking_file_dict[os.path.basename(file_path_in_result)]
      if not file_mark.has_key(file_path_in_result):
        file_mark[file_path_in_result] = 0
      file_mark[file_path_in_result] = file_mark[file_path_in_result] + 1

    print '------checkstyle start-------'
    #checkstyle
    output_lines = []
    output_lines.extend(
      os.popen('java -jar ./analyzer/checkstyle-8.2-all.jar -c /google_checks.xml ' + dir_for_marking).readlines())
    output_lines.extend(
      os.popen('java -jar ./analyzer/checkstyle-8.2-all.jar -c /sun_checks.xml ' + dir_for_marking).readlines())
    for line in output_lines:#[ERROR] /Users/robert/Documents/src/python/StylisticFingerprinting/dir_for_marking/java-source_apache-log4j-2.9.1-src_log4j-web_src_test_java_org_apache_logging_log4j_web_WebLookupTest.java_2.java:0: File does not end with a newline. [NewlineAtEndOfFile]
      if line.startswith('['):
        file_path_in_result = line[line.find('] ')+2:line.find(':')]
        file_path_in_result = marking_file_dict[os.path.basename(file_path_in_result)]
        if not file_mark.has_key(file_path_in_result):
          #file_mark[file_path_in_result] = 0
          print 'ERROR------------%s does not have pmd marking' % file_path_in_result
          continue
        file_mark[file_path_in_result] = file_mark[file_path_in_result] + 1



    '''
    index = 0
    total_file_count = len(file_list)
    for file_path in file_list:
      file_mark[file_path] = self.markfile(file_path)
      index = index + 1
      print "%d / %d" %(index, total_file_count)

    '''

    #sort
    sorted_file_marks = sorted(file_mark.items(), key=lambda x: x[1], reverse=False)

    count = len(sorted_file_marks)
    top_file_marks = sorted_file_marks[0: count/4]
    bottom_file_marks = sorted_file_marks[count * 3/4:]
    #print top_file_marks
    #print bottom_file_marks

    top_file_dir = self.project + '_readable'
    self.createNewDir(top_file_dir)

    for (top_file_path, mark) in top_file_marks:
      shutil.copy(top_file_path, top_file_dir+ os.sep+ os.path.basename(top_file_path))

    bottom_file_dir = self.project + '_unreadable'
    self.createNewDir(bottom_file_dir)

    for (bottom_file_path, mark) in bottom_file_marks:
      shutil.copy(bottom_file_path, bottom_file_dir+ os.sep+ os.path.basename(bottom_file_path))



  def distincy(self, file_list):
    md5_dict = {}
    for i in range(len(file_list) - 1, -1, -1):
      file_path = file_list[i]
      md5file = open(file_path, 'rb')
      md5 = hashlib.md5(md5file.read()).hexdigest()
      if file_path == 'output/java-source_hibernate-orm_hibernate-jcache_src_test_java_org_hibernate_test_domain_EventManager.java_5.java':
        print file_path
        print md5

      if file_path == 'output/java-source_hibernate-orm_hibernate-jcache_src_test_java_org_hibernate_test_domain_EventManager.java_5.java':
        print file_path
        print md5
      md5file.close()
      if md5_dict.has_key(md5):
        print '%s has same md5 with %s with md5 %s' % (file_path, md5_dict[md5], md5)
        os.remove(file_path)
        file_list.remove(file_path)
      else:
        md5_dict[md5] = file_path



if (__name__ == '__main__'):

  orderMarking = OrderMarking(argv[1:])
  orderMarking.mark()


