---
title: "使用pycharm操作git_pycharm git"
source: "https://blog.csdn.net/weixin_42575020/article/details/133931414?ops_request_misc=elastic_search_misc&request_id=8e0f92aa91c62f571fbb51e1722dd4a1&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~ElasticSearch~search_v2-2-133931414-null-null.142^v102^pc_search_result_base7&utm_term=%E4%BD%BF%E7%94%A8pycharm%E5%9F%BA%E7%A1%80%E6%93%8D%E4%BD%9C&spm=1018.2226.3001.4187"
author:
  - "[[Danker01]]"
published: 2023-10-19
created: 2026-10-10
description: "文章浏览阅读3.2k次，点赞8次，收藏25次。本文详细介绍了如何在PyCharm中配置Git、克隆代码、新增提交、版本比较、暂存、推送以及分支管理等操作，包括远程仓库的合并、回滚和分支相关操作，适合Git初学者参考。"
tags:
  - "clippings"
---
##### 说明：本来想自己写在pycharm上使用git的操作，看到有大佬已经总结的很是详细，遂不在做无用功，转发一下和大家共同学习，后面会把原文链接放上。

##### 1\. 大前提：先在 settings 里面把git配上

打开Pycharm, 点击File -> Settings -> Version Control --> Git ，在 Path to Git executable中选择本地的git.exe路径：

