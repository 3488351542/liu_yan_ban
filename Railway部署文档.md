# Railway 部署文档 - 留言板项目

> Railway = 云端部署平台（rei wei 瑞威）
> 用途：把留言板项目部署到云端，让别人能访问
> 项目地址：https://github.com/3488351542/liu_yan_ban

---

## 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| Railway | rei wei 瑞威 | 部署平台名 |
| deploy | di pu lao yi 迪普老伊 | 部署 |
| redeploy | rui di pu lao yi 瑞迪普老伊 | 重新部署 |
| PostgreSQL | pou si te gre si kiu er 剖斯特格雷斯奎尔 | 数据库 |
| DATABASE_URL | da te bei si yo er ao 达特贝斯优尔奥 | 数据库连接地址 |
| target port | ta ge te pao te 塔格特泡特 | 目标端口 |
| crash | ke ra shi 克拉石 | 崩溃 |
| log | lao ge 涝格 | 日志 |

---

## 一、准备工作

### 1.1 项目已上传到 GitHub

```bash
# 确认你的项目在 GitHub 上
git remote -v
# 显示：
# origin  https://github.com/3488351542/liu_yan_ban.git (fetch)
# origin  https://github.com/3488351542/liu_yan_ban.git (push)
```

### 1.2 项目根目录有 Dockerfile

```
project1_message_board/
  ├── Dockerfile        ← Railway 需要用 Dockerfile 构建
  ├── app.py
  ├── requirements.txt
  └── ...
```

### 1.3 app.py 支持 DATABASE_URL 环境变量

```python
# get_db() 函数必须写成这样（同时支持本地和云端）：
def get_db():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # 云端：用 Railway 提供的连接地址
        return psycopg2.connect(database_url)
    # 本地：用本机的 PostgreSQL
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="message_board",
        user="postgres",
        password="123456"
    )
```

---

## 二、在 Railway 上创建项目

### 第 1 步：登录 Railway

```
https://railway.app/
```

用 GitHub 账号登录。

### 第 2 步：创建新项目

点 **New Project** → **Deploy from GitHub repo** → 选择 `3488351542/liu_yan_ban`

### 第 3 步：确认分支设置

在 Settings 里查看：

| 设置项 | 值 |
|:-------|:----|
| Branch connected to production | `master`（或你推代码的分支） |
| Auto deploys when pushed to GitHub | ✅ 开启 |

---

## 三、添加 PostgreSQL 数据库

### 第 1 步：创建数据库服务

在项目页面点 **New** → **Database** → **PostgreSQL**

Railway 会自动：
- ✅ 安装 PostgreSQL（基于 `ghcr.io/railwayapp-templates/postgres-ssl`）
- ✅ 生成数据库连接地址
- ✅ 创建环境变量 `DATABASE_URL`

### 第 2 步：把 DATABASE_URL 注入到应用

去 **app 服务**（不是 PostgreSQL 服务）的 **Variables** 页面：

1. 点 **Add Variable**（或 **Add Reference**）
2. 名称填：`DATABASE_URL`
3. 值选：**Refer** → 选择 PostgreSQL 服务 → 选 `DATABASE_URL`
4. 显示为：`${{Postgres.DATABASE_URL}}`
5. 点 **Add**（或 **Deploy**）

---

## 四、配置端口

### 重要：Target port 必须和应用的端口一致

| 你的应用监听端口 | Dockerfile 里写的 | Railway Target port |
|:---------------:|:-----------------:|:------------------:|
| 5000 | `EXPOSE 5000` + `CMD ... -b 0.0.0.0:5000` | **5000** |

去 **Settings** → **Networking** → **Target port**，改成 `5000`（和 Dockerfile 里一致）。

**常见错误：** 如果 Target port 是 8080 但应用监听 5000，会返回 502。

---

## 五、部署

### 5.1 自动部署

推送代码到 GitHub 的 `master` 分支后，Railway 会自动部署：

