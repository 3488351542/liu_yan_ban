# Git / GitHub 使用教学

> 作者注：每个英文单词都标注了中文翻译 + 拼音发音

---

## 为什么要用 Git / GitHub

```
你的代码在电脑里        →  别人看不到
用 Git 推到 GitHub     →  别人能下载你的代码
部署平台从 GitHub 拉取  →  别人能访问你的网站
```

---

## 整体流程

```
git init      → 告诉 Git 开始管这个文件夹
git remote    → 连上 GitHub 的仓库
git pull      → 把 GitHub 上的 .gitignore 下载下来
git add .     → 把所有文件装进箱子
git commit    → 封箱贴标签
git push      → 寄到 GitHub
```

---

## 每个命令详解

### 1. `cd d:/...`

```
cd = change directory = 改变目录（chen zhi 陈止）
```

**作用：** 进入你指定的文件夹。
**类比：** 双击打开一个文件夹。

---

### 2. `git init`

```
git = 版本控制工具（ji te 吉特）
init = initialize = 初始化（i ni she lai zi 伊尼舍来子）
```

**作用：** 在当前文件夹里创建一个仓库。相当于告诉 Git："这个文件夹我要开始管了"。
**做了之后发生了什么：** 文件夹里多了一个隐藏的 `.git` 文件夹（不要打开它）。

---

### 3. `git remote add origin https://...`

```
remote = 远程（rui mou te 瑞谋特）
add = 添加（ai de 埃得）
origin = 远程仓库的名字（ao rui jin 奥瑞金）
```

**作用：** 把你本地的 Git 和 GitHub 上的仓库连起来。
**类比：** 添加微信好友。`origin` 是你给这个好友起的昵称（业界习惯都叫 origin）。

> origin 是自定义的名字，可以改成任何词，比如 `git remote add 好朋友 https://...`
> 后面加 `.git` 是 GitHub 的规矩，所有仓库地址都以 `.git` 结尾

---

### 4. `git pull origin main`

```
pull = 拉取（pu er 普尔）
main = 主要分支（mei yin 梅因）
```

**作用：** 从 GitHub 下载最新的代码到本地。
**为什么要先拉：** 在 GitHub 上创建仓库时自动生成了 `.gitignore` 文件。这个文件告诉 Git "哪些文件不该上传"（比如虚拟环境 `venv/`、数据库 `database.db`）。必须先下载它，再上传代码，否则会把不该上传的文件也传上去。

> main 是 Git 的分支（branch）名，不是 app.py 里的代码。分支类似游戏的存档位，一个项目只有一个分支时默认叫 main。

---

### 5. `git add .`

```
add = 添加（ai de 埃得）
. = 点号 = 当前文件夹所有文件
```

**作用：** 把所有文件放进"暂存区"（告诉 Git "这些文件我要上传了"）。
**类比：** 收拾行李，把所有要带的东西放进箱子。
**注意：** `.gitignore` 里列出的文件不会被装进去。

---

### 6. `git commit -m "第一次提交：留言板"`

```
commit = 提交（ke mi te 科密特）
-m = message = 消息（mai sei zhi 麦塞至）
```

**作用：** 把暂存区里的文件打包成一个版本，并写上备注。
**类比：** 封箱，贴上标签。
**第一次使用前需要设置身份：**

```
git config --global user.email "你的邮箱@qq.com"
git config --global user.name "你的GitHub用户名"
```

`--global` = 全局设置（设一次，以后所有仓库都用这个身份）

---

### 7. `git push -u origin main`

```
push = 推送（pu shi 普石）
-u = upstream = 上游（a pu si te rui mu 阿普斯特瑞姆）
origin = 远程仓库
main = 主分支
```

**作用：** 把这个版本推到 GitHub 上。
**类比：** 把箱子寄到 GitHub。

---

## 常见问题

### Q: 初始身份设置报错？

```
Author identity unknown
```

按提示设置邮箱和用户名即可：

```
git config --global user.email "你的邮箱"
git config --global user.name "你的用户名"
```

### Q: 出现 `LF will be replaced by CRLF` 警告？

这是 Windows 和 Linux 换行符格式不同导致的，**不影响代码运行**。每个 Windows 用户都会看到。

如果想消除这个警告：
```
git config --global core.autocrlf true
```

---

## 补充概念：GitHub 仓库地址

```
仓库页面网址： https://github.com/用户名/仓库名
Git 地址：     https://github.com/用户名/仓库名.git
```

`.git` 告诉电脑"这是个 Git 仓库"，就像快递单上的"（收）"字。

---

## 以后日常用到的只有三个命令

```
git add .        # 把改过的文件都装进去
git commit -m "写了什么"  # 封箱写备注
git push         # 寄到 GitHub
```

第一次设置好后，以后每次改完代码就这三步。
