# Docker 镜像加速配置

> 原因：Docker Hub 官方镜像站在国外，国内访问被墙（连接超时）
> 解决：配置国内镜像加速器

---

## 问题现象

运行 `docker build -t message-board:1.0 .` 时报错：

```
ERROR: failed to resolve source metadata for docker.io/library/python:3.13-slim
dial tcp 108.160.169.175:443: connectex: A connection attempt failed
```

简单说：**Docker 下载不了 Python 基础镜像，因为连不上外网。**

---

## 解决方法

### 第 1 步：修改 Docker 配置文件

文件位置：`C:\Users\38554\.docker\daemon.json`

添加 `registry-mirrors`（镜像加速器地址）：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io",
    "https://dockerproxy.link",
    "https://docker.jiaxin.site",
    "https://dc.j8.work",
    "https://docker.nju.edu.cn",
    "https://atomhub.openatom.cn"
  ]
}
```

配置说明：

| 配置项 | 说明 |
|--------|------|
| `registry-mirrors` | 镜像加速器列表，Docker 会依次尝试 |
| `docker.xuanyuan.me` | 轩辕镜像（公益免费） |
| `docker.1ms.run` | 毫秒镜像（稳定快速） |
| `docker.m.daocloud.io` | DaoCloud 镜像（老牌公益） |
| `dockerproxy.link` | 代理镜像 |
| `docker.jiaxin.site` | 嘉信镜像 |
| `dc.j8.work` | 备用镜像 |
| `docker.nju.edu.cn` | 南京大学镜像 |
| `atomhub.openatom.cn` | 开放原子镜像（336个基础镜像） |

---

### 第 2 步：重启 Docker Desktop

修改配置后必须重启才能生效：

方式一：右键 Docker 桌面右下角图标 → Restart
方式二：打开 Docker Desktop → 设置 ⚙️ → Restart

---

### 第 3 步：验证是否生效

重启后运行：

```bash
docker info
```

看到输出中有以下内容即生效：

```
Registry Mirrors:
  https://docker.mirrors.ustc.edu.cn/
  https://hub-mirror.c.163.com/
```

---

### 第 4 步：重新构建

```bash
docker build -t message-board:1.0 .
```

---

## 参数解析

| 参数 | 翻译 | 拼音 |
|------|------|------|
| registry | 注册表 / 镜像仓库 | rui zhi si te rui 瑞知斯特瑞 |
| mirror | 镜像 / 加速器 | mi re 米热 |
| daemon | 守护进程（Docker 后台服务） | di men 迪门 |
| json | 配置文件格式 | jei sen 杰森 |
| restart | 重启 | rui si ta te 瑞斯它特 |
