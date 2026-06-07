# Git 命令大全

> 按官方帮助文档分类整理
> Git = 版本控制工具（ji te 吉特）
> 用法：`git 命令` 或 `git --help` 查看全部

### 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| origin | ao rui jin 奥瑞金 | 远程仓库名 |
| master | ma si te 马斯特 | 主分支名 |
| main | mei yin 梅因 | 主分支名 |
| HEAD | hai de 海的 | 当前最新提交 |

---

## 一、创建仓库（start a working area）

### 1.1 clone — 克隆项目

```bash
git clone https://github.com/用户名/仓库名.git
```

| 部分 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `clone` | ✅ **固定** | 克隆 | ke lou en 科漏恩 |
| `https://...` | ❌ **自定义** | 仓库地址 | |

**作用：** 把 GitHub 上的项目下载到本地

---

### 1.2 init — 初始化仓库

```bash
git init
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `init` | initialize = 初始化 | i ni she lai zi 伊尼舍来子 |

**作用：** 让当前文件夹受 Git 管理，生成 `.git` 隐藏文件夹

---

### 1.3 config — 配置身份

```bash
git config --global user.name "你的名字"    # 设置用户名
git config --global user.email "你的邮箱"   # 设置邮箱
git config --list                          # 查看所有配置
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `config` | 配置 | ken fi ge 肯菲格 |
| `--global` | 全局 | glou bo 格娄伯 |
| `user.name` | 用户名 | yo ze nei mu 优则内姆 |
| `user.email` | 用户邮箱 | yo ze yi mei ou 优则伊梅欧 |
| `--list` | 列出 | li si te 利斯特 |

**作用：** 第一次用 Git 必须先设置身份

---

## 二、修改文件（work on the current change）

### 2.1 add — 添加文件到暂存区

```bash
git add 文件名
git add .            # 添加所有文件
git add app.py       # 只添加一个文件
git add templates/   # 添加一个文件夹
```

| 部分 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `add` | ✅ **固定** | 添加 | ai de 埃得 |
| `.` | ✅ **固定** | 点号=当前目录所有 | |
| `文件名` | ❌ **自定义** | 你要添加的文件 | |

---

### 2.2 mv — 重命名或移动文件

```bash
git mv 旧文件名 新文件名    # 重命名
git mv 文件 目标文件夹/     # 移动文件
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `mv` | move = 移动 | mu fu 姆夫 |

**作用：** 重命名或移动文件，同时告诉 Git 这个变化

---

### 2.3 restore — 恢复文件

```bash
git restore 文件名                  # 撤销修改（还没 add 的）
git restore --staged 文件名          # 取消暂存（已 add 的）
git restore --source=版本id 文件名   # 恢复到指定版本
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `restore` | 恢复 | rui si tao 瑞斯涛 |
| `--staged` | 暂存区 | si tei zhi de 斯忒知的 |
| `--source` | 来源 | sao si 骚斯 |

---

### 2.4 stash — 暂存修改

```bash
git stash                  # 暂存当前修改（工作区变干净）
git stash pop              # 恢复最近一次暂存
git stash list             # 查看所有暂存
git stash drop             # 删除最近一次暂存
git stash apply 暂存id     # 恢复指定暂存（不删除）
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `stash` | 暂存 | si ta shi 斯它石 |
| `pop` | 取出 | pao pu 抛普 |
| `list` | 列表 | li si te 利斯特 |
| `drop` | 丢弃 | dao pu 到普 |
| `apply` | 应用 | a pu lai 阿普来 |

**作用：** 临时保存修改，切分支做其他事，回来再恢复

---

### 2.5 rm — 删除文件

```bash
git rm 文件名              # 删除文件（本地 + Git）
git rm --cached 文件名     # 停止跟踪（不删本地文件）
git rm -r 文件夹名          # 删除整个文件夹
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `rm` | remove = 移除 | rui mu fu 瑞姆夫 |
| `--cached` | 缓存（不删本地） | kai chi de 开驰得 |
| `-r` | recursive = 递归 | rui ke si 瑞克斯 |

---

## 三、查看状态和历史（examine the history and state）

### 3.1 status — 查看状态

```bash
git status
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `status` | 状态 | si tai te si 斯太特斯 |

**作用：** 看哪些文件改了、哪些还没 add、哪些还没 commit

---

### 3.2 diff — 查看详细改动

```bash
git diff                   # 看未 add 的改动
git diff --cached          # 看已 add 未 commit 的
git diff 版本1 版本2       # 比较两个版本的差异
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `diff` | 差异 | di fu 迪夫 |

