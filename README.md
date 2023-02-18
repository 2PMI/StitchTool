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

 - NaiveEstimate(Recommended): 新的光场估计方法，利用像素合成后进行估计，加入了自适应降噪，但是对于部分花纹状噪声较多的图像，即使在降噪后上下两端还是会有一定的残留影响图像质量。因此，可以选择调整`bias`，通常设为`bias=0.6`即可，如果上下边缘还是有较明显的亮线，可以再适度调大，例如`bias=1`

 - BaSiC: 集成 BaSiC 算法，代码详见 https://github.com/peng-lab/BaSiCPy

 - Bagging: 合并 BaSiC 和 NaiveEstimate 的结果，以补偿边缘的亮暗偏差，`bias` 表示 NaiveEstimate 的占比，如`bias=1` 表示最终图像仅由 NaiveEstimate 结果构成
