# zTT: Learning-based DVFS with Zero Thermal Throttling for Mobile Devices \[*MobiSys'21*\] - Artifact Evaluation

This repository contains all the artifacts necessary to run zTT on NVIDIA Jetson TX2 & Pixel 3a.

Each subdirectory contains the corresponding source codes and instructions to repeat the results of the paper.

Please follow the detailed instructions in each subdirectory.

## Requirements

### Jetson TX 2 
* Jetpack 3.3
* CUDA 9.0
* cuDNN 7.1.5
* OpenCV 3.4.2

### Pixel 3a
* Android 9 (Kernel version 4.9)

### Client & Agent server
* Ubuntu 18.04

## Contents

### Jetson TX2
* client.py   -   Client code
* agent.py    -   Agent server code
### Pixel 3a
* client.py  -  Client code
* agent.py  -  Agent server code
* power_on.py - Script to turn on Pixel 3a through Monsoon power monitor (Run on client)
* power_off.py - Script to turn off Pixel 3a through Monsoon power monitor (Run on client)
