---
author: \[\[高考数学呆哥\]\]
title: pycharm 怎么更换python版本-CSDN博客
---

python相关学习资料：

[https://edu.51cto.com/video/4102.html](https://edu.51cto.com/video/4102.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=wzy_tl)

[https://edu.51cto.com/video/4645.html](https://edu.51cto.com/video/4645.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=wzy_tl)

[https://edu.51cto.com/video/3832.html](https://edu.51cto.com/video/3832.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=wzy_tl)

### PyCharm更换Python版本指南

PyCharm是一个功能强大的Python集成开发环境（IDE），它支持多种编程语言，包括Python。在使用PyCharm进行Python开发时，我们可能需要根据项目需求更换Python版本。本文将详细介绍如何在PyCharm中更换Python版本，并提供一个实际示例。

#### 1. 准备工作

在开始更换Python版本之前，我们需要确保已经安装了多个版本的Python。可以通过Python官网下载并安装不同版本的Python。同时，确保每个Python版本的安装路径都已添加到系统环境变量中。

#### 2. 打开PyCharm项目

打开PyCharm，选择需要更换Python版本的项目。如果尚未创建项目，可以点击"Create New Project"创建一个新项目。

#### 3. 更换Python解释器

更换Python解释器是更换Python版本的关键步骤。以下是更换Python解释器的具体步骤：

##### 3.1 打开项目设置

在PyCharm的顶部菜单栏中，点击"File"，然后选择"Settings"（对于Mac用户，选择"PyCharm" \> "Preferences"）。

##### 3.2 选择Python解释器

在"Settings"窗口中，选择"Project:你的项目名" \> "Python Interpreter"。

##### 3.3 更换解释器

在"Python Interpreter"页面，可以看到当前项目使用的Python解释器。点击右侧的齿轮图标，选择"Add"。

在弹出的"Add Python Interpreter"窗口中，你可以选择"System Interpreter"、"Virtualenv Environment"或"Conda Environment"等选项。对于更换系统Python版本，我们选择"System Interpreter"。

在"System Interpreter"页面，点击"..."按钮，浏览并选择你想要使用的Python版本。选择完毕后，点击"OK"。

##### 3.4 应用更改

在"Add Python Interpreter"窗口中，点击"OK"，然后在"Python Interpreter"页面，点击"Apply"和"OK"应用更改。

#### 4. 验证Python版本

更换Python版本后，我们需要验证项目是否使用了新的Python版本。在PyCharm的终端中输入以下命令：

    python --version
    python运行

- 

如果输出的版本号与我们选择的版本一致，说明更换成功。

#### 5. 示例

假设我们需要将项目从Python 3.6更换到Python 3.8。以下是更换过程的示例：

1.  打开PyCharm项目。
2.  打开"Settings" \> "Project:你的项目名" \> "Python Interpreter"。
3.  点击齿轮图标，选择"Add"。
4.  选择"System Interpreter"，点击"..."，选择Python 3.8的安装路径。
5.  点击"OK"，然后在"Python Interpreter"页面，点击"Apply"和"OK"。

更换完成后，在终端输入 `python --version` ，输出应为 `Python 3.8.x` 。

#### 6. 结语

通过以上步骤，我们可以轻松地在PyCharm中更换Python版本。这为开发不同版本的Python项目提供了便利。同时，合理地管理Python版本有助于避免版本冲突和兼容性问题。

#### 状态图

以下是更换Python解释器的状态图：

    stateDiagram-v2
        [*] --> 打开PyCharm项目: 打开项目
        打开PyCharm项目 --> 打开项目设置: 点击"File" > "Settings"
        打开项目设置 --> 选择Python解释器: 选择"Project:你的项目名" > "Python Interpreter"
        选择Python解释器 --> 更换解释器: 点击齿轮图标，选择"Add"
        更换解释器 --> 应用更改: 点击"Apply"和"OK"
        应用更改 --> 验证Python版本: 输入\`python --version\`

#### 类图

以下是Python解释器的类图：

PythonInterpreter +path: string +version: string SystemInterpreter +path: string VirtualenvEnvironment +path: string CondaEnvironment +path: string

通过本文的介绍，希望能够帮助大家更好地使用PyCharm进行Python开发，灵活地更换Python版本。

原创作者: u_16213315 转载于: https://blog.51cto.com/u_16213315/11594169