---

### 3.3 log — 查看提交历史

```bash
git log                  # 完整历史
git log --oneline        # 简洁版（一行一个）
git log --oneline -5     # 只看最近5条
git log --oneline --graph  # 图形化显示分支
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `log` | 日志 | lao ge 涝格 |
| `--oneline` | 一行显示 | wan e lai en 完额来恩 |
| `--graph` | 图形 | gu ra fu 古拉夫 |

---

### 3.4 show — 查看某个提交的详情

```bash
git show                 # 查看最新提交
git show 版本id           # 查看指定提交
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `show` | 显示 | shou 收 |

---

### 3.5 grep — 在代码中搜索

```bash
git grep "关键词"         # 在当前代码中搜索
git grep -n "关键词"      # 显示行号
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `grep` | 搜索 | ge rui pu 格瑞普 |
| `-n` | 行号 | |

---

### 3.6 bisect — 二分查找 bug

```bash
git bisect start             # 开始查找
git bisect bad               # 当前版本有 bug
git bisect good 版本id       # 这个版本没有 bug
git bisect reset             # 结束查找
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `bisect` | 二分查找 | bai sai ke te 百赛科特 |
| `bad` | 坏 | |
| `good` | 好 | |

---

### 3.7 ls-files — 查看跟踪的文件

```bash
git ls-files                 # 查看所有被 Git 跟踪的文件
git ls-files 文件名           # 查看某个文件是否被跟踪
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `ls-files` | list files = 列出文件 | ai ai si 埃埃斯 / fai er si 法伊尔斯 |

**作用：** 看哪些文件被 Git 管着，`.gitignore` 是否生效。

```bash
# 常用场景
git ls-files database.db      # 查 database.db 是否被跟踪
                                # 有输出 = 被跟踪了
                                # 没输出 = 没被跟踪（或被忽略了）
```

---

## 四、分支和提交（grow, mark and tweak your common history）

### 4.1 branch — 分支管理

```bash
git branch                   # 查看所有分支
git branch 分支名             # 创建分支
git branch -d 分支名          # 删除分支
git branch -D 分支名          # 强制删除分支
git branch -m 旧名 新名       # 重命名分支
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `branch` | 分支 | bu ran chi 布染迟 |
| `-d` | delete = 删除 | di li te 迪利特 |
| `-D` | 强制删除 | qiang zhi shan chu 强制删除 |
| `-m` | move = 改名 | mu fu 姆夫 |

---

### 4.2 commit — 提交修改

```bash
git commit -m "说明文字"      # 提交并写备注
git commit -a -m "说明"      # 跳过 add 直接提交（只对已跟踪文件有效）
git commit --amend -m "新说明"  # 修改上一次提交的备注
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `commit` | 提交 | ke mi te 科密特 |
| `-m` | message=消息 | mai sei zhi 麦塞至 |
| `-a` | all=所有 | ao er 奥尔 |
| `--amend` | 修改 | e men de 埃门得 |

---

### 4.3 merge — 合并分支

```bash
git merge 分支名              # 把指定分支合并到当前分支
git merge --no-ff 分支名     # 禁用快进合并
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `merge` | 合并 | me zhi 么之 |
| `--no-ff` | no fast forward = 不快进 | bu kuai jin 不快进 |

**merge 怎么工作的：**

合并前：
```
main:   提交A ← 提交B ← 提交C
                                ↑
                              main

新功能: 提交A ← 提交B ← 提交C ← 提交D ← 提交E
                                                ↑
                                             新功能
```

执行 `git switch main` + `git merge 新功能` 后：
```
main:   提交A ← 提交B ← 提交C ← 提交D ← 提交E
                                                ↑
                                          main + 新功能（都有）
```

**合并后两个分支都有同样的代码，都不丢失。**

---

### 4.3.1 Fast-Forward（快进合并）vs 普通合并

```bash
git merge 新功能        # 默认：如果可能，使用快进
git merge --no-ff 新功能  # 禁用快进，总是创建一个新的 merge commit
```

**Fast-Forward（快进）** —— main 没有新提交，直接把指针往前移：
```
合并前：  main → 提交A ← 提交B
                    新功能 → 提交C ← 提交D

合并后：  main + 新功能 → 提交A ← 提交B ← 提交C ← 提交D
```
没有分叉，直接往前推。

