---
author: \[\[Danker01\]\]
title: 使用pycharm操作git_pycharm git
---

##### 说明：本来想自己写在pycharm上使用git的操作，看到有大佬已经总结的很是详细，遂不在做无用功，转发一下和大家共同学习，后面会把原文链接放上。

##### 1. 大前提：先在 settings 里面把git配上

打开Pycharm, 点击File -\> Settings -\> Version Control --\> Git ，在 Path to Git executable中选择本地的git.exe路径：

![使用pycharm操作git_pycharm git_rId11.png](../images/使用pycharm操作git_pycharm git_rId11.png){width="5.833333333333333in" height="4.095942694663167in"}

##### 2. 克隆代码

① 先从gitee上复制一下远端地址

![使用pycharm操作git_pycharm git_rId15.png](../images/使用pycharm操作git_pycharm git_rId15.png){width="5.833333333333333in" height="2.279643482064742in"}

② 再去克隆，点击Pycharm导航栏中的 VCS -\> Get from Version Control ，粘贴地址，并指定要放的路径

![使用pycharm操作git_pycharm git_rId18.png](../images/使用pycharm操作git_pycharm git_rId18.png){width="5.833333333333333in" height="2.9841961942257216in"}

![使用pycharm操作git_pycharm git_rId21.png](../images/使用pycharm操作git_pycharm git_rId21.png){width="5.833333333333333in" height="3.4162390638670166in"}

![使用pycharm操作git_pycharm git_rId24.png](../images/使用pycharm操作git_pycharm git_rId24.png){width="5.833333333333333in" height="0.8049573490813648in"}

##### 3 新增文件提交到版本库

![使用pycharm操作git_pycharm git_rId28.png](../images/使用pycharm操作git_pycharm git_rId28.png){width="5.833333333333333in" height="5.243444881889764in"}

![使用pycharm操作git_pycharm git_rId31.png](../images/使用pycharm操作git_pycharm git_rId31.png){width="5.833333333333333in" height="3.8013418635170604in"}

单独提交test1.py到本地版本库：就只选中test1.py，点击右键，选择Git -\> Commit File

![使用pycharm操作git_pycharm git_rId34.png](../images/使用pycharm操作git_pycharm git_rId34.png){width="5.833333333333333in" height="5.924990157480315in"}

输入提交的备注信息，选择Commit and Push

![使用pycharm操作git_pycharm git_rId37.png](../images/使用pycharm操作git_pycharm git_rId37.png){width="5.833333333333333in" height="4.848020559930009in"}

![使用pycharm操作git_pycharm git_rId40.png](../images/使用pycharm操作git_pycharm git_rId40.png){width="5.833333333333333in" height="3.840325896762905in"}

刚才其实点了取消，现在我新增一行代码，点击Push

![使用pycharm操作git_pycharm git_rId43.png](../images/使用pycharm操作git_pycharm git_rId43.png){width="5.833333333333333in" height="4.253569553805774in"}

###### Compare with:

这里注意下，就是每次提交之前，点击Compare with，让本地文件跟版本库做一下比较再提。它不仅可以跟当前的比，还可以跟历史的比，甚至还可以跟某些分支比。

在我又加了第二行代码，做下比较再提交：

![使用pycharm操作git_pycharm git_rId47.png](../images/使用pycharm操作git_pycharm git_rId47.png){width="5.833333333333333in" height="5.586586832895888in"}

可以看到变化的代码：

![使用pycharm操作git_pycharm git_rId50.png](../images/使用pycharm操作git_pycharm git_rId50.png){width="5.833333333333333in" height="1.8012543744531933in"}

##### 4. git add. （把所有工作区内容提交到暂存区 Git -\> Add ）

![使用pycharm操作git_pycharm git_rId54.png](../images/使用pycharm操作git_pycharm git_rId54.png){width="5.833333333333333in" height="5.241352799650044in"}

##### 5. git commit -m '注释'（将所有变化提交到版本库 ）

![使用pycharm操作git_pycharm git_rId58.png](../images/使用pycharm操作git_pycharm git_rId58.png){width="5.833333333333333in" height="5.632182852143482in"}

##### 6. git pull （将远端的dev拉到本地的dev）

\# 将本地提交到远端之前，要先从远端拉到本地

![使用pycharm操作git_pycharm git_rId62.png](../images/使用pycharm操作git_pycharm git_rId62.png){width="5.833333333333333in" height="1.978840769903762in"}

![使用pycharm操作git_pycharm git_rId65.png](../images/使用pycharm操作git_pycharm git_rId65.png){width="5.833333333333333in" height="4.257194881889764in"}

同样的作用：直接点箭头，也可以操作从远端拉到本地，它拉下来就直接自动merge进来：

![使用pycharm操作git_pycharm git_rId68.png](../images/使用pycharm操作git_pycharm git_rId68.png){width="5.833333333333333in" height="2.7844739720034997in"}

##### 7. git push到远端（把本地的dev推到远端的dev ）

![使用pycharm操作git_pycharm git_rId72.png](../images/使用pycharm操作git_pycharm git_rId72.png){width="5.833333333333333in" height="4.078632983377078in"}

查看远端dev已经添加进去：

![使用pycharm操作git_pycharm git_rId75.png](../images/使用pycharm操作git_pycharm git_rId75.png){width="5.833333333333333in" height="3.6728390201224848in"}

双击注释可以看到代码：

![使用pycharm操作git_pycharm git_rId78.png](../images/使用pycharm操作git_pycharm git_rId78.png){width="5.833333333333333in" height="3.736978346456693in"}

同样点击箭头也可以完成push操作:

