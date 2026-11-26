---
title: "pycharm 怎么更换python版本-CSDN博客"
source: "https://blog.csdn.net/weixin_33603316/article/details/140785876?ops_request_misc=elastic_search_misc&request_id=5f0030491c0eebb6d701486ff75bd069&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~ElasticSearch~search_v2-2-140785876-null-null.142^v102^pc_search_result_base7&utm_term=%E4%BD%BF%E7%94%A8pycharm%E6%9B%B4%E6%8D%A2python%E7%89%88%E6%9C%AC&spm=1018.2226.3001.4187"
author:
  - "[[高考数学呆哥]]"
published: 2024-07-30
created: 2026-10-10
description: "文章浏览阅读5.8k次，点赞6次，收藏18次。python相关学习资料：https://edu.51cto.com/video/4102.htmlhttps://edu.51cto.com/video/4645.htmlhttps://edu.51cto.com/video/3832.htmlPyCharm更换Python版本指南PyCharm是一个功能强大的..._pycharm切换python版本"
tags:
  - "clippings"
---
python相关学习资料：

[https://edu.51cto.com/video/4102.html](https://edu.51cto.com/video/4102.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=wzy_tl)

[https://edu.51cto.com/video/4645.html](https://edu.51cto.com/video/4645.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=wzy_tl)

[https://edu.51cto.com/video/3832.html](https://edu.51cto.com/video/3832.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=wzy_tl)

### PyCharm更换Python版本指南

PyCharm是一个功能强大的Python集成开发环境（IDE），它支持多种编程语言，包括Python。在使用PyCharm进行Python开发时，我们可能需要根据项目需求更换Python版本。本文将详细介绍如何在PyCharm中更换Python版本，并提供一个实际示例。

#### 1\. 准备工作

在开始更换Python版本之前，我们需要确保已经安装了多个版本的Python。可以通过Python官网下载并安装不同版本的Python。同时，确保每个Python版本的安装路径都已添加到系统环境变量中。

#### 2\. 打开PyCharm项目

打开PyCharm，选择需要更换Python版本的项目。如果尚未创建项目，可以点击"Create New Project"创建一个新项目。

#### 3\. 更换Python解释器

更换Python解释器是更换Python版本的关键步骤。以下是更换Python解释器的具体步骤：

##### 3.1 打开项目设置

在PyCharm的顶部菜单栏中，点击"File"，然后选择"Settings"（对于Mac用户，选择"PyCharm" > “Preferences”）。

##### 3.2 选择Python解释器

在"Settings"窗口中，选择"Project:你的项目名" > “Python Interpreter”。

##### 3.3 更换解释器

在"Python Interpreter"页面，可以看到当前项目使用的Python解释器。点击右侧的齿轮图标，选择"Add"。

在弹出的"Add Python Interpreter"窗口中，你可以选择"System Interpreter"、“Virtualenv Environment"或"Conda Environment"等选项。对于更换系统Python版本，我们选择"System Interpreter”。

在"System Interpreter"页面，点击"…“按钮，浏览并选择你想要使用的Python版本。选择完毕后，点击"OK”。

##### 3.4 应用更改

在"Add Python Interpreter"窗口中，点击"OK"，然后在"Python Interpreter"页面，点击"Apply"和"OK"应用更改。

#### 4\. 验证Python版本

更换Python版本后，我们需要验证项目是否使用了新的Python版本。在PyCharm的终端中输入以下命令：

```python
python --version
python运行
```
- 1.

如果输出的版本号与我们选择的版本一致，说明更换成功。

#### 5\. 示例

假设我们需要将项目从Python 3.6更换到Python 3.8。以下是更换过程的示例：

1. 打开PyCharm项目。
2. 打开"Settings" > “Project:你的项目名” > “Python Interpreter”。
3. 点击齿轮图标，选择"Add"。
4. 选择"System Interpreter"，点击"…"，选择Python 3.8的安装路径。
5. 点击"OK"，然后在"Python Interpreter"页面，点击"Apply"和"OK"。

更换完成后，在终端输入 `python --version` ，输出应为 `Python 3.8.x` 。

#### 6\. 结语

通过以上步骤，我们可以轻松地在PyCharm中更换Python版本。这为开发不同版本的Python项目提供了便利。同时，合理地管理Python版本有助于避免版本冲突和兼容性问题。

#### 状态图

以下是更换Python解释器的状态图：

```
stateDiagram-v2
    [*] --> 打开PyCharm项目: 打开项目
    打开PyCharm项目 --> 打开项目设置: 点击"File" > "Settings"
    打开项目设置 --> 选择Python解释器: 选择"Project:你的项目名" > "Python Interpreter"
    选择Python解释器 --> 更换解释器: 点击齿轮图标，选择"Add"
    更换解释器 --> 应用更改: 点击"Apply"和"OK"
    应用更改 --> 验证Python版本: 输入\`python --version\`
```

#### 类图

以下是Python解释器的类图：

<svg viewBox="0 0 619.5449829101562 248" style="max-width: 619.5449829101562px;" xmlns="http://www.w3.org/2000/svg" width="100%" id="render_119_3465697728-svg"><g><defs><marker orient="auto" markerHeight="240" markerWidth="190" refY="7" refX="0" id="classDiagram-aggregationStart"><path d="M 18,7 L9,13 L1,7 L9,1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="28" markerWidth="20" refY="7" refX="19" id="classDiagram-aggregationEnd"><path d="M 18,7 L9,13 L1,7 L9,1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="240" markerWidth="190" refY="7" refX="0" id="classDiagram-extensionStart"><path d="M 1,7 L18,13 V 1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="28" markerWidth="20" refY="7" refX="19" id="classDiagram-extensionEnd"><path d="M 1,1 V 13 L18,7 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="240" markerWidth="190" refY="7" refX="0" id="classDiagram-compositionStart"><path d="M 18,7 L9,13 L1,7 L9,1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="28" markerWidth="20" refY="7" refX="19" id="classDiagram-compositionEnd"><path d="M 18,7 L9,13 L1,7 L9,1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="240" markerWidth="190" refY="7" refX="0" id="classDiagram-dependencyStart"><path d="M 5,7 L9,13 L1,7 L9,1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="28" markerWidth="20" refY="7" refX="19" id="classDiagram-dependencyEnd"><path d="M 18,7 L9,13 L14,7 L9,1 Z"></path></marker></defs><defs><marker orient="auto" markerHeight="240" markerWidth="190" refY="7" refX="0" id="classDiagram-lollipopStart"><circle r="6" cy="7" cx="6" fill="white" stroke="black"></circle></marker></defs><g><g></g><g><path marker-start="url(#classDiagram-extensionStart)" style="fill:none" id="id1" d="M230.51234436035156,84.85905992285653L206.2229792277018,93.2158832690471C181.9336140950521,101.57270661523769,133.3548838297526,118.28635330761885,109.06551869710286,130.8098433204761C84.77615356445312,143.33333333333334,84.77615356445312,151.66666666666666,84.77615356445312,155.83333333333334L84.77615356445312,160" stroke="currentColor"></path><path marker-start="url(#classDiagram-extensionStart)" style="fill:none" id="id2" d="M305.67250061035156,110L305.67250061035156,114.16666666666667C305.67250061035156,118.33333333333333,305.67250061035156,126.66666666666667,305.67250061035156,135C305.67250061035156,143.33333333333334,305.67250061035156,151.66666666666666,305.67250061035156,155.83333333333334L305.67250061035156,160" stroke="currentColor"></path><path marker-start="url(#classDiagram-extensionStart)" style="fill:none" id="id3" d="M380.83265686035156,84.38784290828292L405.8053550720215,92.8232024235691C430.7780532836914,101.25856193885528,480.72344970703125,118.12928096942763,505.6961479187012,130.7313071513805C530.6688461303711,143.33333333333334,530.6688461303711,151.66666666666666,530.6688461303711,155.83333333333334L530.6688461303711,160" stroke="currentColor"></path></g><g><g><g transform="translate(0, 0)"><rect height="0" width="0" ry="0" rx="0"></rect></g></g><g><g transform="translate(0, 0)"><rect height="0" width="0" ry="0" rx="0"></rect></g></g><g><g transform="translate(0, 0)"><rect height="0" width="0" ry="0" rx="0"></rect></g></g></g><g><g transform="translate(305.67250061035156, 59)" id="classId-PythonInterpreter-0"><rect height="102" width="150.3203125" y="-51" x="-75.16015625" fill="none" stroke="currentColor"></rect><line y2="-20" y1="-20" x2="75.16015625" x1="-75.16015625" stroke="currentColor" stroke-opacity="0.2"></line><line y2="40" y1="40" x2="75.16015625" x1="-75.16015625" stroke="currentColor" stroke-opacity="0.2"></line><g><text transform="translate( -67.66015625, -43.5)" style="" fill="currentColor"><tspan x="0" dy="1em" fill="currentColor">PythonInterpreter </tspan></text><text transform="translate( -67.66015625, -8.5)" style=""><tspan x="0" dy="1em" fill="currentColor">+path: string </tspan></text><text transform="translate( -67.66015625, 13.5)" style=""><tspan x="0" dy="1em" fill="currentColor">+version: string </tspan></text></g></g><g transform="translate(84.77615356445312, 200)" id="classId-SystemInterpreter-1"><rect height="80" width="153.55230712890625" y="-40" x="-76.77615356445312" fill="none" stroke="currentColor"></rect><line y2="-9" y1="-9" x2="76.77615356445312" x1="-76.77615356445312" stroke="currentColor" stroke-opacity="0.2"></line><line y2="29" y1="29" x2="76.77615356445312" x1="-76.77615356445312" stroke="currentColor" stroke-opacity="0.2"></line><g><text transform="translate( -69.27615356445312, -32.5)" style="" fill="currentColor"><tspan x="0" dy="1em" fill="currentColor">SystemInterpreter </tspan></text><text transform="translate( -69.27615356445312, 2.5)" style=""><tspan x="0" dy="1em" fill="currentColor">+path: string </tspan></text></g></g><g transform="translate(305.67250061035156, 200)" id="classId-VirtualenvEnvironment-2"><rect height="80" width="188.24038696289062" y="-40" x="-94.12019348144531" fill="none" stroke="currentColor"></rect><line y2="-9" y1="-9" x2="94.12019348144531" x1="-94.12019348144531" stroke="currentColor" stroke-opacity="0.2"></line><line y2="29" y1="29" x2="94.12019348144531" x1="-94.12019348144531" stroke="currentColor" stroke-opacity="0.2"></line><g><text transform="translate( -86.62019348144531, -32.5)" style="" fill="currentColor"><tspan x="0" dy="1em" fill="currentColor">VirtualenvEnvironment </tspan></text><text transform="translate( -86.62019348144531, 2.5)" style=""><tspan x="0" dy="1em" fill="currentColor">+path: string </tspan></text></g></g><g transform="translate(530.6688461303711, 200)" id="classId-CondaEnvironment-3"><rect height="80" width="161.75230407714844" y="-40" x="-80.87615203857422" fill="none" stroke="currentColor"></rect><line y2="-9" y1="-9" x2="80.87615203857422" x1="-80.87615203857422" stroke="currentColor" stroke-opacity="0.2"></line><line y2="29" y1="29" x2="80.87615203857422" x1="-80.87615203857422" stroke="currentColor" stroke-opacity="0.2"></line><g><text transform="translate( -73.37615203857422, -32.5)" style="" fill="currentColor"><tspan x="0" dy="1em" fill="currentColor">CondaEnvironment </tspan></text><text transform="translate( -73.37615203857422, 2.5)" style=""><tspan x="0" dy="1em" fill="currentColor">+path: string</tspan></text></g></g></g></g></g></svg>

通过本文的介绍，希望能够帮助大家更好地使用PyCharm进行Python开发，灵活地更换Python版本。

原创作者: u\_16213315 转载于: https://blog.51cto.com/u\_16213315/11594169