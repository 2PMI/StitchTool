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
 - None: 只进行拼接，不进行光场矫正
 - Estimate: 旧的光场估计方法，先进行高斯模糊后利用小图进行估计，可能需要手动调整`bias`以达到更好效果
 - NaiveEstimate: 新的光场估计方法，利用像素合成后进行估计，此时 `bias` 表示预处理进行高斯模糊的 `sigma` 值，对于大多数图像而言，`bias=1` 是一个比较好的选择；但对于那些噪声较大的图像，`bias` 可以设置为更大的值，如 `bias=2`，以达到更好的降噪效果；同理，对于那些噪声较小的图像，`bias` 可以设置为更小的值，如 `bias=0.5` 或 `bias=0`
 - BaSiC: 集成 BaSiC 算法，代码详见 https://github.com/peng-lab/BaSiCPy
 - Bagging: 合并 BaSiC 和 NaiveEstimate 的结果，以补偿边缘的亮暗偏差，`bias` 表示 NaiveEstimate 的占比，如`bias=1` 表示最终图像仅由 NaiveEstimate 结果构成
