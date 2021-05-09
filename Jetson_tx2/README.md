# zTT for Nvidia Jetson tx2

## Install dependencies

```bash
$ cd zTT/Jetson_tx2
$ pip install -r requirements.txt
```
Download other files using this link : https://drive.google.com/file/d/1A5q0qeHseQw1g-3kalZUm5Bh4uk_f0rW/view?usp=sharing

## Instruction

### 1. Agent server device
Run *agent.py.*

```bash
$ python agent.py
```

### 2. Client device
Run *client.py.*

#### Usage of client.py
```
usage: client.py [-h] [--IP_ADDR IP_ADDR] [--app APP] [--file FILE]
                 [--exp_time EXP_TIME] [--target_fps TARGET_FPS]

optional arguments:
  -h, --help            show this help message and exit
  --IP_ADDR IP_ADDR     [server ip address (e.g. 192.168.1.1]
  --app APP             Select an app to test: [rendering, YOLO, aquarium]
  --file FILE           Path of a video file for rendering
  --exp_time EXP_TIME   Set time for experiment
  --target_fps TARGET_FPS
                        Set target_fps [e.g., 30]
```

#### Video rendering
* Requires OPEN CV2 with python 3.5
* It needs root-privilege to acces "sysfs" in the linux kernel.

#### YOLOv3
* We refered YOLOv3 implementation [1] and modifed it to measure and record the FPS.
* After get original source code[1], change "src/demo.c" file with proposed "demo.c" in our YOLO directory. And then, please make the project.
* We also provide "test" file to excute YOLOv3, you need a "traffic.mp4"(File name can be changed) in the YOLO project directory.

#### Chrome browser
* We provide chromedriver to measure Frame rate from Chrome browser. 
* We also provide "drivertest" file for a toy test.


# References
[1] https://pjreddie.com/darknet/yolo/