![](https://i-blog.csdnimg.cn/blog_migrate/5a39ef116a9385b136476a1edcad1df7.png)

##### 2\. 克隆代码

① 先从gitee上复制一下远端地址

![](https://i-blog.csdnimg.cn/blog_migrate/7143c96efad035354dc2d3f5e8513226.png)

② 再去克隆，点击Pycharm导航栏中的 VCS -> Get from Version Control ，粘贴地址，并指定要放的路径

![](https://i-blog.csdnimg.cn/blog_migrate/9672483bc524d5e3b81f9b0801176f0e.png)

![](https://i-blog.csdnimg.cn/blog_migrate/c4bff41d2fd91eddf6913a87d0501971.png)

![](https://i-blog.csdnimg.cn/blog_migrate/6e5bdddf4d76a36d48d1db308d214095.png)

##### 3 新增文件提交到版本库

![](https://i-blog.csdnimg.cn/blog_migrate/31a03a4ad6144f6c39910b8cdbafbec2.png)

![](https://i-blog.csdnimg.cn/blog_migrate/d54def73c0845570b344fc1311d64b64.png)

单独提交test1.py到本地版本库：就只选中test1.py，点击右键，选择Git -> Commit File

![](https://i-blog.csdnimg.cn/blog_migrate/bcde129222380e530ab0e9b33f5e7f2d.png)

输入提交的备注信息，选择Commit and Push

![](https://i-blog.csdnimg.cn/blog_migrate/049d4c3bc448d8febf8c397be111b8df.png)

![](https://i-blog.csdnimg.cn/blog_migrate/55ef3ab7362d2ed8bd76560f70fa88b9.png)

刚才其实点了取消，现在我新增一行代码，点击Push

![](https://i-blog.csdnimg.cn/blog_migrate/8f1819f2d4f8dfda2e6b0f1f8d1aa24a.png)

###### Compare with:

这里注意下，就是每次提交之前，点击Compare with，让本地文件跟版本库做一下比较再提。它不仅可以跟当前的比，还可以跟历史的比，甚至还可以跟某些分支比。

在我又加了第二行代码，做下比较再提交：

![](https://i-blog.csdnimg.cn/blog_migrate/f5d0356edf641c1249572f1946c3aad4.png)

可以看到变化的代码：

![](https://i-blog.csdnimg.cn/blog_migrate/69bff95103e6c061d24531811989c9a5.png)

##### 4\. git add. （把所有工作区内容提交到暂存区 Git -> Add ）

![](https://i-blog.csdnimg.cn/blog_migrate/58364c0155079c141458d7113927a3fd.png)

##### 5\. git commit -m '注释'（将所有变化提交到版本库 ）

![](https://i-blog.csdnimg.cn/blog_migrate/82e16407e0cfe02ac529e37d111aab83.png)

##### 6\. git pull （将远端的dev拉到本地的dev）

\# 将本地提交到远端之前，要先从远端拉到本地

![](https://i-blog.csdnimg.cn/blog_migrate/b2a54c4a277477e0dc46ab5945562e14.png)

![](https://i-blog.csdnimg.cn/blog_migrate/39d532c75e8d1156a3665ed230b7fc56.png)

同样的作用：直接点箭头，也可以操作从远端拉到本地，它拉下来就直接自动merge进来：

![](https://i-blog.csdnimg.cn/blog_migrate/b27034e48d948b93e55094dada20c734.png)

##### 7\. git push到远端（把本地的dev推到远端的dev ）

![](https://i-blog.csdnimg.cn/blog_migrate/80733ddc689601f34776d16cececc1b7.png)

查看远端dev已经添加进去：

![](https://i-blog.csdnimg.cn/blog_migrate/04678f1997397d7297c0fbfc174b4ca9.png)

双击注释可以看到代码：

![](https://i-blog.csdnimg.cn/blog_migrate/b5b5533fbf9d77a7b70d38ed135a8890.png)

同样点击箭头也可以完成push操作:

![](https://i-blog.csdnimg.cn/blog_migrate/aa2b4669b717fc0377e106ffe9186b42.png)

![](https://i-blog.csdnimg.cn/blog_migrate/6aaba1dfd8895fd14ea42462a745ebce.png)

查看远程dev仓库：

![](https://i-blog.csdnimg.cn/blog_migrate/09a9792298dac1dfee0a3146ca39c8d9.png)

##### 8\. 线上分支合并（远端的dev合并到远端的master分支上）

\>> 先切到dev分支上，再点击+Pull Request

![](https://i-blog.csdnimg.cn/blog_migrate/e51e8c4f26ca0bb2e89a9de6736e4e9f.png)

![](https://i-blog.csdnimg.cn/blog_migrate/bb4accd55e6147a0a99e46e425eb4d0f.png)

提交后管理员审查代码（代码review），通过之后点击合并，合并之后点击接收Pull Request

![](https://i-blog.csdnimg.cn/blog_migrate/3c5a82262a401feec91d654bb8eb578c.png)

合进来之后，可以看到master分支上就可以看到已经合进来了：

![](https://i-blog.csdnimg.cn/blog_migrate/48488f3f0161126d1ec44bb805100e5f.png)

##### 9\. 远程仓库回滚

切换到master分支，输入命令 git log 可以看到日志， 如果是要恢复到最初的状态，复制版本号

![](https://i-blog.csdnimg.cn/blog_migrate/f53268bbb8a06f0ee9d1d6b9b811ecdb.png)

按q退出后输入命令：

```
git reset --hard  e36c43c4657ed915cc685c9afcdc7daa7aea4198
```

现在本地master 就恢复到了最初状态（远端还没有恢复）

![](https://i-blog.csdnimg.cn/blog_migrate/ac7db3a66ef02c08665f4f549945d673.png)

输入命令提交到远端：

```
git push origin master -f   # f是强制提交到远端，这个一般不要用
```

![](https://i-blog.csdnimg.cn/blog_migrate/ba01e5aebe07db437ce3eeec78479ca9.png)

现在查看远端master, 已经恢复了：

![](https://i-blog.csdnimg.cn/blog_migrate/e719dd9972225d3ba4f2774269685bfa.png)

##### 10\. 添加或删除远程仓库

![](https://i-blog.csdnimg.cn/blog_migrate/a589eeb79794bedb9760cd6eb4955188.png)

![](https://i-blog.csdnimg.cn/blog_migrate/dcd506035c6a1430e49ac501372c9c42.png)

##### 11\. 分支相关操作

点击pycharm右下角

![](https://i-blog.csdnimg.cn/blog_migrate/2f89f5f827bcf13cdacf9f3ee32183db.png)

![](https://i-blog.csdnimg.cn/blog_migrate/2bfc3a04c92c50ae3423940f5309c125.png)

\>> 在本地建一个dev分支

![](https://i-blog.csdnimg.cn/blog_migrate/4f7c03e464f3e3cf1c042b297d6d8612.png)

![](https://i-blog.csdnimg.cn/blog_migrate/3a7ca1045244ae1465b4f1bbe4e05d12.png)

\>> 把本地dev分支 push到远端dev

![](https://i-blog.csdnimg.cn/blog_migrate/c5984d33c128a27bc723497529627229.png)

远端就有了dev：

![](https://i-blog.csdnimg.cn/blog_migrate/f3f377f46e0c149f016806330e3a712c.png)

\>> 删除本地dev

要先切到本地master，直接在本地的dev分支上不能删

![](https://i-blog.csdnimg.cn/blog_migrate/588cd6a86406450c9ff134af148f4ab9.png)

![](https://i-blog.csdnimg.cn/blog_migrate/4cfc29c4a3b1eeb897e9bafbdb84070f.png)

再delete dev

![](https://i-blog.csdnimg.cn/blog_migrate/85c7d8c0ca756d0aef6417e4a74906b5.png)

\>> 把远端dev拉到本地dev

![](https://i-blog.csdnimg.cn/blog_migrate/74ec06f6badd7e7f79ecc91bfbfcefc3.png)

本地就有了dev：

![](https://i-blog.csdnimg.cn/blog_migrate/d9128f1964f7ff77c03c63a3de123b1b.png)

![](https://i-blog.csdnimg.cn/blog_migrate/be530268b44b8a029db7dcfc40053549.png)