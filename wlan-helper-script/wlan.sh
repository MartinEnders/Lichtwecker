#!/bin/bash
# check if a wlan0 if exists
if echo `/sbin/ifconfig` | grep -q $1; then
#check if there is IP Address
  if echo `/sbin/ifconfig $1` | grep -q "inet "; then
    exit 0
  fi
  /sbin/modprobe -r 8192cu
fi
/sbin/modprobe 8192cu
exit 0
