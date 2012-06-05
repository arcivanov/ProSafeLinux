#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import binascii
from psl import psl

query_cmds={
  "ip":psl.CMD_IP,
  "name":psl.CMD_NAME,
  "model":psl.CMD_MODEL,
  "mac":psl.CMD_MAC,
  "gateway":psl.CMD_GATEWAY,
  "dhcp":psl.CMD_DHCP,
  "netmask":psl.CMD_NETMASK,
  "firmware_version":psl.CMD_FIRMWAREV,
  "traffic-statistic":psl.CMD_PORT_STAT,
  "speed-statistic":psl.CMD_SPEED_STAT,
  "vlan_engine":psl.CMD_VLAN_SUPP,
  "vlan_id":psl.CMD_VLAN_ID,
  "vlan802_id":psl.CMD_VLAN802_ID, 
  "vlan_pvid":psl.CMD_VLANPVID,
  "qos_id":psl.CMD_QUALITY_OF_SERVICE,
  "port_qos":psl.CMD_PORT_BASED_QOS,
  "bandwith_limit_in":psl.CMD_BANDWITH_INCOMMING_LIMIT,
  "bandwith_limit_out":psl.CMD_BANDWITH_OUTGOING_LIMIT,
  "broadcast_filter":psl.CMD_BROADCAST_FILTER,
  "port_mirror":psl.CMD_PORT_MIRROR,
  "block_unkown_multicast":psl.CMD_BLOCK_UNKOWN_MULTICAST,
  "igpm_spoofing":psl.CMD_IGPM_SPOOFING,
  "fixme_2":psl.CMD_FIMXE2,
  "fixme_5":psl.CMD_FIMXE5,
  "fixme_c":psl.CMD_FIXMEC,	
  "fixme_e":psl.CMD_FIXMEF,
  "fixme_f":psl.CMD_FIXMEF,
  "fixme_5400":psl.CMD_FIXME5400,
  "fixme_6000":psl.CMD_FIXME6000,
  "fixme_6800":psl.CMD_FIXME6800,
  "fixme_7400":psl.CMD_FIXME7400,
  }

query_cmds_rev={}

for key in query_cmds: 
    value=query_cmds[key]
    query_cmds_rev[value]=key
    
parser = argparse.ArgumentParser(description='Manage Netgear ProSafe Plus switches under linux.')
parser.add_argument("--interface",nargs=1,help="Interface",default=["eth0"])
parser.add_argument("--debug",help="Debug output",action='store_true')
subparsers = parser.add_subparsers(help='operation',dest="operation")

discover_parser=subparsers.add_parser('discover', help='Find all switches in all subnets')
passwd_parser=subparsers.add_parser("passwd",help="Change Password of a switch")
passwd_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
passwd_parser.add_argument("--old",nargs=1,help="old password",required=True)
passwd_parser.add_argument("--new",nargs=1,help="new password",required=True)

query_parser=subparsers.add_parser("query",help="Query values from the switch")
query_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
query_parser.add_argument("--passwd",nargs=1,help="password")
ch=query_cmds.keys()
ch.append("all")
query_parser.add_argument("query",nargs="+",help="What to query for",choices=ch);

reboot_parser=subparsers.add_parser("reboot",help="Reboot the switch")
reboot_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
reboot_parser.add_argument("--passwd",nargs=1,help="password",required=True)

reset_parser=subparsers.add_parser("factory-reset",help="Reset the switch")
reset_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
reset_parser.add_argument("--passwd",nargs=1,help="password",required=True)

set_parser=subparsers.add_parser("set",help="Set values to the switch")
set_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
set_parser.add_argument("--passwd",nargs=1,help="password",required=True)
set_parser.add_argument("--ip",nargs=1,help="Change IP")
set_parser.add_argument("--name",nargs=1,help="Change Name")
set_parser.add_argument("--gateway",nargs=1,help="Default Gateway")
set_parser.add_argument("--netmask",nargs=1,help="Netmask")
set_parser.add_argument("--dhcp",nargs=1,help="DHCP?",choices=["on","off"])
set_parser.add_argument("--reset-traffic-statistic",dest="resettraffictstatistic",action='store_true');

