# SQL 命令大全（增删改查）

> 运行：`.\db "你的SQL"`
> SQL = Structured Query Language = 结构化查询语言（si kiu er 斯奎尔）

### 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| users | yo ze si 优则斯 | 用户表 |
| messages | mai sei zhi si 麦塞至斯 | 留言表 |
| alice | ai li si 艾丽丝 | 用户名 |
| bob | bao bo 鲍勃 | 用户名 |
| null | na er 纳尔 | 空值 |

---

## 一、数据库表结构

> 当前项目共 4 张表

### 1.1 users — 用户表（user = 用户 / yo ze 优则）

```sql
.\db "pragma table_info(users)"
```

| 序号 | 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|------|
| 1 | `id` | 编号 | ai di 埃迪 | integer | 主键，自动增长 |
| 2 | `email` | 邮箱 | yi mei ou 伊梅欧 | text | 唯一，不能重复 |
| 3 | `password` | 密码 | pa si wo de 帕斯沃得 | text | 加密后乱码 |
| 4 | `role` | 角色 | rou ou 肉欧 | text | 'admin'或'user' |
| 5 | `created_at` | 创建时间 | ke rui ei ti de ai te 克瑞埃提德埃特 | timestamp | 注册时间 |

**练习数据：** `.\db "insert into users (email, password, role) values ('test@qq.com', '123456', 'user')"`

---

### 1.2 messages — 留言表（message = 留言 / mai sei zhi 麦塞至）

```sql
.\db "pragma table_info(messages)"
```

| 序号 | 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|------|
| 1 | `id` | 编号 | ai di 埃迪 | integer | 主键 |
| 2 | `username` | 用户名 | yo ze nei mu 优则内姆 | text | 显示名字 |
| 3 | `content` | 内容 | ken ten te 肯ten特 | text | 留言内容 |
| 4 | `reply_to` | 回复给 | rui pu lai tu 瑞普来突 | integer | null=原始留言，数字=回复xx |
| 5 | `user_email` | 用户邮箱 | yo ze yi mei ou 优则伊梅欧 | text | 谁发的 |
| 6 | `created_at` | 创建时间 | ke rui ei ti de ai te 克瑞埃提德埃特 | timestamp | 发布时间 |

---

### 1.3 chat_messages — AI 聊天表（chat = 聊天 / chai te 柴特）

```sql
.\db "pragma table_info(chat_messages)"
```

| 序号 | 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|------|
| 1 | `id` | 编号 | ai di 埃迪 | integer | 主键 |
| 2 | `user_email` | 用户邮箱 | yo ze yi mei ou 优则伊梅欧 | text | 谁的对话 |
| 3 | `role` | 角色 | rou ou 肉欧 | text | 'user'或'assistant' |
| 4 | `content` | 内容 | ken ten te 肯ten特 | text | 具体内容 |
| 5 | `reasoning` | 推理 | rui ze ning 瑞泽宁 | text | 深度思考过程 |
| 6 | `model` | 模型 | mao dou 茅斗 | text | flash 或 pro |
| 7 | `created_at` | 创建时间 | ke rui ei ti de ai te 克瑞埃提德埃特 | timestamp | 发言时间 |

---

### 1.4 user_config — 用户配置表（config = 配置 / ken fi ge 肯菲格）

```sql
.\db "pragma table_info(user_config)"
```

| 序号 | 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|------|
| 1 | `email` | 邮箱 | yi mei ou 伊梅欧 | text | 主键 |
| 2 | `api_key` | API密钥 | ei pi ai ki 埃皮埃奇 | text | DeepSeek API Key |

---

## 二、查（SELECT = 查询 / si lai ke te 斯莱科特）

### 2.1 基本查询

| 序号 | 命令 | 翻译 | 说明 |
|------|------|------|------|
| 2.1.1 | `select * from users` | select=查询, from=从, *=所有, users=用户表 | 查所有用户 |
| 2.1.2 | `select * from messages` | messages=留言表 | 查所有留言 |
| 2.1.3 | `select * from chat_messages` | chat=聊天 | 查所有聊天记录 |
| 2.1.4 | `select * from user_config` | config=配置 | 查 API Key 配置 |

### 2.2 指定列

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.2.1 | `select email, role from users` | 只看邮箱和角色 |
| 2.2.2 | `select id, username, content from messages` | 只看留言的编号、用户名、内容 |
| 2.2.3 | `select username, content from messages limit 3` | 只看前3条的用户名和内容 |

