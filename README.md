# 2photon_pipeline

## install
### install essential packages
```
pip install -r requirements.txt
```
### pre-commit install
For developers, you should install pre-commit to format your code
```
pip install pre-commit
pre-commit install
```
## Usage
### launch GUI
```
python main.py
```
### Settings
#### 1. Select Light Field
 - Estimate: 旧的光场估计方法，先进行高斯模糊后利用小图进行估计，可能需要手动调整`bias`以达到更好效果
 - Estimate2: 新的光场估计方法，利用像素合成后进行估计，保持`bias = 0`的默认值即可
