---
title: "Pycharm | 一文掌握 Pycharm 中的 Git 操作 ( 超详细)_pycharm git"
source: "https://blog.csdn.net/gzhrock/article/details/131594757?ops_request_misc=elastic_search_misc&request_id=8e0f92aa91c62f571fbb51e1722dd4a1&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~ElasticSearch~search_v2-5-131594757-null-null.142^v102^pc_search_result_base7&utm_term=%E4%BD%BF%E7%94%A8pycharm%E5%9F%BA%E7%A1%80%E6%93%8D%E4%BD%9C&spm=1018.2226.3001.4187"
author:
  - "[[gzhrock]]"
published: 2023-07-07
created: 2026-10-10
description: "文章浏览阅读1.8w次，点赞67次，收藏237次。文章介绍了如何在Pycharm中使用Git进行拉取仓库、提交更改、处理冲突、推送更新等操作，包括添加文件到.gitignore，选择性提交代码块，以及解决合并冲突的步骤。"
tags:
  - "clippings"
---
#### 文章目录

---

## 原创声明

**本文为 HinGwenWoong 原创，如果这篇文章对您有帮助，欢迎转载，转载请阅读文末的【授权须知】，感谢您对 HinGwenWoong 文章的认可！**

---

## 前言

日常开发中, 经常会使用 `Git` 来管理项目, IDE 使用 `Pycharm`, 使用 `Pycharm` 中的 `Git` 操作可以大大节省直接使用命令敲代码的时间.  
下面教大家如何使用 `Pycharm` 里面的 `Git` 插件来进行图形化的操作.

**我是 HinGwenWoong，一个有着清晰目标不停奋斗的程序猿，热爱技术，喜欢分享，码字不易，如果帮到您，请帮我在屏幕下方点赞 👍 ，您的点赞可以让技术传播得更远更广，谢谢！**

---

## 一、拉取仓库

- 使用 `Git` 来进行 `clone` 操作克隆远程仓库:
- 打开 `VCS` - > `Git` -> `Clone`, 如果看不到 `Git` 可以找 `Version Control`.  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/7c8430c2c02a4ab56c53533390e43a22.png#pic_center)
- 填入仓库的 `git` 地址, 这里填入了 `pytorch` 的 git 地址:  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e45d010410c70d82ae657e93d57e8ac0.png#pic_center)
- 点击窗口右下方的 `[ clone ]` 之后会开始克隆操作, 可以看到 `Pycharm` 下方有进度条  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/d89578ce6cc9945753d466c89432b55a.png#pic_center)
- 拉取成功后,会弹出如下图所示的窗口,选择 `New Window` 或者 `This Window` 即可:  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/6a2cef71f4626c6bfe984ea2d4b9ac63.png#pic_center)

---

## 二、Git commit

- 修改好文件之后,需要 `Commit` 操作.

### Pycharm Commit 窗口

在状态栏 `View` -> `Tool Windows` -> `Commit` 打开 `Pycharm Commit` 窗口:  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c8f857962638b7a377cb2aaa24148614.png#pic_center)

### 添加到.gitignore

选中需要添加到 `../../.gitignore` 的文件, 鼠标右键, 选择 `Add to .gitignore` 即可  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/f34f38a58f8df297ea155cc146416a82.png#pic_center)

- 如果是没有文件则会自动创建  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/36b33f74c8a17a56e7bf3c0bc8e6e7f3.png#pic_center)

### Commit 整个文件的更改

选中需要进行 `Commit` 的文件,我这里的例子是将 已经 `git` 版本控制的文件`../../.gitignore` 文件 和 未经过 `git` 版本控制的 `main.py` 进行 `Commit`, 输入的 `Commit` 信息是 `First commit`, 点击下方的 `Commit 按钮` 即可进行 `Commit` 操作

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/d0f717811be1e0c22dc091a2e8fb3790.png#pic_center)

### Commit 文件中其中几个代码块

双击需要 `Commit` 的文件,选中需要提交的代码块,可以看到文件前面的 `[ ]` 变成 `[-]` 即表示选中部分, 完成后也是点击 `Commit` 按钮即可  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ce20abadd377f5cd63152839e81071c0.png#pic_center)

