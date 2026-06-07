# .gitignore 编写规则大全

> .gitignore = Git 忽略文件（git i gao en 吉特伊高恩）
> 作用：告诉 Git "这些文件不要跟踪，不要提交，不要推送"
> 文件位置：项目根目录下，文件名就是 `.gitignore`

---

## 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| gitignore | git i gao en 吉特伊高恩 | Git 忽略文件 |
| ignore | i gao en 伊高恩 | 忽略 |
| venv | ven v 文维 | 虚拟环境目录 |
| secret | si ke rui te 斯克瑞特 | 密钥 |
| config | ken fi ge 肯菲格 | 配置 |
| cache | kai chi 开驰 | 缓存 |
| log | lao ge 涝格 | 日志 |
| temp | tai mu pu 太姆普 | 临时文件 |

---

## 一、基础语法

### 1.1 注释

```gitignore
# 井号开头表示注释
# 这一行会被 Git 忽略
```

### 1.2 忽略单个文件

```
database.db              # 忽略根目录下的 database.db
config.yml               # 忽略根目录下的 config.yml
password.txt             # 忽略根目录下的 password.txt
```

### 1.3 忽略整个文件夹

```
venv/                    # 忽略 venv 文件夹及其所有内容
__pycache__/             # 忽略 __pycache__ 文件夹
node_modules/            # 忽略 node_modules 文件夹
.env/                    # 忽略 .env 文件夹
```

**注意：** 结尾的 `/` 表示这是一个文件夹。

### 1.4 忽略所有某类文件（通配符）

```
*.db                     # 忽略所有 .db 结尾的文件
*.log                    # 忽略所有 .log 结尾的文件
*.tmp                    # 忽略所有 .tmp 结尾的文件
*.pyc                    # 忽略所有 .pyc 结尾的文件
*.bak                    # 忽略所有 .bak（备份）文件
*.zip                    # 忽略所有 .zip 文件
*.tar                    # 忽略所有 .tar 文件
```

### 1.5 通配符详解

```
*        # 任意多个字符（除了 /）
?        # 任意一个字符
[...]    # 字符范围，如 [abc] 匹配 a、b、c
**       # 任意层级目录
```

| 写法 | 匹配什么 |
|------|---------|
| `*.log` | 所有 .log 文件（任何目录） |
| `??.txt` | a.txt ✅ ab.txt ✅ abc.txt ❌ |
| `[abc].py` | a.py ✅ b.py ✅ d.py ❌ |
| `**/temp` | 所有层级下的 temp 文件和文件夹 |

---

## 二、进阶用法

### 2.1 路径限制（只忽略根目录下的）

```
/build                  # 忽略根目录下的 build（不含子目录的 build）
/config.env             # 只忽略根目录下的 config.env

# 对比：
build/                  # 忽略所有目录下的 build 文件夹
/build                  # 只忽略根目录下的 build
```

### 2.2 例外规则（! 取反）

```
# 忽略所有 .env 文件
.env

# 但保留 .env.example（不忽略它）
!.env.example
```

| 写法 | 作用 |
|------|------|
| `!文件名` | 白名单：这个文件不忽略 |
| `!文件夹/` | 白名单：这个文件夹不忽略 |

### 2.3 忽略子文件夹下的特定内容

```
# 只忽略 src 文件夹里的 .log 文件
src/*.log

# 忽略所有子目录下的 config.json
**/config.json

# 忽略 dist 里所有 .map 文件
dist/**/*.map
```

### 2.4 忽略空文件夹

```
# Git 不跟踪空文件夹，所以你不需要写规则忽略空文件夹
# 但如果文件夹里有 .gitkeep，就不会被忽略
```

---

## 三、常见项目配置

### 3.1 Python 项目

```gitignore
# 虚拟环境
venv/
env/
.venv/
env.bak/

# 缓存
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# 数据库
*.db
*.sqlite
*.sqlite3

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/

# 密钥
*.key
*.pem
secrets.toml

# 构建产物
dist/
build/
*.egg-info/

# 日志
*.log
```

### 3.2 Node.js 项目

```gitignore
node_modules/
npm-debug.log
yarn-error.log
.env
.env.local
dist/
build/
.cache/
*.tsbuildinfo
```

### 3.3 Java 项目

```gitignore
target/
*.class
*.jar
*.war
*.log
.idea/
*.iml
.settings/
.project
```

### 3.4 Docker 项目

```gitignore
# 镜像 tar 包
*.tar
*.tar.gz

# 容器数据
data/
volumes/

# Docker 环境
.env
docker-compose.override.yml
```

---

## 四、实际案例解析

### 案例 1：你的留言板项目

```gitignore
# 目前已有的：
.streamlit/secrets.toml   # ↓ 忽略 .streamlit 里的密钥文件
*.db                      # ↓ 忽略所有数据库文件
venv/                     # ↓ 忽略虚拟环境

# 建议再加：
__pycache__/              # Python 缓存
.env                      # 环境变量（如果以后用）
*.log                     # 日志文件
.vscode/                  # VS Code 配置
.idea/                    # PyCharm 配置
Dockerfile                # 如果不想把 Dockerfile 推上去
```

### 案例 2：用 ! 保留特定文件

```gitignore
# 忽略所有 .env 文件
.env*

# 但保留 .env.example 作为模板
!.env.example
```

### 案例 3：多层目录精准控制

```gitignore
# 忽略所有子目录的 secrets 文件夹
**/secrets/

# 但保留 src/secrets/important.md
!src/secrets/important.md
```

---

## 五、常见误区

| 错误写法 | 问题 | 正确写法 |
|---------|------|---------|
| `venv` | 也会匹配 `venv.py` | `venv/` |
| `*.db` | 根目录和子目录全忽略 | 如果只想忽略根目录：`/*.db` |
| `dir/*` | 只忽略 dir 下第一层，不递归 | `dir/**` 或 `dir/` |
| 不加 `!.env.example` 就直接写 `.env*` | `.env.example` 也被忽略了 | 先写 `.env*` 再写 `!.env.example` |

---

## 六、为什么不忽略还有用

`.gitignore` 不只是管"推不推送"，它还管：

| 作用 | 说明 |
|------|------|
| `git add .` 时自动跳过 | 加了忽略的文件不会被 git add |
| `git status` 不显示 | 忽略的文件不会出现在修改列表里 |
| 推送也不包含 | 远程仓库没有这些文件 |

**注意：** 如果一个文件**已经被 Git 跟踪了**（比如已经 `git add` 或 `git commit` 过），这时再加 `.gitignore` 也无效。需要先：

```bash
# 让 Git 停止跟踪这个文件
git rm --cached 文件名

# 然后再写进 .gitignore
```

---

## 七、查看规则是否生效

```bash
# 测试 .gitignore 规则是否匹配某个文件
git check-ignore -v 文件名

# 查看哪些文件被忽略
git status --ignored
```

| 命令 | 翻译 | 拼音 |
|------|------|------|
| `check-ignore` | 检查忽略规则 | che ke i gao en 车克伊高恩 |
| `-v` | verbose = 详细 | ve bou si 沃伯斯 |
| `--ignored` | 被忽略的 | i gao en de 伊高恩得 |
