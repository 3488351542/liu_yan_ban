# PostgreSQL 安装配置文档

> PostgreSQL = 企业级数据库（ pou si te gre si kiu er 剖斯特格雷斯奎尔）
> 简称：pg（pi ji 皮吉）
> 用途：把留言板从 SQLite 换成 PostgreSQL

---

## 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| PostgreSQL | pou si te gre si kiu er 剖斯特格雷斯奎尔 | 数据库名 |
| postgres | pou si te gre si 剖斯特格雷斯 | 默认用户名 |
| psql | pi si kiu er 皮斯奎尔 | 命令行工具 |
| localhost | lou ke ou hou si te 漏克欧候斯特 | 本机地址 |
| password | pa si wo de 帕斯沃得 | 密码 |
| port | pao te 泡特 | 端口 |
| database | da te bei si 达特贝斯 | 数据库 |
| host | hou si te 候斯特 | 主机 |

---

## 一、下载

### 下载地址

```
https://www.postgresql.org/download/windows/
```

点 `Download the installer`，下载 `.exe` 文件。

---

## 二、安装步骤

> 安装包位置：`D:\yonghu2xiadesuoyouruanjiantongyianzhuanglujing\postgresql\postgresql-18.4-1-windows-x64.exe`

双击运行安装包，按以下步骤操作：

### 第 1 步：Welcome（欢迎）

```
┌─────────────────────────────────┐
│  Welcome to the PostgreSQL Setup │
│  [Next >]                       │
└─────────────────────────────────┘
```

点 **Next**。

| 参数 | 翻译 | 拼音 |
|------|------|------|
| Welcome | 欢迎 | wei er ka mu 威尔卡姆 |
| Next | 下一步 | nai ke si te 奈克斯特 |

---

### 第 2 步：Installation Directory（安装目录）

```
┌─────────────────────────────────┐
│  Installation Directory          │
│  D:\...\postgresql\sql          │
│  [Browse...]  [Next >]          │
└─────────────────────────────────┘
```

点 **Browse...** → 选 `D:\yonghu2xiadesuoyouruanjiantongyianzhuanglujing\postgresql\sql` → **Next**

| 参数 | 翻译 | 拼音 |
|------|------|------|
| Browse | 浏览 | bu rao zi 布绕子 |
| Directory | 目录 | dai rui ai ke te rui 戴瑞艾克特瑞 |

---

### 第 3 步：Select Components（选择组件）

```
┌─────────────────────────────────┐
│  Select Components               │
│  ☑ PostgreSQL Server            │
│  ☑ pgAdmin 4                    │
│  ☑ Stack Builder                │
│  ☑ Command Line Tools           │
│  [Next >]                       │
└─────────────────────────────────┘
```

**默认全选，不用改，点 Next。**

| 参数 | 翻译 | 拼音 |
|------|------|------|
| PostgreSQL Server | PostgreSQL 服务器 | se ve 瑟沃 |
| pgAdmin 4 | 图形化管理工具 | pi ji a dan 皮吉阿丹 |
| Stack Builder | 扩展工具 | si tai ke 斯太克 |
| Command Line Tools | 命令行工具 | ke man de lai en 科曼得来恩 |

---

### 第 4 步：Data Directory（数据目录）

```
┌─────────────────────────────────┐
│  Data Directory                  │
│  D:\...\sql\data                │
│  [Next >]                       │
└─────────────────────────────────┘
```

**默认路径，不用改，点 Next。**

数据目录用来存你数据库里的实际数据（表、记录等）。

---

### 第 5 步：Password（设置密码）

```
┌─────────────────────────────────┐
│  Password                        │
│  Password: [******]             │
│  Retype:   [******]             │
│  [Next >]                       │
└─────────────────────────────────┘
```

输入密码：`123456`（两次要一致）→ **Next**

| 参数 | 翻译 | 拼音 |
|------|------|------|
| Password | 密码 | pa si wo de 帕斯沃得 |
| Retype | 重新输入 | rui tai pu 瑞太普 |

**注意：** 记好这个密码，后面连接数据库要用。

---

### 第 6 步：Port（端口）

```
┌─────────────────────────────────┐
│  Port                            │
│  5432                           │
│  [Next >]                       │
└─────────────────────────────────┘
```

**默认 `5432`，不用改，点 Next。**

| 参数 | 翻译 | 拼音 |
|------|------|------|
| Port | 端口 | pao te 泡特 |

**5432 是什么：** 就像门牌号，程序通过这个端口找到 PostgreSQL。

---

### 第 7 步：Locale（地区）

```
┌─────────────────────────────────┐
│  Locale                          │
│  [Default locale]               │
│  [Next >]                       │
└─────────────────────────────────┘
```

**默认，不用改，点 Next。**

| 参数 | 翻译 | 拼音 |
|------|------|------|
| Locale | 地区 | lou kei ou 漏克欧 |