![使用pycharm操作git_pycharm git_rId81.png](../images/使用pycharm操作git_pycharm git_rId81.png){width="5.833333333333333in" height="5.4365551181102365in"}

![使用pycharm操作git_pycharm git_rId84.png](../images/使用pycharm操作git_pycharm git_rId84.png){width="5.833333333333333in" height="4.137178477690289in"}

查看远程dev仓库：

![使用pycharm操作git_pycharm git_rId87.png](../images/使用pycharm操作git_pycharm git_rId87.png){width="5.833333333333333in" height="4.194482720909886in"}

##### 8. 线上分支合并（远端的dev合并到远端的master分支上）

\>\> 先切到dev分支上，再点击+Pull Request

![使用pycharm操作git_pycharm git_rId91.png](../images/使用pycharm操作git_pycharm git_rId91.png){width="5.833333333333333in" height="3.759705818022747in"}

![使用pycharm操作git_pycharm git_rId94.png](../images/使用pycharm操作git_pycharm git_rId94.png){width="5.833333333333333in" height="5.23440179352581in"}

提交后管理员审查代码（代码review），通过之后点击合并，合并之后点击接收Pull Request

![使用pycharm操作git_pycharm git_rId97.png](../images/使用pycharm操作git_pycharm git_rId97.png){width="5.833333333333333in" height="3.991778215223097in"}

合进来之后，可以看到master分支上就可以看到已经合进来了：

![使用pycharm操作git_pycharm git_rId100.png](../images/使用pycharm操作git_pycharm git_rId100.png){width="5.833333333333333in" height="3.3845997375328083in"}

##### 9. 远程仓库回滚

切换到master分支，输入命令 git log 可以看到日志， 如果是要恢复到最初的状态，复制版本号

![使用pycharm操作git_pycharm git_rId104.png](../images/使用pycharm操作git_pycharm git_rId104.png){width="5.833333333333333in" height="6.394584426946632in"}

按q退出后输入命令：

    git reset --hard  e36c43c4657ed915cc685c9afcdc7daa7aea4198

现在本地master 就恢复到了最初状态（远端还没有恢复）

![使用pycharm操作git_pycharm git_rId107.png](../images/使用pycharm操作git_pycharm git_rId107.png){width="5.833333333333333in" height="1.2546916010498688in"}

输入命令提交到远端：

    git push origin master -f   # f是强制提交到远端，这个一般不要用

![使用pycharm操作git_pycharm git_rId110.png](../images/使用pycharm操作git_pycharm git_rId110.png){width="5.833333333333333in" height="2.9446806649168855in"}

现在查看远端master, 已经恢复了：

![使用pycharm操作git_pycharm git_rId113.png](../images/使用pycharm操作git_pycharm git_rId113.png){width="5.833333333333333in" height="2.3469094488188977in"}

##### 10. 添加或删除远程仓库

![使用pycharm操作git_pycharm git_rId117.png](../images/使用pycharm操作git_pycharm git_rId117.png){width="5.833333333333333in" height="4.526233595800525in"}

![使用pycharm操作git_pycharm git_rId120.png](../images/使用pycharm操作git_pycharm git_rId120.png){width="5.833333333333333in" height="2.892856517935258in"}

##### 11. 分支相关操作

点击pycharm右下角

![使用pycharm操作git_pycharm git_rId124.png](../images/使用pycharm操作git_pycharm git_rId124.png){width="5.111111111111111in" height="3.1527777777777777in"}

![使用pycharm操作git_pycharm git_rId127.png](../images/使用pycharm操作git_pycharm git_rId127.png){width="3.361111111111111in" height="3.2777777777777777in"}

\>\> 在本地建一个dev分支

![使用pycharm操作git_pycharm git_rId130.png](../images/使用pycharm操作git_pycharm git_rId130.png){width="3.3333333333333335in" height="3.361111111111111in"}

![使用pycharm操作git_pycharm git_rId133.png](../images/使用pycharm操作git_pycharm git_rId133.png){width="5.541666666666667in" height="3.2777777777777777in"}

\>\> 把本地dev分支 push到远端dev

![使用pycharm操作git_pycharm git_rId136.png](../images/使用pycharm操作git_pycharm git_rId136.png){width="5.833333333333333in" height="3.815165135608049in"}

远端就有了dev：

![使用pycharm操作git_pycharm git_rId139.png](../images/使用pycharm操作git_pycharm git_rId139.png){width="3.3333333333333335in" height="4.097222222222222in"}

\>\> 删除本地dev

要先切到本地master，直接在本地的dev分支上不能删

![使用pycharm操作git_pycharm git_rId142.png](../images/使用pycharm操作git_pycharm git_rId142.png){width="5.833333333333333in" height="3.6592858705161855in"}

![使用pycharm操作git_pycharm git_rId145.png](../images/使用pycharm操作git_pycharm git_rId145.png){width="2.986111111111111in" height="2.638888888888889in"}

再delete dev

![使用pycharm操作git_pycharm git_rId148.png](../images/使用pycharm操作git_pycharm git_rId148.png){width="5.833333333333333in" height="3.7846576990376204in"}

\>\> 把远端dev拉到本地dev

![使用pycharm操作git_pycharm git_rId151.png](../images/使用pycharm操作git_pycharm git_rId151.png){width="5.833333333333333in" height="3.8247419072615925in"}

本地就有了dev：

![使用pycharm操作git_pycharm git_rId154.png](../images/使用pycharm操作git_pycharm git_rId154.png){width="3.3333333333333335in" height="4.097222222222222in"}

![使用pycharm操作git_pycharm git_rId157.png](../images/使用pycharm操作git_pycharm git_rId157.png){width="5.833333333333333in" height="3.7784087926509184in"}
