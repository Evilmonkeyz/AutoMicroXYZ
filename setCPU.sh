#!/bin/bash
echo "Before change:"
echo $(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor)

echo "Setting CPU to performance mode"
echo $(echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor) &> /dev/null
echo $(echo performance > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor) &> /dev/null
echo $(echo performance > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor) &> /dev/null
echo $(echo performance > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor) &> /dev/null

echo "After change:"
echo $(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor)