---

## 三、Git pull

- 拉取仓库, 状态栏 `VCS` -> `Git` -> `Pull`  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/a1bf021bdc036f813a9f41a0157073f1.png#pic_center)
- 弹出窗口,选取分支名之后点击 `[pull]` 即可:  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c9195b45aa30da998c40349209a29078.png#pic_center)
- 拉取成功会显示,证明拉取成功!  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/b068265690f3d3b7229873af01fc9df2.png#pic_center)

---

## 四、处理冲突

`Pull` 的过程中有时候会遇到需要解决冲突的时候, 如果有冲突,回弹出如下的弹窗, 下图显示的是冲突的文件 `README.md`,有三个选项:

- `Accept Yours`: 使用自己的文件代替远程的文件, **危险操作,直接覆盖!!!**
- `Accept Theirs`: 使用远程的文件替代本地的文件, **危险操作,直接覆盖!!!**
- `Merge...`: 自己手动选择, 推荐使用!  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/99d158fc1999fa271b16d17822203add.png#pic_center)
- 点击 `Mege` 之后会弹出一个界面:
	- 左边的框 `master`: 本地的文件
		- 中间的框 `Result`: 最终的合并文件
		- 右边的框 `origin/master`: 远程仓库的文件
		- 圆圈①: 可以看到一个 `x` 和一个 `>>` 如果是 `>>` 则是使用你本地的修改解决冲突, 如果 `x` 则放弃合并
		- 圆圈②: `<<` 选择远程仓库的文件来解决冲突, `x` 则放弃合并
		- 圆圈③: 魔术棒,两边都 `Accept`, 不丢弃其中一方  
		![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/b54ab73561f7a966692405e9dc420dfa.png#pic_center)
- 所有的冲突都解决之后,点击右下方的 `[Apply]` 即可.

---

## 五、Git push

在状态栏选择 `VCS` -> `Git` -> `Push` 进行 `Push` 操作  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c263669dd7f489a60c13f394d35e77c0.png#pic_center)

- 看到无误之后,按 `Push` 进行推送  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/58247513812e30184dd4fff08bb51598.png#pic_center)
- 看到这个成功标志即表明推送成功!  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/9a41c7e79bdc98ac2198306e051c3f05.png#pic_center)

---

## 六、查看 Git 记录

- 在状态栏选择 `View` -> `Tool Windows` -> `Git`:  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ba6883e2993dce6c119cab5ec74690c3.png#pic_center)
- 可以在 `Pycharm` 底部看到 `Git Log`:  
	![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/d2f707f3742a79401fe0704e4a7a3516.png#pic_center)

---

## 总结

以上就是 `Pycharm` 中 `Git` 的简单操作, 学会之后可以在工作中完成绝大部分的 `Git` 操作, 学到的小伙伴赶紧用起来.

**我是 HinGwenWoong，一个有着清晰目标不停奋斗的程序猿，热爱技术，喜欢分享，码字不易，如果帮到您，请帮我在屏幕下方点赞 👍 ，您的点赞可以让技术传播得更远更广，谢谢！**

---

## 授权须知

1. 原创文章在推送两天后才可进行转载
2. 转载文章，禁止声明原创
3. 不允许直接二次转载，转载请根据原文链接联系作者
4. 若无需改版，在文首清楚标注作者及来源/原文链接，并删除【原创声明】，即可直接转载。  
	但对于未注明转载来源/原文链接的文章，我将保留追述的权利。

> 作者：HinGwenWoong  
> 一个有着清晰目标不停奋斗的程序猿，热爱技术，喜欢分享，共同进步！  
> CSDN: HinGwenWoong  
> 原文链接： [Pycharm | 一文掌握 Pycharm 中的 Git 操作 ( 超详细)](https://blog.csdn.net/hxj0323/article/details/109208253)

5. 若需要修改文章的排版，请根据原文链接联系作者
6. 再次感谢您的认可，转载请遵守如上转载须知！

---