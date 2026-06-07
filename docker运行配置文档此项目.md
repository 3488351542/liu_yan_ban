# Docker 运行配置文档 - 留言板项目

> 本文档只针对本项目（project1_message_board）
> 目录：d:\yonghu2xiadesuoyouruanjiantongyianzhuanglujing\4-24\5-30\xiang_mu\project1_message_board

---

## 准备工作

**确认 Docker 已安装：**

```bash
docker --version
```

显示 `Docker version 29.5.2` 说明已装好。

---

## 第 1 步：创建 Dockerfile

在项目目录下创建文件 `Dockerfile`（注意：没有后缀名）。

```
位置：project1_message_board/Dockerfile
```

### 文件内容

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
```

### 逐行详解

#### 第 1 行：FROM — 基于哪个镜像

```dockerfile
FROM python:3.13-slim
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `FROM` | ✅ **固定** | 从...开始 | fu rang mu 弗让姆 | Dockerfile 第一行必须是 FROM |
| `python` | ❌ **自定义** | Python 官方镜像 | pai sen 派森 | 你的项目是 Python 写的 |
| `:` | ✅ **固定** | 分隔符 | | 分隔镜像名和版本 |
| `3.13-slim` | ❌ **自定义** | 版本号 | | Python 3.13，slim=精简版 |

**为什么：** 项目需要 Python 环境。slim 版约 100MB，完整版 1GB，用 slim 足够。

---

#### 第 2 行：WORKDIR — 工作目录

```dockerfile
WORKDIR /app
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `WORKDIR` | ✅ **固定** | 工作目录 | wa ke di 沃克迪 | 容器里的当前路径 |
| `/app` | ❌ **自定义** | 路径名 | | 也可以在 `/myapp` |

**为什么：** 后面的命令都在这个目录执行，相当于 `cd /app`。

---

#### 第 3 行：COPY requirements.txt

```dockerfile
COPY requirements.txt .
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `COPY` | ✅ **固定** | 复制 | kao pi 考批 | 从本机复制到镜像 |
| `requirements.txt` | ❌ **自定义** | 依赖清单 | rui kuai er men ci 瑞快尔门次 | 记录要装哪些库 |
| `.` | ✅ **固定** | 点号=当前目录 | | WORKDIR 指定的 `/app` |

**为什么先复制这个文件而不直接复制全部代码：** Docker 每行命令会生成一个缓存层。只要 requirements.txt 没变，下次构建直接使用缓存，**不用重新装依赖**，速度快很多。

---

#### 第 4 行：RUN pip install — 安装依赖

```dockerfile
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `RUN` | ✅ **固定** | 运行（构建时执行） | ran 软 | 构建时执行的命令 |
| `pip` | ✅ **固定** | Python 包管理器 | pi pu 皮普 | 装 Python 库 |
| `install` | ✅ **固定** | 安装 | in si tao er 因斯掏尔 | |
| `-r` | ✅ **固定** | requirements 从文件读 | | |
| `requirements.txt` | ❌ **自定义** | 依赖文件 | | |
| `-i` | ✅ **固定** | index 指定下载源 | | 用哪个镜像站 |
| `清华源` | ❌ **自定义** | 国内镜像 | | 比官方源快 10 倍 |

**为什么：** 项目需要 Flask、gunicorn、requests、qrcode 等库，全部在 requirements.txt 里列着。国内用清华源下载快。

---

#### 第 5 行：COPY 项目代码

```dockerfile
COPY . .
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `COPY` | ✅ **固定** | 复制 | kao pi 考批 | |
| `.`（第一个） | ❌ **自定义** | 本机当前目录 | | 你电脑项目目录 |
| `.`（第二个） | ✅ **固定** | 容器里的当前目录 | | /app |

**为什么在第 4 行之后才复制：** 以后你只改代码不改依赖库时，第 1-4 行直接用缓存，只重新执行第 5 行，**构建时间从几分钟变几秒**。

---

#### 第 6 行：EXPOSE — 声明端口

```dockerfile
EXPOSE 5000
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `EXPOSE` | ✅ **固定** | 暴露端口 | ai ke si pao zi 埃克斯泡子 | 声明容器用什么端口 |
| `5000` | ❌ **自定义** | 端口号 | | Flask 默认 5000 |

**为什么：** Flask 监听 5000 端口，告诉 Docker 这个容器要用 5000。注意这只是声明，真正映射到本机还要靠 `docker run -p`。

---

#### 第 7 行：CMD — 启动命令

```dockerfile
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
```

| 参数 | 固定/自定义 | 翻译 | 拼音 | 说明 |
|------|-----------|------|------|------|
| `CMD` | ✅ **固定** | 启动命令 | ke man de 科曼得 | 容器启动时执行 |
| `gunicorn` | ✅ **固定** | Python 服务器 | ga ni ka en 嘎尼卡恩 | 比 Flask 自带稳定 |
| `app:app` | ❌ **自定义** | app.py 里的 app 变量 | | 从 app.py 取 Flask 实例 |
| `-b` | ✅ **固定** | bind 绑定地址 | | 监听哪个 IP+端口 |
| `0.0.0.0:5000` | **固定** | 所有 IP 的 5000 端口 | | 0.0.0.0=允许外部访问 |

**`app:app` 拆解：**

```
app:app
 ↑    ↑
文件名  Flask 实例名
       └── app.py 里有 app = Flask(__name__)
