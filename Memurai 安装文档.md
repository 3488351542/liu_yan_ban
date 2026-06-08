# Memurai 安装文档

> Windows 上运行 Redis 的方案 / 承德应职院微墙项目

---

## 1. 什么是 Memurai

Memurai 是 Windows 原生的 Redis 替代品，100% 兼容 Redis 协议。
因为 Redis 官方不支持 Windows，所以用 Memurai 在 Windows 上跑 Redis 服务。

---

## 2. 下载

| 版本 | 费用 | 说明 |
|------|------|------|
| **Developer Edition** | 免费 | 每次运行10天后需重启，个人开发够用 |
| Enterprise Edition | 收费 | 生产环境无限使用 |

下载地址：https://www.memurai.com/

选择 **Memurai for Redis — Developer Edition**

---

## 3. 安装

### 方式一：直接安装（推荐）

```bash
1. 双击下载的 Memurai-for-Redis-v8.2-RC1.msi
2. 一路 Next，默认安装到 C:\Program Files\Memurai
3. 装完自动启动 Redis 服务（端口 6379）
```

### 方式二：静默安装

```bash
msiexec /i "Memurai-for-Redis-v8.2-RC1.msi" /quiet
```

---

## 4. 验证安装

```bash
# 检查服务是否运行
redis-cli ping
# 返回 PONG 即成功
```

如果 `redis-cli` 找不到，手动加环境变量：

```
系统变量 → Path → 新建 → C:\Program Files\Memurai
```

---

## 5. 启动/停止

```bash
# 自动启停
redis-cli SHUTDOWN          # 停止
memurai-server.exe          # 手动启动

# 查看状态
redis-cli ping              # 检查连接
```

---

## 6. Python 连接

```bash
pip install redis -i https://pypi.tuna.tsinghua.edu.cn/simple
```

```python
import redis
r = redis.Redis(host='localhost', port=6379)
print(r.ping())  # True
```

---

## 7. 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `redis-cli` 找不到 | 没加环境变量 | 手动把 `C:\Program Files\Memurai` 加到 PATH |
| Connection Refused | Memurai 没启动 | 运行 `memurai-server.exe --service-start` |
| Developer 版到期 | 10天自动关机 | 重启 Memurai 服务即可 |
| 端口被占用 | 其他程序占用了6379 | 改 `C:\Program Files\Memurai\memurai.conf` 里的端口 |
