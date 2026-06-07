# Docker 命令大全

> Docker = 容器化工具（da ke 达克）
> 把你的项目+环境打包成一个箱子，换个服务器也能直接跑

## Docker Desktop 界面中文翻译

### 左侧菜单栏

| 英文 | 中文 | 拼音 |
|------|------|------|
| **Containers** | 容器 | ken tei ne si 肯忒呢斯 |
| **Images** | 镜像 | yi mi zhi si 伊米之斯 |
| **Volumes** | 数据卷 | wo liu mu si 沃柳姆斯 |
| **Kubernetes** | 容器编排集群 | ku bo nei ti si 库伯内提斯 |
| **Builds** | 镜像构建 | bi er de si 比尔德斯 |
| **MCP Toolkit** | MCP 工具包 | tu er ki te 图尔基特 |
| **Docker Hub** | 镜像仓库 | ha bu 哈布 |
| **Extensions** | 插件扩展 | yi ke si ten shen si 伊克斯腾申斯 |

### Volumes 页面

| 英文 | 中文 | 拼音 |
|------|------|------|
| **Volume** | 数据卷 | wo liu mu 沃柳姆 |
| **Container** | 容器 | ken tei ne 肯忒呢 |
| **Create** | 创建 | ke rui ei te 克瑞埃特 |

**英文：** All data in a container is lost once it is removed.

| 单词 | 拼音 | 中文 |
|------|------|------|
| data | dei ta 嘚塔 | 数据 |
| lost | lao si te 涝斯特 | 丢失 |
| removed | rui mu fu de 瑞姆夫得 | 删除 |

### 顶部栏

| 英文 | 中文 | 拼音 |
|------|------|------|
| **Search** | 搜索 | se chai 瑟柴 |
| **Sign in** | 登录 | sai yin 赛因 |

### 底部状态栏

| 英文 | 中文 | 拼音 |
|------|------|------|
| **Engine running** | 引擎运行中 | en jin ran ning 恩金软宁 |
| **RAM** | 内存 | rai mu 瑞姆 |
| **CPU** | 处理器 | xi pi you 西皮优 |
| **Disk** | 磁盘 | di si ke 迪斯克 |

---

## 一、Docker 基础概念

```ascii
image = 镜像 / 模板（yi mi zhi 伊米之）
container = 容器 / 运行中的程序（ken tei ne 肯忒呢）
Dockerfile = 制作镜像的配方文件（da ke fi er 达克菲儿）
```

```
image（镜像） → docker run → container（容器）
（模板）                   （跑起来的程序）

docker run 镜像    = run = 运行（ran 软），从镜像启动容器
docker build       = build = 构建（bi er de 比尔德），用 Dockerfile 制作镜像
```

---

## 二、镜像操作（image = 镜像 / yi mi zhi 伊米之）

### 2.1 docker images — 查看本地有哪些镜像

```bash
docker images
docker image ls
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `images` | ✅ **固定** | 镜像列表 | yi mi zhi si 伊米之斯 |
| `ls` | ✅ **固定** | list = 列表 | li si te 利斯特 |
| `docker` | ✅ **固定** | 容器工具名 | da ke 达克 |

**输出示例：**
```
REPOSITORY    TAG       IMAGE ID       CREATED       SIZE
python        3.13      abc123def456   2 days ago    1.2GB
```

| 英文 | 翻译 | 拼音 |
|------|------|------|
| REPOSITORY | 仓库名 | rui pao zi te rui 瑞泡兹特瑞 |
| TAG | 标签 | tai ge 太哥 |
| IMAGE ID | 镜像编号 | yi mi zhi ai di 伊米之埃迪 |
| CREATED | 创建时间 | ke rui ei ti de 克瑞埃提德 |
| SIZE | 大小 | sai zi 赛子 |

---

### 2.2 docker pull — 下载镜像

```bash
docker pull 镜像名:标签
docker pull python:3.13          # python = Python语言（pai sen 派森）
docker pull nginx:latest         # nginx = Web服务器（en jin ke si 恩金克斯）
docker pull postgres:16          # postgres = 数据库名（pou si te ge re si 剖斯特格瑞斯）
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `pull` | ✅ **固定** | 拉取 / 下载 | pu er 普尔 |
| `镜像名` | ❌ **自定义** | 你要下载的镜像 | |
| `:` | ✅ **固定** | 分隔符 | |
| `标签` | ❌ **自定义** | 版本号（tag） | |
| `latest` | ✅ **固定** | 最新版 | lei te si te 雷特斯特 |