```

**`0.0.0.0` vs `127.0.0.1`：**

```
127.0.0.1 = 只允许容器内部访问 → 你本机浏览器打不开 ❌
0.0.0.0   = 允许外部访问       → 你本机浏览器能打开 ✅
```

---

## 第 2 步：构建镜像

```bash
cd d:/yonghu2xiadesuoyouruanjiantongyianzhuanglujing/4-24/5-30/xiang_mu/project1_message_board
docker build -t message-board:1.0 .
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `docker` | ✅ **固定** | Docker 命令 | da ke 达克 |
| `build` | ✅ **固定** | 构建 | bi er de 比尔德 |
| `-t` | ✅ **固定** | tag = 起名+版本 | tai ge 太哥 |
| `message-board:1.0` | ❌ **自定义** | 镜像名:版本号 | |
| `.` | ❌ **自定义** | 当前目录（找 Dockerfile） | |

**构建过程：**
```
[+] Building ...
 → FROM python:3.13-slim        ← 下载 Python 基础镜像
 → WORKDIR /app                  ← 创建目录
 → COPY requirements.txt .       ← 复制依赖文件
 → RUN pip install ...           ← 安装依赖（最慢的一步）
 → COPY . .                      ← 复制代码
 → EXPOSE 5000                   ← 声明端口
 → CMD gunicorn ...              ← 设置启动命令
```

---

## 第 3 步：查看镜像

```bash
docker images
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `images` | 镜像列表 | yi mi zhi si 伊米之斯 |

输出示例：
```
REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
message-board    1.0       abc123def456   30 seconds ago   500MB
```

---

## 第 4 步：运行容器

```bash
docker run -d -p 5000:5000 --name my-board message-board:1.0
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `run` | ✅ **固定** | 运行 | ran 软 |
| `-d` | ✅ **固定** | daemon = 后台运行 | di 迪 |
| `-p 5000:5000` | ✅ **固定** | port = 端口映射 | pao te 泡特 |
| `--name` | ✅ **固定** | 给容器起名 | nei mu 内姆 |
| `my-board` | ❌ **自定义** | 你起的容器名 | |
| `message-board:1.0` | ❌ **自定义** | 用哪个镜像启动 | |

**端口映射说明：**
```
-p 5000:5000
   ↑       ↑
本机端口  容器内部端口
           Flask 跑在 5000 端口
你访问 http://localhost:5000 → 转到容器里的 Flask
```

---

## 第 5 步：查看容器

```bash
docker ps
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `ps` | process status = 进程状态 | pu sai 普赛 |

看到 `my-board` 在列表里就说明运行成功。

---

## 第 6 步：打开浏览器

```
http://localhost:5000
```

应该能看到留言板首页。

---

## 常用容器管理命令

### 查看日志

```bash
docker logs my-board           # 查看日志
docker logs -f my-board        # -f = follow = 实时跟踪
```

### 停止容器

```bash
docker stop my-board
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `stop` | 停止 | si tao pu 斯掏普 |

### 启动已停止的容器

```bash
docker start my-board
```

### 删除容器

```bash
docker rm my-board
```

### 删除镜像

```bash
docker rmi message-board:1.0
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `rmi` | remove image = 删镜像 | a er ai 阿尔埃 |

---

## 完整流程（一键执行）

```bash
# 1. 进入项目目录
cd d:/yonghu2xiadesuoyouruanjiantongyianzhuanglujing/4-24/5-30/xiang_mu/project1_message_board

# 2. 构建镜像
docker build -t message-board:1.0 .

# 3. 运行容器
docker run -d -p 5000:5000 --name my-board message-board:1.0

# 4. 查看
docker ps
docker logs my-board

# 5. 打开浏览器访问 http://localhost:5000

# 6. 停止并删除
docker stop my-board
docker rm my-board
```

---

## 修改代码后重新部署

改完代码后，只需要重新构建 + 运行：

```bash
# 删除旧容器
docker stop my-board
docker rm my-board

# 删除旧镜像
docker rmi message-board:1.0

# 重新构建
docker build -t message-board:1.0 .

# 重新运行
docker run -d -p 5000:5000 --name my-board message-board:1.0
```

---

## 打包发给别人

### 第 1 步：导出镜像为文件

```bash
docker save -o message-board.tar message-board:1.0
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `save` | ✅ **固定** | 保存 | sei fu 塞夫 |
| `-o` | ✅ **固定** | output = 输出文件名 | |
| `message-board.tar` | ❌ **自定义** | 导出的文件名 | |
| `message-board:1.0` | ❌ **自定义** | 要导出的镜像名 | |

### 第 2 步：把文件发给朋友

```
生成的文件：message-board.tar（约 300~500MB）
发送方式：
  ✅ U盘复制
  ✅ 微信/QQ
  ✅ 网盘（百度网盘、阿里云盘）
  ❌ 邮件（附件太小）
```

### 第 3 步：朋友那边导入

```bash
docker load -i message-board.tar
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `load` | ✅ **固定** | 导入 | lou de 漏得 |
| `-i` | ✅ **固定** | input = 输入文件 | |

### 第 4 步：朋友运行

```bash
docker run -d -p 5000:5000 --name message-board message-board:1.0
```

然后打开 http://localhost:5000 就能用了。

### 注意事项

| 问题 | 说明 |
|------|------|
| 朋友不需要装 Python | Docker 镜像自带 Python + Flask + 所有依赖 |
| 朋友只需要装 Docker | 必须先装 Docker Desktop |
| 数据不共享 | 你的留言和朋友的留言是分开的，各自一个数据库 |