args = parser.parse_args()
interface=args.interface[0]
#print interface

g = psl(interface)

def discover():
  print "Searching for ProSafe Plus Switches ...\n"
  g.discover()

def reboot():
  print "Rebooting Switch...\n";
  cmd={g.CMD_PASSWORD:args.passwd[0],
       g.CMD_REBOOT:True}
  g.transmit(cmd,args.mac[0],g.transfunc)

def factoryReset():
  print "Reseting Switch to factory defaults...\n";
  cmd={g.CMD_PASSWORD:args.passwd[0],
       g.CMD_FACTORY_RESET:True}
  g.transmit(cmd,args.mac[0],g.transfunc)
if args.operation=="passwd":
  print "Changing Password...\n";
  g.passwd(args.mac[0],args.old[0],args.new[0],g.transfunc)

def set():
  print "Changing Values..\n"
  cmd={psl.CMD_PASSWORD:args.passwd[0]}
  
  if (args.ip):
      cmd[psl.CMD_IP]=args.ip[0]
      
  if (args.dhcp):
      cmd[psl.CMD_DHCP]=(args.dhcp[0]=="on")
      
  if (args.name):
      cmd[psl.CMD_NAME]=args.name[0]
      
  if (args.gateway):
      cmd[psl.CMD_GATEWAY]=args.gateway[0]
      
  if (args.netmask):
      cmd[psl.CMD_NETMASK]=args.netmask[0]
      
  if (args.resettraffictstatistic):
      cmd[psl.CMD_RESET_PORT_STAT]=True
      
  g.transmit(cmd,args.mac[0],g.transfunc)

def display_port_stat(data):
   print "%-30s%4s%15s%15s %s" %("Port Statistic:","Port","Rec.","Send","FIXME")
   for row in data:
      print "%-30s%4d%15d%15d %s" %("",row["port"],row["rec"],row["send"],row["rest"])

def display_speed_stat(data):
   print "%-30s%4s%15s%10s" %("Speed Statistic:","Port","Speed","FIXME")
   for row in data:
      speed=row["speed"]
      if speed==psl.SPEED_NONE:
	 speed="Not conn."
      if speed==psl.SPEED_10MH:
	 speed="10 Mbit/s H"
      if speed==psl.SPEED_10ML:
	 speed="10 Mbit/s L"
      if speed==psl.SPEED_100MH:
	 speed="100 Mbit/s H"
      if speed==psl.SPEED_100ML:
	 speed="100 Mbit/s L"
      if speed==psl.SPEED_1G:
	 speed="1 Gbit/s"
      print "%-30s%4d%15s%10s" %("",row["port"],speed,row["rest"])
  
queryFuncHash={
  psl.CMD_PORT_STAT:display_port_stat,
  psl.CMD_SPEED_STAT:display_speed_stat
  }
def query():
  print "Query Values..\n";
  if not(args.passwd == None):
     login={g.CMD_PASSWORD:args.passwd[0]}
     g.transmit(login,args.mac[0],g.transfunc)
  cmd=[]
  for q in args.query:
    if q == "all":
      for k in query_cmds.keys():
        if ((query_cmds[k]!=psl.CMD_VLAN_ID) and (query_cmds[k]!=psl.CMD_VLAN802_ID)):
  	  cmd.append(query_cmds[k])
    if q in query_cmds:
       cmd.append(query_cmds[q])
  g.query(cmd,args.mac[0],g.storefunc)
  for key in g.outdata.keys():
    if key in queryFuncHash:
      func=queryFuncHash[key]
      func(g.outdata[key])
    else:
     if key in query_cmds_rev:
       print "%-30s%s" %(query_cmds_rev[key].capitalize(),g.outdata[key])
     else:
       if args.debug:
         print "-%-29s%s" %(key,g.outdata[key])
       

cmdHash={
 "reboot":reboot,
 "discover":discover,
 "factory-reset":factoryReset,
 "set":set,
 "query":query,
}

if (args.debug):
  g.setDebugOutput()

if args.operation in cmdHash:
   cmdHash[args.operation]();
else:
   print "ERROR: operation not found!"
