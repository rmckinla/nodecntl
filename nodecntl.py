#!/usr/bin/python

##############################################################################    
# Node Control v1.0
#  This program will send a command via ssh to ip address stored in
#  a list file.
#
#  Assume following:
#    1. ssh is setup and running correctly
#    2. The nodes have their ssh keys setup and working
#    3. The head has all the nodes with proper keys
#    4. fping is installed (mod code to go back to ping)
#
#  todo : 
#    1. Add node update it's ip address. This will allow changing DHCP
#    2. Fix node user. Move off root access
#    x. change ssh command to StrictHostKeyChecking=no
#
##############################################################################    

import os, sys
import time, fileinput, tempfile

from time import ctime
from os import path
from os import walk
import threading
import subprocess

ssh_opt     = "-o StrictHostKeyChecking=no -o ConnectTimeout=5 -o ConnectionAttempts=1"
fn_nodelist = "nodelist"
a_nodebase  = []                # contains information from nodelist file
a_nodeinfo  = []                # contains node index and ipaddress
cnt_nodes   = 0                 # number of nodes loaded into array

##############################################################################    
# Populate base file information in to an array
##############################################################################    
def popbaselist():
  global a_nodebase
  filecheck = fn_nodelist
  if(os.path.isfile(filecheck) == False):
    print "Node list does not exist"
    return(1)
  fp_nodelist = open(fn_nodelist, 'r')
  a_nodebase = fp_nodelist.readlines()    
  fp_nodelist.close()
  return(0)

##############################################################################    
# Populate array with node information
##############################################################################    
def popnodeinfo():
  global a_nodebase, a_nodeinfo, cnt_nodes
  a_work  = []
  a_work2 = []
  for wrk in a_nodebase:
    a_work = wrk.split(",")
    a_work[2] = a_work[2].rstrip("\n")
    a_work[2] = a_work[2].rstrip("\r")
    if a_work[0] == "node":
      wrk1 = [a_work[1] , a_work[2]]
      a_nodeinfo.append(wrk1)
      cnt_nodes = cnt_nodes + 1
    a_nodeinfo.sort()
  return(0)

##############################################################################    
# Check to see if an ip address responds to a ping command
##############################################################################    
def checkalive(ip_addr):
  cmd_ping = "fping -t500 -r1 " + ip_addr
  proc = subprocess.Popen([cmd_ping], stdout=subprocess.PIPE, shell=True)
  (out, err) = proc.communicate()
  if "nreach" in out:
    return(1)
  else:
    return(0) 

##############################################################################    
# Check node alive
# Send a command to node
##############################################################################    
def sendnodecmd(cmd_type, cmd_send):
  global a_nodeinfo, cnt_nodes
  for i in range (0, cnt_nodes):
    if checkalive(a_nodeinfo[i][1]) == 0:
      print "-------------------------------------------------------------"
      print "   Node ID: " +  a_nodeinfo[i][0] + " | Command: " + cmd_send 
      print "-------------------------------------------------------------"
      cmd_ssh = "ssh " + ssh_opt + " root@" + a_nodeinfo[i][1] + " \"" + cmd_send
      if cmd_type == "p":
        cmd_ssh = cmd_ssh + "\" &"
      else:
        cmd_ssh = cmd_ssh + "\""
      os.system(cmd_ssh)
    else:
      print "-------------------------------------------------------------"
      print "   Node ID: " + a_nodeinfo[i][0] + " | Not responding, skipping"
      print "-------------------------------------------------------------"
  return(0)

def listnodeip():
  print "Node IP listing"
  print "Working Nodes: " + str(cnt_nodes)
  index = 0
  for wrk in a_nodeinfo:
    print "  Node ID: " + str(a_nodeinfo[index][0]) + "  IP : " + str(a_nodeinfo[index][1])
    index = index + 1
  return(0)  

##############################################################################    
# Check node alive
# Copy file to a node
##############################################################################    
def nodecpy(fn_src, fn_dest):
  global a_nodeinfo, cnt_nodes
  for i in range (0, cnt_nodes):
    if checkalive(a_nodeinfo[i][1]) == 0:
      print "-------------------------------------------------------------"
      print "   Node ID: " +  a_nodeinfo[i][0] + " | Src: " + fn_src + "  Dest: " + fn_dest
      print "-------------------------------------------------------------"
      cmd_scp = "scp -p " + fn_src + " root@" + a_nodeinfo[i][1] + ":" + fn_dest #" root@$HOSTNAME:$2
      os.system(cmd_scp)
    else:
      print "-------------------------------------------------------------"
      print "   Node ID: " + a_nodeinfo[i][0] + " | Not responding, skipping"
      print "-------------------------------------------------------------"
  return(0)
  
##############################################################################    
# Main section
##############################################################################    
def main():
  print "----------------------------------------------------------"
  print "  Node Control v1.0"
  print "                                  -R McK 2015-02-19"
  print "----------------------------------------------------------"
  popbaselist()
  popnodeinfo()

  try:
    cmd_type = str(sys.argv[1])
    if cmd_type == "-c" or cmd_type == "-C":
      try:
        cmd_fn1 = str(sys.argv[2])
        cmd_fn2 = str(sys.argv[3])
        nodecpy(cmd_fn1, cmd_fn2)
      except:
        pass
    elif cmd_type == "-l" or cmd_type == "-L":
      listnodeip()
    elif cmd_type == "-s" or cmd_type == "-S":
      try:
        cmd_send = str(sys.argv[2])
        sendnodecmd("s", cmd_send)
      except:
        pass

    elif cmd_type == "-p" or cmd_type == "-P":
      try:
        cmd_send = str(sys.argv[2])
        sendnodecmd("p", cmd_send)
      except:
        pass
    
  except:
    pass
    print "Usage : nodecntl.py <opt>"
    print "  <opt>"
    print "     -p <cmd> : Send command parallel to nodes"
    print "     -s <cmd> : Send command sequentially to nodes"
    print "     -l : list nodes information"
    print "     -c <src> <dest> : Copy file to nodes"
    print "  Encapsulate <cmd> in \" \" for complex commands"
    


    
  print "\n\n"
  print "----------------------------------------------------------"
  print "All node Commands submitted"
  sys.exit()

##############################################################################    
# Startup Main section
##############################################################################    
if __name__ == '__main__':
  main()

  