**--no-ff（不快进）** —— 总是建一个新 commit：
```
合并前：  main → 提交A
                    新功能 → 提交B ← 提交C

合并后：  main → 提交A ←─ 提交D（merge commit）
                         ↙         ↗
              新功能 → 提交B ←── 提交C
```
保留分支历史，能看出来"这里曾经有个分支"。

---

### 4.3.2 合并后查看结果

```bash
# 图形化看合并历史
git log --oneline --graph

# 看所有分支的合并情况
git log --oneline --graph --all
```

---

### 4.3.3 合并冲突

如果两个分支改了同一个文件同一行，合并时会报冲突：

```bash
git merge 新功能
# Auto-merging app.py
# CONFLICT (content): Merge conflict in app.py
# Automatic merge failed; fix conflicts and then commit the result.
```

解决冲突三步：

```bash
# 1. 打开冲突文件，手动选择保留哪个版本
#    <<<<<<< HEAD   ← 当前分支的内容
#    =======       ← 分隔线
#    >>>>>>> 新功能  ← 被合并分支的内容

# 2. 修改完后保存，标记为已解决
git add app.py

# 3. 提交合并
git commit
```

---

### 4.4 rebase — 变基（整理提交历史）

```bash
git rebase 分支名             # 把当前分支变基到目标分支
git rebase -i HEAD~3         # 交互式重写最近3条提交
git rebase --abort           # 取消变基
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `rebase` | 变基 | rui bei si 瑞贝斯 |
| `-i` | interactive=交互 | yin te ai ke ti fu 因特艾克替夫 |
| `--abort` | 放弃 | a bao te 阿包特 |

---

### 4.5 reset — 回滚

```bash
git reset --soft HEAD~1      # 撤回commit，保留代码修改
git reset --mixed HEAD~1     # 撤回commit+暂存，保留代码（默认）
git reset --hard HEAD~1      # 彻底回到上个版本，代码也变
git reset --hard 版本id       # 回到指定版本
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `reset` | 重置 | rui sai te 瑞赛特 |
| `--soft` | 软 | sao fu te 扫夫特 |
| `--mixed` | 混合 | min ke si te 民科斯特 |
| `--hard` | 硬 | ha de 哈得 |
| `HEAD~1` | 前1个版本 | qian yi ge ban ben 前一个版本 |

---

### 4.6 switch — 切换分支（新写法）

```bash
git switch 分支名             # 切换到分支
git switch -c 新分支名        # 创建并切换到新分支
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `switch` | 切换 | si wei chi 斯威迟 |
| `-c` | create=创建 | ke rui ei te 克瑞埃特 |

---

### 4.7 tag — 标签

```bash
git tag                      # 查看所有标签
git tag v1.0                 # 创建标签
git tag -a v1.0 -m "说明"    # 创建带说明的标签
git push origin v1.0         # 推送标签到远程
git push origin --delete 标签名  # 删除远程标签
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `tag` | 标签 | tai ge 太哥 |
| `-a` | annotated=附注 | e nou tei ti de 埃诺忒提得 |

---

### 4.8 revert — 安全回滚

```bash
git revert 版本id            # 撤销某次提交（生成新的commit）
git revert HEAD             # 撤销最新提交
git revert --no-edit 版本id  # 撤销，不编辑备注
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `revert` | 还原 | rui ve te 瑞沃特 |
| `HEAD` | 当前最新提交 | hai de 海的 |
| `--no-edit` | 不编辑备注 | |

**注意：** revert 和 reset 的区别
- `reset` = 删除历史，回到过去（危险）
- `revert` = 保留历史，加一条新提交"撤销"（安全，适合团队）

---

### 4.9 backfill — 下载缺失对象（部分克隆时用）

```bash
git backfill
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `backfill` | 回填 | bai ke fi er 百克菲尔 |

---

## 五、协作（collaborate）

### 5.1 fetch — 只下载不合并

```bash
git fetch origin             # 下载远程更新，不合并
git fetch --all              # 下载所有远程
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `fetch` | 获取 | fei chi 飞奇 |
| `--all` | 所有 | suo you 所有 |

---

### 5.2 pull — 拉取并合并

```bash
git pull origin master       # 拉取远程更新并自动合并
git pull --rebase            # 拉取后变基（保持历史整洁）
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `pull` | 拉取 | pu er 普尔 |
| `--rebase` | 变基 | rui bei si 瑞贝斯 |

---

### 5.3 push — 推送

