# Railway 部署

> 完整项目文档已合并到 **[部署通用文档.md](./部署通用文档.md)**
> 本文档仅保留 Railway 特有配置和常见问题

## 快速部署

```bash
git push origin master
# Railway 自动检测 Dockerfile 并部署
```

## 关键设置

| 项目 | 值 | 说明 |
|------|-----|------|
| Target Port | **5000** | 与 Dockerfile 的 EXPOSE 一致 |
| Start Command | 使用 Dockerfile | CMD 已配好 gunicorn |
| PostgreSQL | 插件添加 | 自动注入 `DATABASE_URL` |

## 常见问题

| 问题 | 解决 |
|------|------|
| 502 Bad Gateway | Target Port 没设成 5000 |
| Gunicorn 超时 | Dockerfile 加 `--timeout 600` |
| DATABASE_URL 没注入 | Variables → Refer PostgreSQL |
| 数据库列缺失 | 重启自动补全（init_db 兼容） |

完整踩坑记录见 `部署通用文档.md` → 第9节