### 2.3 条件筛选（WHERE = 哪里 / wei er 威尔）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.3.1 | `select * from users where role = 'admin'` | role=角色，'admin'=管理员 |
| 2.3.2 | `select * from users where role = 'user'` | 'user'=普通用户 |
| 2.3.3 | `select * from messages where username = 'alice'` | username=用户名，查 alice 的留言 |
| 2.3.4 | `select * from messages where reply_to is null` | is null=为空，只查原始留言 |
| 2.3.5 | `select * from messages where reply_to is not null` | is not null=不为空，只查回复 |

### 2.4 排序（ORDER BY = 排序 / ao de bai 奥得拜）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.4.1 | `select * from messages order by id desc` | desc=降序，最新的在前 |
| 2.4.2 | `select * from messages order by id asc` | asc=升序，最早的在前 |
| 2.4.3 | `select * from messages order by created_at desc` | 按发布时间倒序 |

### 2.5 限制条数（LIMIT = 限制 / li mi te 利米特）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.5.1 | `select * from messages limit 3` | 只看前3条 |
| 2.5.2 | `select * from messages order by id desc limit 5` | 按倒序再看前5条（最新5条） |
| 2.5.3 | `select * from messages limit 5 offset 10` | offset=跳过，跳过10条取5条 |

### 2.6 模糊搜索（LIKE = 模糊匹配 / lai ke 来科）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.6.1 | `select * from users where email like '%qq.com'` | %=任意字符，查 qq.com 结尾的 |
| 2.6.2 | `select * from messages where content like '%Python%'` | 查内容包含"Python"的 |
| 2.6.3 | `select * from users where email like 'alice%'` | 查以 alice 开头的 |

### 2.7 统计（COUNT = 计数 / kao en te 靠恩特）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.7.1 | `select count(*) from users` | 统计用户总数 |
| 2.7.2 | `select count(*) from messages` | 统计留言总数 |
| 2.7.3 | `select count(*) from users where role = 'admin'` | 统计管理员数量 |
| 2.7.4 | `select count(*) from messages where reply_to is not null` | 统计回复数量 |

### 2.8 分组统计（GROUP BY = 分组 / gu ru pu bai 古入普拜）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.8.1 | `select username, count(*) from messages group by username` | 每人发了几条留言 |
| 2.8.2 | `select role, count(*) from users group by role` | 每种角色有多少人 |

### 2.9 去重（DISTINCT = 不重复 / di si ting ke te 迪斯廷科特）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.9.1 | `select distinct username from messages` | 看哪些人发过留言（不重复） |
| 2.9.2 | `select distinct role from users` | 看有哪些角色 |

### 2.10 多重条件（AND = 并且, OR = 或者）

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.10.1 | `select * from messages where reply_to is not null and username = 'alice'` | alice 的回复 |
| 2.10.2 | `select * from users where role = 'admin' or role = 'user'` | 管理员或普通用户 |
| 2.10.3 | `select * from messages where username = 'alice' or username = 'bob'` | alice 或 bob 的留言 |

### 2.11 查看表结构

| 序号 | 命令 | 译文 |
|------|------|------|
| 2.11.1 | `pragma table_info(users)` | pragma=声明，看 users 有哪些列 |
| 2.11.2 | `pragma table_info(messages)` | 看 messages 有哪些列 |
| 2.11.3 | `select name from sqlite_master where type = 'table'` | 看数据库里有哪些表 |

---

## 三、增（INSERT = 插入 / yin se te 因瑟特）

### 3.1 插入用户

| 序号 | 命令 | 译文 |
|------|------|------|
| 3.1.1 | `insert into users (email, password, role) values ('new@qq.com', '123456', 'user')` | 新增一个用户 |

### 3.2 插入留言

| 序号 | 命令 | 译文 |
|------|------|------|
| 3.2.1 | `insert into messages (username, content, user_email) values ('new', '你好', 'new@qq.com')` | 发一条新留言 |
| 3.2.2 | `insert into messages (username, content, reply_to, user_email) values ('new', '回复', 1, 'new@qq.com')` | 回复 id=1 的留言 |

### 3.3 插入其他表

| 序号 | 命令 | 译文 |
|------|------|------|
| 3.3.1 | `insert into chat_messages (user_email, role, content, model) values ('test@qq.com', 'user', '你好', 'deepseek-v4-flash')` | 新增 AI 聊天记录 |
| 3.3.2 | `insert into user_config (email, api_key) values ('test@qq.com', 'sk-test')` | 新增 API Key |

---