```bash
git push origin master              # 推送到远程
git push -u origin master           # 第一次推送
git push origin --delete 分支名      # 删除远程分支
git push origin --force master      # 强制推送（慎用）
git push origin --tags              # 推送所有标签
git push --all origin               # 推送所有分支
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `push` | 推送 | pu shi 普石 |
| `origin` | 远程仓库名（自定义） | ao rui jin 奥瑞金 |
| `master` | 分支名（自定义） | ma si te 马斯特 |
| `-u` | upstream=上游 | a pu si te rui mu 阿普斯特瑞姆 |
| `--delete` | 删除 | di li te 迪利特 |
| `--force` | 强制 | fo si 佛斯 |
| `--tags` | 所有标签 | tai ge si 太哥斯 |
| `--all` | 所有分支 | ao er 奥尔 |

---

## 六、远程仓库管理

### 6.1 remote — 管理远程连接

```bash
git remote -v                   # 查看所有远程仓库
git remote add 名字 地址         # 添加远程仓库
git remote remove 名字          # 删除远程仓库
git remote rename 旧名 新名     # 重命名远程仓库
```

| 部分 | 翻译 | 拼音 |
|------|------|------|
| `remote` | 远程 | rui mou te 瑞谋特 |
| `-v` | verbose=详细 | ve bou si 沃伯斯 |
| `add` | 添加 | ai de 埃得 |
| `remove` | 移除 | rui mu fu 瑞姆夫 |
| `rename` | 重命名 | rui nei mu 瑞内姆 |

---

## 七、日常使用流程

### 7.1 第一次使用

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git init
git remote add origin https://github.com/用户名/仓库名.git
```

### 7.2 每天写代码

```bash
git add .                    # 添加所有改过的文件
git commit -m "改了什么"      # 提交写备注
git pull origin master       # 先拉取远程更新
git push origin master       # 再推送到远程
```

### 7.3 分支操作

```bash
git checkout -b 新功能         # 创建新分支
git add . && git commit -m "写完了"  # 提交
git checkout master            # 切回主分支
git merge 新功能               # 合并新功能
git branch -d 新功能           # 删除分支
git push origin master         # 推送到远程
```

### 7.4 回滚操作

```bash
git log --oneline             # 找到要回滚的版本id
git reset --hard 版本id        # 回到那个版本
git push origin master --force # 推送到远程覆盖

---

## 八、GitHub 完整流程（从零开始）

### 第 1 步：在 GitHub 上创建仓库

```
1. 打开 https://github.com
2. 点右上角 + → New repository
3. 填仓库名（如 liu_yan_ban）
4. 选 Public（公开）或 Private（私有）
5. 点 Create repository
```

### 第 2 步：在你电脑上连接 GitHub

```bash
# 设置身份（第一次用 Git 必须做）
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub邮箱"

# 进入项目目录
cd 你的项目文件夹

# 初始化本地仓库
git init

# 连接 GitHub 仓库
git remote add origin https://github.com/你的用户名/仓库名.git
```

### 第 3 步：推送代码到 GitHub

```bash
git add .
git commit -m "第一次提交"
git pull origin master        # 如果 GitHub 上有 .gitignore 等文件
git push -u origin master
```

### 第 4 步：更新代码（日常）

```bash
git add .
git commit -m "改了什么"
git pull origin master
git push origin master
```

### 第 5 步：从 GitHub 下载到新电脑

```bash
# 新电脑上不需要 init，直接克隆
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名
```
```

---

## 九、查看文件是否被跟踪

### 9.1 `git ls-files` 文件名（最直接）

```bash
git ls-files 文件名
```

| 结果 | 说明 |
|:----|:------|
| 有输出（显示文件名） | ✅ 被跟踪了 |
| 没输出 | ❌ 没被跟踪（或已被忽略） |

### 9.2 `git status` 文件名

```bash
git status 文件名
```

| 结果 | 说明 |
|:----|:------|
| `Changes to be committed` 或 `modified` | ✅ 被跟踪 |
| `Untracked files` | ❌ 没被跟踪 |
| 不显示在列表里 | 🔒 被 `.gitignore` 忽略了 |

### 9.3 `git check-ignore -v` 文件名

```bash
git check-ignore -v 文件名
```

| 结果 | 说明 |
|:----|:------|
| 显示匹配的规则（如 `.gitignore:219:*.db database.db`） | 🔒 被 `.gitignore` 忽略了 |
| 没显示 | ✅ 没被忽略（或被跟踪） |

### 示例

```bash
# 查 app.py 是否被跟踪
git ls-files app.py

# 查 database.db 是否被忽略
git check-ignore -v database.db

# 看文件状态
git status database.db
```