# zTT for Nvidia Jetson tx2
## Video rendering
* Requires OPEN CV2 with python 3.5
* It needs root-privilege to acces "sysfs" in the linux kernel.

## YOLOv3
* We refered YOLOv3 implementation [1] and modifed it to measure and record the FPS.
* After get original source code[1], change "src/demo.c" file with proposed "demo.c" in our YOLO directory. And then, please make the project.
* We also provide "test" file to excute YOLOv3, you need a "traffic.mp4"(File name can be changed) in the YOLO project directory.

## Chrome browser
* We provide chromedriver to measure Frame rate from Chrome browser. 
* We also provide "drivertest" file for a toy test.


# References
[1] https://pjreddie.com/darknet/yolo/
