# zTT for Nvidia Jetson tx2
<img src="jetson_testbed.jpg" width=300 height=300>

## Install dependencies

```bash
$ cd zTT/Jetson_tx2
$ pip install -r requirements.txt
```
Next, please download two video files using this link(Jetsontx2_video.zip) : https://drive.google.com/file/d/10v1qrFC2N_rlYStoa5qPE6UeEKaN-5FN/view?usp=sharing

Then, unzip the Jetsontx2_video.zip file under "ztt/Jetson_tx2"

## Instruction

### 1. Agent server device (Server, ubuntu)
Run *agent.py.*

```bash
$ python agent.py
```
#### Ok, the agent is watiing for connections ..
### 2. Client device (Jetson tx2)
* It needs root-privilege to acces "sysfs" in the linux kernel.
Let's run *client.py.*


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
* We also provide "video.mp4" file through Googledrive link. It should be under the JETSON project directory.
* Example
```bash
$ python3 client.py --IP_ADDR 192.168.1.7 --app rendering --file video.mp4 --exp_time 2000 --target_fps 30
```
#### YOLOv3
* We refered YOLOv3 implementation [1] and modifed it to measure and record the FPS.
* We provide executable files.
* We also provide "test" file to excute YOLOv3, you need a "traffic.mp4"(Packaged in the .zip file) under the JETSON project directory.
* Example
```bash
$ python3 client.py --IP_ADDR 192.168.1.7 --app YOLO --exp_time 2000 --target_fps 15
```
#### Chrome browser
* We provide chromedriver to measure Frame rate from Chrome browser. 
* Example
```bash
$ python3 client.py --IP_ADDR 192.168.1.7 --app aquarium --exp_time 2000 --target_fps 30
```
### 3. After connected
* You can see real-time graphs at the server-side.
* After training, we make sure that the zTT agent successfully meet target_fps and prevent overheating.

# References
[1] https://pjreddie.com/darknet/yolo/