---

### 2.3 docker rmi — 删除镜像

```bash
docker rmi 镜像名
docker rmi python:3.13           # 删除 Python 镜像
docker rmi 镜像ID                # 用 ID 删
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `rmi` | ✅ **固定** | remove image = 删镜像 | a er ai 阿尔埃 |

---

### 2.4 docker build — 从 Dockerfile 制作镜像

```bash
docker build -t 镜像名:标签 .    # build（bi er de 比尔德）构建
docker build -t my-app:1.0 .     # 用当前目录的 Dockerfile 制作
docker build -t my-app:1.0 -f Dockerfile.prod .  # 指定 Dockerfile
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `build` | ✅ **固定** | build = 构建（bi er de 比尔德） | |
| `-t` | ✅ **固定** | tag = 名字+标签 | tai ge 太哥 |
| `-f` | ✅ **固定** | file = 指定文件 | fai er 法伊尔 |
| `.` | ❌ **自定义** | 当前目录 | |

---

## 三、容器操作（container = 容器 / ken tei ne 肯忒呢）

### 3.1 docker run — 启动容器

```bash
docker run 镜像名
docker run -d -p 8080:5000 my-app      # 后台运行 + 端口映射
docker run --name mycontainer my-app   # 指定容器名字
docker run -it mycontainer bash        # 交互模式
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `run` | ✅ **固定** | 运行 | ran 软 |
| `-d` | ✅ **固定** | daemon = 后台运行 | di meng 迪蒙 |
| `-p 8080:5000` | ✅ **固定** | port = 端口映射 | pao te 泡特 |
| `--name` | ✅ **固定** | 给容器起名 | nei mu 内姆 |
| `-it` | ✅ **固定** | interactive = 交互模式 | yin te ai ke ti fu 因特艾克替夫 |
| `bash` | ❌ **自定义** | 要运行的命令 | ba shi 巴十 |

**端口映射说明：**
```bash
docker run -p 8080:5000 my-app
              ↑       ↑
          你电脑访问    容器内部
         http://localhost:8080 → 容器里的 5000 端口
```

---

### 3.2 docker ps — 查看运行中的容器

```bash
docker ps                 # 只看正在运行的
docker ps -a              # 查看所有容器（包括已停止的）
docker ps -q              # 只显示容器ID（用于批量操作）
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `ps` | ✅ **固定** | process = 进程（pu rao sai si 普绕赛斯） status = 状态（si tai te si 斯太特斯） | pu sai 普赛 |
| `-a` | ✅ **固定** | all = 所有 | suo you |
| `-q` | ✅ **固定** | quiet = 安静（只显示ID） | kuai ye te 快耶特 |

---

### 3.3 docker stop — 停止容器

```bash
docker stop 容器名或ID
docker stop mycontainer          # 停止叫 mycontainer 的容器
docker stop $(docker ps -q)      # 停止所有容器
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `stop` | ✅ **固定** | 停止 | si tao pu 斯掏普 |

---

### 3.4 docker start — 启动已停止的容器

```bash
docker start 容器名
docker start mycontainer
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `start` | ✅ **固定** | 启动 | si da te 斯达特 |

---

### 3.5 docker rm — 删除容器

```bash
docker rm 容器名
docker rm mycontainer
docker rm $(docker ps -aq)       # 删除所有容器
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `rm` | ✅ **固定** | remove = 移除 | a er em 阿尔埃姆 |

---

### 3.6 docker logs — 查看容器日志

```bash
docker logs 容器名
docker logs -f mycontainer       # 实时跟踪日志
docker logs --tail 100 mycontainer  # 只看最后100行
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `logs` | ✅ **固定** | 日志 | lao ge 涝格 |
| `-f` | ✅ **固定** | follow = 实时跟踪 | fo lou 佛漏 |
| `--tail` | ✅ **固定** | 只看末尾 | tei er 忒尔 |

