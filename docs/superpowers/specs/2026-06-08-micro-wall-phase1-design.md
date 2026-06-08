# 承德应职院微墙 — 第一期设计文档

## 概述
将现有留言板改造为多分类内容平台（微墙），包含分类系统、底部导航、发布弹窗、点赞搜索、热榜等功能，分两期完成。

## 第一期范围

### 数据库
- messages 表新增：`category`(text), `likes_count`(int), `comments_count`(int)
- 新建 likes 表：user_email, message_id, unique 约束，一人一赞
- 新建 favorites 表：user_email, message_id, unique 约束
- users 表新增：nickname, avatar_url, phone

### 页面布局（从上到下）
1. 顶部标题：承德应职院微墙
2. 搜索框（🔍 搜索消息...）
3. 版权小字：著作者:谢先生 微信号:xjx200504091731（微信号可复制）
4. 功能入口：🤖 AI助手 | 🎨 绘图（同新窗口打开）
5. 今日热榜入口（炫酷样式，展开/收起面板）
6. Tab 切换栏：最新 | 留言板 | 日常投稿 | 二手闲置
7. 帖子列表（微博/朋友圈样式）
8. 底部固定导航：🏠 首页  ＋(发布)  👤 我的

### 后端路由
| 方法 | 路由 | 功能 |
|------|------|------|
| POST | /api/like/<msg_id> | 点赞/取消（toggle） |
| GET | /api/search?q=xxx | 搜索帖子 |
| GET | /api/messages?category=xxx&page=1 | 按分类获取帖子 |
| POST | /submit | 发布（新增 category 字段） |
| POST | /delete/<msg_id> | 删帖（仅作者/管理员） |
| 已有 | /api/upload | 图片上传（不变） |
| 已有 | /ai, /image-gen | AI/绘图（不变） |

### 前端
- templates/index.html — 完全重写（新布局、新样式）
- templates/profile.html — 新增（第二期做）
- static/css/style.css — 独立样式（第一期全部内嵌 style 标签，后续拆分）
- static/js/app.js — 独立 JS（第一期全部内嵌 script 标签，后续拆分）

### 不变的功能
- 用户注册/登录/退出
- AI 助手页面（/ai）
- 图片生成页面（/image-gen）
- 二维码页面（/qrcode）
- 图片上传 API

## 第二期范围（预告）
- 今日热榜逻辑实现（按点赞+评论排序 TOP10）
- "我的"页面（个人资料、帖子、收藏、统计）
- 头像/昵称/手机号编辑
- 账户切换

## 技术约束
- Flask + PostgreSQL（保持现有技术栈）
- 不支持 Elasticsearch，搜索用 PostgreSQL ILIKE
- 点赞/收藏用 AJAX fetch 无刷新
- 底部导航 position: fixed
- 兼容已有数据库数据（旧数据 category 默认为 'message'）
- 保持对 Railway 部署兼容
