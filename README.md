# zTT Implementation settings
## Development environment
* tegra-Ubuntu (kernel version 4.4.38) on Nvidia Jetson TX2
* Android 9.0 Pie (kernel version 4.9) on Google Pixel 3a (Rooted)

## Requirements
* Python 3.5
* Keras 2.2
* tensorflow 1.10.0


## Hyperparameter for Learning
| Hyperparameter  | Value |
| ------------- | ------------- |
| Learning rate  | 0.05  |
| Discount factor  | 0.99  |
| Batch size  | 64  |
| Replay memory size  | 500  |
| Input layer  | 6 units with RELU  |
| Hidden layer  | 6 units with RELU  |
| Outputput layer  | 6 units with RELU  |