---

### 3.7 docker exec — 进入容器内部

```bash
docker exec -it 容器名 bash
docker exec -it mycontainer bash       # 进入容器，打开终端
docker exec mycontainer ls             # 在容器里执行一条命令
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `exec` | ✅ **固定** | execute = 执行 | yi ge sai ke te 伊格赛科特 |

---

## 四、Dockerfile — 制作镜像的配方

> 创建 Dockerfile 放到项目根目录，没有后缀名

### 4.1 Dockerfile 内容示例

```dockerfile
# FROM = 基于哪个镜像（fu rang mu 弗让姆）
FROM python:3.13-slim

# WORKDIR = 工作目录（wa ke di 沃克迪）
WORKDIR /app

# COPY = 复制文件到容器里（kao pi 考批）
COPY requirements.txt .

# RUN = 运行命令（ran 软）
RUN pip install -r requirements.txt    # pip = Python包管理器（pi pu 皮普）

# COPY 项目代码
COPY . .

# EXPOSE = 暴露端口（ai ke si pao zi 埃克斯泡子）
EXPOSE 5000

# CMD = 容器启动时执行（ke man de 科曼得）
# app:app = app.py 文件里的 app 变量（Flask 实例）
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
```

| 指令 | 固定/自定义 | 翻译 | 拼音 | 作用 |
|------|-----------|------|------|------|
| `FROM` | ✅ **固定** | 从 | fu rang mu 弗让姆 | 基于哪个镜像 |
| `WORKDIR` | ✅ **固定** | 工作目录 | wa ke di 沃克迪 | 进入哪个文件夹 |
| `COPY` | ✅ **固定** | 复制 | kao pi 考批 | 把文件放进镜像 |
| `RUN` | ✅ **固定** | 运行 | ran 软 | 构建时执行命令 |
| `EXPOSE` | ✅ **固定** | 暴露 | ai ke si pao zi 埃克斯泡子 | 声明容器端口 |
| `CMD` | ✅ **固定** | 命令 | ke man de 科曼得 | 启动时执行的命令 |
| `slim` | ✅ **固定** | 精简版 | si li mu 斯利姆 |

---

## 五、docker compose — 一键启动多个容器

> compose = 组合（kem pou zi 克姆剖子）
> 用 `docker-compose.yml` 文件同时启动多个服务

### 5.1 docker-compose.yml 示例

```yaml
version: '3.8'                    # version = 版本号（固定）
services:                          # services = 多个服务（固定）
  web:                             # web = 服务名（自定义）
    build: .                       # build（bi er de 比尔德）从当前目录构建
    ports:                         # ports = 端口映射（固定）
      - "8080:5000"
  db:
    image: postgres:16             # image = 镜像
    environment:                   # environment = 环境变量（固定）
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: 123456
```

| 英文 | 翻译 | 拼音 |
|------|------|------|
| services | 服务们 | se ve si si 瑟维斯斯 |
| ports | 端口 | pao ci 泡次 |
| environment | 环境变量 | yin wai en men te 因外恩门特 |
| version | 版本 | ve shen 沃申 |

### 5.2 常用命令

```bash
docker compose up                  # up = 启动所有服务
docker compose up -d               # 后台启动
docker compose down                # down = 停止并删除
docker compose logs -f             # logs = 查看日志
docker compose ps                  # ps = 查看状态
docker compose restart             # restart = 重启
```

| 命令 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `up` | ✅ **固定** | 启动 | a pu 阿普 |
| `down` | ✅ **固定** | 停止+删除 | dang 当 |
| `restart` | ✅ **固定** | 重启 | rui si ta te 瑞斯塔特 |

---

## 六、常用组合命令

```bash
# prune = 清理（pu run 普润）
docker container prune          # 清理所有停止的容器
docker image prune              # 清理所有不用的镜像

