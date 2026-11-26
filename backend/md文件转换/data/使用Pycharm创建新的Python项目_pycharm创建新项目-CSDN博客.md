---
title: "使用Pycharm创建新的Python项目_pycharm创建新项目-CSDN博客"
source: "https://blog.csdn.net/tianyi0361/article/details/157502747?ops_request_misc=&request_id=&biz_id=102&utm_term=%E4%BD%BF%E7%94%A8pycharm%E5%88%9B%E5%BB%BA%E6%96%B0%E9%A1%B9%E7%9B%AE&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-5-157502747.142^v102^pc_search_result_base7&spm=1018.2226.3001.4187"
author:
  - "[[发奋的瓜牛]]"
published: 2026-01-29
created: 2026-10-10
description: "文章浏览阅读547次，点赞3次，收藏5次。摘要：本文介绍在PyCharm中创建Python项目的详细步骤。首先启动PyCharm并选择新建项目，选择Python项目类型和虚拟环境（建议新建以避免冲突）。接着命名项目并指定保存位置，PyCharm会自动生成包含venv文件夹和main.py的项目结构。venv包含虚拟环境相关文件（Scripts和lib），main.py是默认创建的示例文件（可取消勾选不生成）。整个过程强调使用虚拟环境管理项目依赖的重要性。_pycharm创建新项目"
tags:
  - "clippings"
---
1.打开PyCharm并选择创建新项目

首先，启动 PyCharm，你会看到欢迎界面。在这里，选择“Create New Project"或者"新建项目"。

![](https://i-blog.csdnimg.cn/direct/c88201c8a4934f88b63bf62e89e6b84f.png)

2.选择项目 类 型和环境

![](https://i-blog.csdnimg.cn/direct/613ee2da381b4f5e8ae2d3d60a974f6e.png)

①选择 Python 作为项目类型，

②选择Virtual Environment（虚拟环境）作为项目环境。此步骤的关键在于使用虚拟环境来管理项目依赖性。

③选择虚拟环境python关联版本

④创建

注：选择虚拟环境：也可以自定义环境进行创建，通常会选择（生成新的） 或 （选择现有）。 建议选择 （生成新的），这样做Python环境不会和其他项目有冲突

![](https://i-blog.csdnimg.cn/direct/7ac4d8fde69d4ca7a4a7cc73754781d6.png)

3.命名项目并选择项目位置

在项目名称框中输入你的项目名称（如PythonProject\_new），并选择一个合适的目录来保存该项目。

![](https://i-blog.csdnimg.cn/direct/89964176d26140eba2b25b18494c5957.png)

4.创建项目

点击创建后，PyCharm 会自动生成项目结构，包括 venv 和main.py。venv 是虚拟环境的 文件夹 ,

项目的主文件。

![](https://i-blog.csdnimg.cn/direct/eca509c1c2b245fd9433f05e78c0e141.png)

5.查看生成的项目结构

创建完成后，你可以在 PyCharm 的项目窗口中看到以下结构:

> MyProject
> 
> |
> 
> |— venv #虚拟环境文件夹
> 
> | |— Scripts # Windows 上的执行文件
> 
> | |— lib # 安装包文件
> 
> |
> 
> |— main.py # 项目的主 Python 文件

6.关于main.py文件

这个是项目创建的一个示例脚本，

![](https://i-blog.csdnimg.cn/direct/16a89508c3c747779a27c91377a1f5eb.png)

如果不需要可以在创建项目时不要勾选欢迎语来进行取消。

![](https://i-blog.csdnimg.cn/direct/5f90ae8a8afa4fc3b7d0217c2a76be3b.png)