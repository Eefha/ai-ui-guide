---
title: "PyCharm从新建1个纯Python项目开始_pycharm新建项目-CSDN博客"
source: "https://blog.csdn.net/ha1314ha/article/details/162332514?ops_request_misc=&request_id=&biz_id=102&utm_term=%E4%BD%BF%E7%94%A8pycharm%E5%88%9B%E5%BB%BA%E6%96%B0%E9%A1%B9%E7%9B%AE&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-0-162332514.142^v102^pc_search_result_base7&spm=1018.2226.3001.4187"
author:
  - "[[ha1314ha]]"
published: 2026-06-27
created: 2026-10-10
description: "文章浏览阅读246次，点赞4次，收藏4次。本文介绍了在PyCharm 2026.1.1中新建Python项目的步骤：1）选择预建的空项目文件夹auto-test2026；2）演示了快速排序算法的实现与运行。总结了项目命名规范（建议小写字母+短横线），推荐新建项目时勾选自动创建Git仓库。特别强调了环境配置的两个选项（继承基础解释器包和全局可用）的潜在问题，指出两者都可能导致依赖冲突和环境污染，建议谨慎选择以保持项目独立性。_pycharm新建项目"
tags:
  - "clippings"
---
## 一、环境信息

已安装：PyCharm 2026.1.1、Python 3.11、git

## 二、开始新建

### 1、打开PyCharm 2026.1.1

![](https://i-blog.csdnimg.cn/direct/5096806d00564f069a46b3b12e9a949b.png)

### 2、新建项目

新建项目

![](https://i-blog.csdnimg.cn/direct/8d5ceba4e3d2411fb49ae465b3406200.png)

【纯Python】下，【位置】处，选本机提前新建好的项目文件夹auto-test2026。

如图，提前建好的项目空白文件夹。

![](https://i-blog.csdnimg.cn/direct/1654abe384234ae9badcdca78b862ddb.png)

![](https://i-blog.csdnimg.cn/direct/8170c479a4f844b4a153c15c5b5a2095.png)

创建

## 三、运行

以一个简单的快速排序为例：

```python
def quik_sort(arr):

    # 递归终止条件：数组长度小于等于1时，本身就是有序的，直接返回

    if len(arr)<=1:

        return arr

    # 选取数组中间元素作为基准值

    center = arr[len(arr)//2]

    left = [x for x in arr if x<center]

    mid = [x for x in arr if x==center]

    right = [x for x in arr if x>center]

    return quik_sort(left) + mid + quik_sort(right)

 

if __name__ == '__main__':

    testdata = [89,90,1,0,-2,-1.99,1000]

    result = quik_sort(testdata)

    print(result)
python运行
```

点击main函数处的绿色运行按钮，运行效果：

![](https://i-blog.csdnimg.cn/direct/4c798103760940b38221c3b433cbedfc.png)

## 四、小结

1、项目文件夹命名

允许： **小写字母、数字、短横线 -、下划线\_，** 不要过长，尽量控制在 20 字符以内。

✅ 稳妥方案：以小写字母开头，中间使用短横线。

2、新建项目时，自动创建git仓库

手动勾选，【创建Git仓库】。

新建的项目，自动 初始化 git，自动生成.git 隐藏文件夹，不用手动执行 `git init` 。

3、2个选项：【从基础 解释器 继承软件包】、 【可用于所有项目】

| 选项 | 核心缺点 |
| --- | --- |
| 从基础解释器继承软件包 | 1\. 依赖版本不可控，无法针对单个项目指定专属版本，不同项目版本要求不同时会冲突  2\. 环境隔离性差，全局包升级后所有继承项目都会受影响  3\. 直接导出 requirements.txt 会混入大量全局多余包，部署风险高  4\. 项目依赖与全局环境强绑定，换机器无法直接复现 |
| 可用于所有项目（全局开启继承） | 1\. 全局配置不可逆，开启后所有新项目默认继承，无法针对单个项目快速切换纯净模式  2\. 团队协作风险高，强制继承个人本地环境，容易出现本地能跑，线上 / 别人电脑跑不了的问题  3\. 无法适配生产部署、版本管控严格的项目，必须手动关闭  4\. 全局环境的垃圾包、测试包会被所有新项目继承，导致项目环境冗余 |

✅ 稳妥方案：本实践里，都不勾。