# Mesh Convergence Study

## Data Structure

<div align="center">

| Model | epsilon | edge length (l)-girdle| edge length (l)-legs | # of elements |
| --- | --- | --- | --- |--- |
|Res_1 | 0.00085 | 0.041 | 0.037 | 106K |
|Res_2 | 0.00075 | 0.034 | 0.024 | 128K |
|Res_3 | 0.00065 | 0.030 | 0.021 | 162K|
|Res_4 | 0.00055 | 0.022 | 0.018 | 193K|
|Res_5 | 0.0005 | 0.015 | 0.012 |336K|
|Res_6 | 0.0005 | 0.009 | 0.009 |718K|
|Res_7 | 0.0005 | 0.008 | 0.007 |1.2M|

</div>

<div align="center">

| Model | elapsed time | left | right | both | Relative percentage of change left|Relative percentage of change right|Relative percentage of change both|
| --- | --- | --- | --- |--- |--- |--- |--- |
|Res_1 | 0:01:52 | 0.227 | 0.217 | 0.222 |1.77|10.60|6.31|
|Res_2 | 0:02:11 | 0.240 | 0.228 | 0.234 |3.75|5.26|0.85|
|Res_3 | 0:02:34 | 0.229 | 0.255 | 0.242 |0.88|5.88|2.48|
|Res_4 | 0:02:54 | 0.249 | 0.255 | 0.252 |7.23|5.88|6.35|
|Res_5 | 0:04:44 | 0.226 | 0.235 | 0.230 |2.21|2.13|2.61|
|Res_6 | 0:13:37 | 0.239 | 0.234 | 0.236 |1.28|2.56|0|
|Res_7 | 0:40:21 | 0.231 | 0.240 | 0.236 |0|0|0|

</div>