```bash
git add .
git commit -m "改了什么"
git push origin master
```

### 5.2 手动重新部署（Redeploy）

如果改了环境变量或设置，需要手动触发：

去 **Deployments** 标签 → 找到最新部署 → 点 `⋯` → **Redeploy**

### 5.3 确认部署成功

| 状态 | 含义 |
|:-----|:------|
| ✅ **Active** | 部署成功，应用运行中 |
| ❌ **Crashed** | 部署失败，需要看日志 |
| 🕐 **Deploying** | 正在构建/部署中 |

---

## 六、常见错误及解决

### 错误 1：502 Bad Gateway

```
症状：浏览器打开显示 502
日志：没有明显报错，Starting Container 后直接开始接收请求
```

| 原因 | 解决方法 |
|:-----|:---------|
| Target port 和监听端口不一致 | Settings → Target port 改为 5000 |
| 应用启动太慢 | Healthcheck Path 可以暂时不设 |

### 错误 2：psycopg2.OperationalError - Connection refused

```
症状：日志里显示连接 localhost:5432 失败
     connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

| 原因 | 解决方法 |
|:-----|:---------|
| `DATABASE_URL` 变量没设置 | Variables 页面添加 `DATABASE_URL` → Refer → PostgreSQL |
| 变量加了但没 Redeploy | 手动触发 Redeploy |
| 代码里没读 `DATABASE_URL` | `get_db()` 里加 `os.environ.get("DATABASE_URL")` 判断 |

### 错误 3：应用崩溃（Crashed）

```
症状：Deployments 显示 Crashed，日志有报错
```

| 原因 | 解决方法 |
|:-----|:---------|
| 数据库连不上 | 检查 DATABASE_URL 变量 |
| Python 依赖缺失 | 检查 requirements.txt |
| 代码语法错误 | 本地先测试再推送 |

### 错误 4：502 但应用状态是 Active

```
症状：状态显示 Active，但访问还是 502
```

| 原因 | 解决方法 |
|:-----|:---------|
| Target port 是 8080 但应用是 5000 | Settings → Target port → 改 5000 |
| 应用还在启动中 | 等 10-20 秒再刷新 |

---

## 七、查看日志

### 查看部署日志（Build Logs）

```
Deployments → 点击部署记录 → Build Logs
```

显示内容：Docker 构建过程、Python 依赖安装

### 查看运行日志（Runtime Logs）

```
Deployments → 点击部署记录 → Runtime Logs / Deploy Logs
```

显示内容：应用启动输出、报错信息

### 查看 HTTP 日志

```
HTTP Logs 标签
```

显示内容：每个请求的状态码、路径、耗时

---

## 八、注意事项

| 事项 | 说明 |
|:-----|:------|
| **GitHub 必须是最新代码** | 推送后确认 `git log origin/master` 是最新 commit |
| **变量添加后要 Redeploy** | 改了环境变量不会自动部署，必须手动触发 |
| **DATABASE_URL 需要 Refer** | 不是手动填字符串，是引用 PostgreSQL 服务 |
| **Target port 必须匹配** | 应用监听什么端口，这里就写什么端口 |
| **本地和云端数据库分开** | 本地数据不会自动同步到云端 |
| **免费额度** | Railway 免费版每月有额度和时间限制 |

---

## 九、SQLite vs PostgreSQL 部署区别

| 对比 | SQLite（旧） | PostgreSQL（新） |
|:-----|:------------|:-----------------|
| 数据库位置 | 项目文件夹里的 `.db` 文件 | 独立的数据库服务 |
| 云端部署 | 文件随代码一起上传 | 需额外创建 PostgreSQL 服务 |
| 数据持久化 | Docker 部署会被覆盖 | 独立服务，数据安全 |
| 环境变量 | 不需要 | 需要 `DATABASE_URL` |
| 代码适配 | 不需要 | `get_db()` 要读环境变量 |