## 四、改（UPDATE = 更新 / a pu dei te 阿普得特）

### 4.1 改角色

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.1.1 | `update users set role = 'admin' where email = 'user@qq.com'` | 把某用户设为管理员 |
| 4.1.2 | `update users set role = 'user' where email = 'admin@qq.com'` | 把某用户降为普通用户 |

### 4.2 改密码

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.2.1 | `update users set password = 'newpass123' where email = 'user@qq.com'` | 改密码 |

### 4.3 改留言

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.3.1 | `update messages set content = '新内容' where id = 1` | 改 id=1 的留言内容 |

### 4.4 改多个字段

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.4.1 | `update users set role = 'admin', password = 'admin123' where email = 'user@qq.com'` | 同时改角色和密码 |

### ⚠️ 注意

```sql
-- 正确：有 where，只改一条
update users set role = 'admin' where email = 'user@qq.com';

-- 危险：没有 where，所有用户都变成 admin！
update users set role = 'admin';
```

---

## 五、删（DELETE = 删除 / di li te 迪利特）

### 5.1 删留言

| 序号 | 命令 | 译文 |
|------|------|------|
| 5.1.1 | `delete from messages where id = 1` | 删 id=1 的留言 |
| 5.1.2 | `delete from messages where username = 'test'` | 删 test 的所有留言 |
| 5.1.3 | `delete from messages where user_email = 'test@qq.com'` | 删某人的所有留言 |

### 5.2 删用户

| 序号 | 命令 | 译文 |
|------|------|------|
| 5.2.1 | `delete from users where email = 'test@qq.com'` | 删某个用户 |

### 5.3 删聊天记录

| 序号 | 命令 | 译文 |
|------|------|------|
| 5.3.1 | `delete from chat_messages where user_email = 'test@qq.com'` | 删某人的所有聊天记录 |

### ⚠️ 注意

```sql
-- 正确：有 where
delete from messages where id = 1;

-- 危险：没有 where，全部留言删光！
delete from messages;
```

### 数据恢复

```bash
.\reset_data    -- 重新添加全部测试数据
```

---

## 六、完整练习流程

```
第 1 步：重置数据
  .\reset_data

第 2 步：查
  .\db "select * from users"
  .\db "select * from messages order by id desc limit 3"

第 3 步：增
  .\db "insert into messages (username, content, user_email) values ('我', '测试', 'me@qq.com')"

第 4 步：再查（确认加上了）
  .\db "select * from messages order by id desc limit 3"

第 5 步：改
  .\db "update messages set content = '修改了' where id = 1"

第 6 步：删
  .\db "delete from messages where id = 1"

第 7 步：重置再练
  .\reset_data
```

---

## 七、关键词速查

| 关键词 | 翻译 | 拼音 | 类别 |
|--------|------|------|------|
| `select` | 查询 | si lai ke te 斯莱科特 | 查 |
| `from` | 从 | fu rang mu 弗让姆 | 查 |
| `where` | 条件 | wei er 威尔 | 查/改/删 |
| `order by` | 排序 | ao de bai 奥得拜 | 查 |
| `desc` | 降序 | di shen ding 迪申丁 | 查 |
| `asc` | 升序 | ei sheng ke 埃升克 | 查 |
| `limit` | 限制 | li mi te 利米特 | 查 |
| `offset` | 跳过 | ao fu sai te 奥夫赛特 | 查 |
| `like` | 模糊 | lai ke 来科 | 查 |
| `count` | 计数 | kao en te 靠恩特 | 查 |
| `group by` | 分组 | gu ru pu bai 古入普拜 | 查 |
| `distinct` | 去重 | di si ting ke te 迪斯廷科特 | 查 |
| `and` | 并且 | an de 安德 | 查 |
| `or` | 或者 | ao 奥 | 查 |
| `is null` | 为空 | yi si na er 衣斯纳尔 | 查 |
| `is not null` | 不为空 | yi si nao te na er 衣斯闹特纳尔 | 查 |
| `insert into` | 插入到 | yin se te yin tu 因瑟特因图 | 增 |
| `values` | 值 | wai liu zi 外刘子 | 增 |
| `update` | 更新 | a pu dei te 阿普得特 | 改 |
| `set` | 设置 | sai te 赛特 | 改 |
| `delete` | 删除 | di li te 迪利特 | 删 |
| `pragma` | 声明 | pu ra ma 普拉玛 | 查结构 |
| `table_info` | 表信息 | tei bou yin fo 忒伯因佛 | 查结构 |