---

### 第 8 步：Ready to Install

```
┌─────────────────────────────────┐
│  Ready to Install PostgreSQL     │
│  [Next]  [Back]  [Cancel]       │
└─────────────────────────────────┘
```

点 **Next** 开始安装，等待进度条走完（约 2~5 分钟）。

---

### 第 9 步：Finish（完成）

```
┌─────────────────────────────────┐
│  Completing PostgreSQL Setup     │
│  ☐ Launch Stack Builder         │
│  [Finish]                       │
└─────────────────────────────────┘
```

- 取消勾选 `Launch Stack Builder`
- 点 **Finish**

---

## 三、验证安装

### 验证方式 1：命令行

```bash
psql --version
```

能看到版本号就装好了：

```
psql (PostgreSQL) 18.4
```

### 验证方式 2：查看服务

打开任务管理器 → 服务 → 找 `postgresql`，状态应为"正在运行"。

---

## 四、添加环境变量（让任意终端都能用 psql）

> 安装后 PowerShell、cmd 可能找不到 `psql` 命令，需要把 PostgreSQL 目录加到系统 PATH 里。

### 添加方法

打开 **PowerShell（管理员）**，执行：

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";D:\yonghu2xiadesuoyouruanjiantongyianzhuanglujing\postgresql\sql\bin", "User")
```

### 验证是否添加成功

```powershell
$env:Path -split ";" | Select-String -Pattern "postgresql"
```

显示以下内容即成功：

```
D:\yonghu2xiadesuoyouruanjiantongyianzhuanglujing\postgresql\sql\bin
```

### 添加后的效果

| 终端 | 能用吗 |
|:-----|:------:|
| PowerShell | ✅ 关掉重开即可 |
| cmd | ✅ 关掉重开即可 |
| Git Bash | ✅ |
| WSL（Linux子系统） | ✅ |

**注意：** 添加后需要**关掉终端重新打开**才能生效，或在当前终端执行 `$env:Path = [Environment]::GetEnvironmentVariable("Path", "User")` 刷新。

---

## 五、创建数据库

安装完成后，创建一个供项目使用的数据库：

```bash
# 连接到 PostgreSQL（会让你输密码：123456）
psql -U postgres

# 在 psql 里执行：
CREATE DATABASE message_board;

# 退出
\q
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| psql | PostgreSQL 命令行 | pi si kiu er 皮斯奎尔 |
| -U | user = 用户名 | yo ze 优则 |
| postgres | 默认管理员账号 | pou si te gre si 剖斯特格雷斯 |
| CREATE DATABASE | 创建数据库 | ke rui ei te 克瑞埃特 |
| \q | quit = 退出 | kui te 奎特 |

---

## 六、SQLite vs PostgreSQL 对比

| 对比项 | SQLite（之前） | PostgreSQL（之后） |
|--------|---------------|-------------------|
| 形式 | 一个 `.db` 文件 | 独立服务，常驻后台 |
| 启动 | 不用管，自动 | 必须启动才能用（默认开机自启） |
| 端口 | 不需要 | 占用 5432 端口 |
| 密码 | 不需要 | 需要密码连接 |
| 并发 | 差（一次只能一个人写） | 好（多人同时访问） |
| 适用场景 | 小工具、手机 App | 网站、企业应用 |

---

## 七、常用管理命令

### 启动/停止 PostgreSQL 服务

```bash
# 启动
net start postgresql

# 停止
net stop postgresql
```

### 连接到数据库

```bash
psql -U postgres              # 连接默认库
psql -U postgres -d message_board  # 连接指定库
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `-d` | database = 指定数据库 | da te bei si 达特贝斯 |

### 在 psql 里常用命令

```bash
\l                    # 查看所有数据库
\c 数据库名            # 切换数据库
\dt                   # 查看所有表
\d 表名               # 查看表结构
\du                   # 查看所有用户
\q                    # 退出
```

| 命令 | 翻译 | 拼音 |
|------|------|------|
| `\l` | list = 列表 | li si te 利斯特 |
| `\c` | connect = 连接 | ke nai ke te 科奈科特 |
| `\dt` | display tables = 显示表 | tei bou er si 忒伯尔斯 |
| `\d` | describe = 描述 | di si ke rai bu 迪斯克莱布 |
| `\du` | display users = 显示用户 | yo ze si 优则斯 |

---

## 八、注意事项

1. **密码别忘：** 安装时设的密码 `123456`，后面连接数据库每次都要用
2. **端口冲突：** 如果 5432 被占用，安装时可以改成别的（如 5433）
3. **服务必须运行：** PostgreSQL 是一个服务，电脑重启后如果没有自动启动，需要手动 `net start postgresql`
4. **防火墙：** 如果其他电脑要连你的数据库，需要防火墙放行 5432 端口（本机用不需要）