# stats = 资源统计（si tai ci 斯太次）
docker stats                    # 查看容器占用的CPU/内存

# 一键停止并删除所有容器
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
```

| 命令 | 翻译 | 拼音 |
|------|------|------|
| `prune` | 清理 | pu run 普润 |
| `stats` | 资源统计 | si tai ci 斯太次 |

---

## 七、Docker 命令速查表

| 命令 | 翻译 | 拼音 | 用途 |
|------|------|------|------|
| `docker images` | 镜像列表 | yi mi zhi si 伊米之斯 | 看本地有哪些镜像 |
| `docker pull 名` | 下载镜像 | pu er 普尔 | 从仓库下载镜像 |
| `docker rmi 名` | 删镜像 | a er ai 阿尔埃 | 删除镜像 |
| `docker build -t 名 .` | 构建镜像 | bi er de 比尔德 | 用 Dockerfile 制作 |
| `docker run 名` | 启动容器 | ran 软 | 从镜像启动容器 |
| `docker ps` | 进程列表 | pu sai 普赛 | 看运行中的容器 |
| `docker stop 名` | 停止 | si tao pu 斯掏普 | 停容器 |
| `docker start 名` | 启动 | si da te 斯达特 | 启容器 |
| `docker rm 名` | 删除 | a er em 阿尔埃姆 | 删容器 |
| `docker logs 名` | 日志 | lao ge 涝格 | 看日志 |
| `docker exec -it 名 bash` | 进入容器 | yi ge sai ke te 伊格赛科特 | 进容器内部 |
| `docker compose up` | 启动全部 | a pu 阿普 | 启动所有服务 |
| `docker compose down` | 停止全部 | dang 当 | 停止所有 |
| `docker stats` | 资源占用 | si tai ci 斯太次 | 看CPU内存 |

---

## 八、Dockerfile 指令速查

| 指令 | 翻译 | 拼音 | 作用 |
|------|------|------|------|
| `FROM` | 从 | fu rang mu 弗让姆 | 基于哪个镜像 |
| `WORKDIR` | 工作目录 | wa ke di 沃克迪 | 设置当前目录 |
| `COPY` | 复制 | kao pi 考批 | 把文件放进镜像 |
| `RUN` | 运行 | ran 软 | 装软件、建文件 |
| `EXPOSE` | 暴露端口 | ai ke si pao zi 埃克斯泡子 | 告诉别人用哪个端口 |
| `CMD` | 启动命令 | ke man de 科曼得 | 容器启动时执行 |

---

## 九、给你的留言板做 Docker 部署

### 第 1 步：创建 Dockerfile

```dockerfile
FROM python:3.13-slim                    # slim = 精简版（si li mu 斯利姆）
WORKDIR /app                             # app = 应用（ai pu 爱普）
COPY requirements.txt .                  # requirements = 依赖需求（rui kuai er men ci 瑞快尔门次）
RUN pip install -r requirements.txt      # pip = Python包管理器（pi pu 皮普）
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]  # gunicorn = Python服务器（ga ni ka en 嘎尼卡恩）
```

**`app:app` 拆解：**
```
app:app
 ↑    ↑
文件名  Flask 实例名
       └── app.py 里：app = Flask(__name__)
```

**如果 app.py 在子目录：**

| app.py 位置 | gunicorn 写法 |
|------------|--------------|
| `app.py` | `gunicorn app:app` |
| `backend/app.py` | `gunicorn backend.app:app` |
| `src/api/app.py` | `gunicorn src.api.app:app` |

规则：把 `/` 换成 `.`，去掉 `.py`

**`0.0.0.0` 为什么不能用 `127.0.0.1`：**
```
127.0.0.1 = 只允许容器内部访问 → 本机浏览器打不开 ❌
0.0.0.0   = 允许外部访问       → 本机浏览器能打开 ✅
```

### 第 2 步：构建镜像

```bash
docker build -t message-board:1.0 .
```

### 第 3 步：运行容器

```bash
docker run -d -p 5000:5000 --name my-board message-board:1.0
```

然后访问 http://localhost:5000 就能看到留言板了。
