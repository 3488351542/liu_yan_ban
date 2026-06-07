# PostgreSQL 命令大全

> PostgreSQL = 企业级数据库（pou si te gre si kiu er 剖斯特格雷斯奎尔）
> 运行：`psql -U postgres -d message_board` 进入命令行
> 文档适用于：留言板项目（project1_message_board）

---

## 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| PostgreSQL | pou si te gre si kiu er 剖斯特格雷斯奎尔 | 数据库名 |
| postgres | pou si te gre si 剖斯特格雷斯 | 默认用户名 |
| psql | pi si kiu er 皮斯奎尔 | 命令行工具 |
| localhost | lou ke ou hou si te 漏克欧候斯特 | 本机地址 |
| password | pa si wo de 帕斯沃得 | 密码 |
| database | da te bei si 达特贝斯 | 数据库 |
| table | tei bou 忒伯 | 表 |
| serial | sei rui ao 塞瑞奥 | 自增类型（PostgreSQL 版） |
| now | nao 闹 | 当前时间函数 |

---

## 一、连接 PostgreSQL

### 1.1 登录数据库

```bash
psql -U postgres
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `psql` | ✅ 固定 | PostgreSQL 命令行 | pi si kiu er 皮斯奎尔 |
| `-U` | ✅ 固定 | user = 用户名 | yo ze 优则 |
| `postgres` | ❌ 自定义 | 默认管理员账号 | pou si te gre si 剖斯特格雷斯 |

**会提示输入密码（安装时设的 123456）。**

### 1.2 指定数据库登录

```bash
psql -U postgres -d message_board
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `-d` | ✅ 固定 | database = 指定数据库 | da te bei si 达特贝斯 |
| `message_board` | ❌ 自定义 | 数据库名 | |

---

## 二、数据库管理

### 2.1 查看所有数据库

```sql
\l
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `\l` | list = 列表 | li si te 利斯特 |

### 2.2 创建数据库

```sql
CREATE DATABASE message_board;
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `CREATE (create)` | 创建 | ke rui ei te 克瑞埃特 |
| `DATABASE (database)` | 数据库 | da te bei si 达特贝斯 |

### 2.3 删除数据库

```sql
DROP DATABASE message_board;
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `DROP (drop)` | 删除（库/表） | dao pu 到普 |

### 2.4 切换数据库

```sql
\c message_board
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `\c` | connect = 连接 | ke nai ke te 科奈科特 |

### 2.5 查看当前连接的数据库

```sql
SELECT current_database();
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `current_database` (current_database) | 当前数据库 | ke ren te 科任特 / da te bei si 达特贝斯 |

---

## 三、表结构（留言板项目）

### 3.1 查看所有表

```sql
\dt
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `\dt` | display tables = 显示表 | tei bou er si 忒伯尔斯 |

### 3.2 查看表结构

```sql
\d users
\d messages
\d chat_messages
\d user_config
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `\d` | describe = 描述 | di si ke rai bu 迪斯克莱布 |

### 3.3 users — 用户表

```sql
\d users
```

| 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|
| `id` | 编号 | ai di 埃迪 | serial | 主键，自动增长 |
| `email` | 邮箱 | yi mei ou 伊梅欧 | text | 唯一，不能重复 |
| `password` | 密码 | pa si wo de 帕斯沃得 | text | 加密后的乱码 |
| `role` | 角色 | rou ou 肉欧 | text | 'admin' 或 'user' |
| `created_at` | 创建时间 | ke rui ei ti de ai te 克瑞埃提德埃特 | timestamp | 注册时间 |

### 3.4 messages — 留言表

```sql
\d messages
```

| 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|
| `id` | 编号 | ai di 埃迪 | serial | 主键 |
| `username` | 用户名 | yo ze nei mu 优则内姆 | text | 显示名字 |
| `content` | 内容 | ken ten te 肯ten特 | text | 留言内容 |
| `reply_to` | 回复给 | rui pu lai tu 瑞普来突 | integer | null=原始留言，数字=回复xx |
| `user_email` | 用户邮箱 | yo ze yi mei ou 优则伊梅欧 | text | 谁发的 |
| `created_at` | 创建时间 | ke rui ei ti de ai te 克瑞埃提德埃特 | timestamp | 发布时间 |

### 3.5 chat_messages — AI 聊天表

```sql
\d chat_messages
```

| 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|
| `id` | 编号 | ai di 埃迪 | serial | 主键 |
| `user_email` | 用户邮箱 | yo ze yi mei ou 优则伊梅欧 | text | 谁的对话 |
| `role` | 角色 | rou ou 肉欧 | text | 'user'或'assistant' |
| `content` | 内容 | ken ten te 肯ten特 | text | 具体内容 |
| `reasoning` | 推理 | rui ze ning 瑞泽宁 | text | 深度思考过程 |
| `model` | 模型 | mao dou 茅斗 | text | AI 模型名 |
| `created_at` | 创建时间 | ke rui ei ti de ai te 克瑞埃提德埃特 | timestamp | 发言时间 |

### 3.6 user_config — 用户配置表

```sql
\d user_config
```

| 列名 | 翻译 | 拼音 | 类型 | 说明 |
|------|------|------|------|------|
| `email` | 邮箱 | yi mei ou 伊梅欧 | text | 主键 |
| `api_key` | API密钥 | ei pi ai ki 埃皮埃奇 | text | DeepSeek API Key |

### 3.7 SQLite vs PostgreSQL 建表区别

```sql
-- SQLite（旧）写法：
id integer primary key autoincrement,

-- PostgreSQL（新）写法：
id serial primary key,
```

| 对比 | SQLite | PostgreSQL |
|------|--------|------------|
| 自增 | `autoincrement` | `serial` |
| 占位符 | `?` | `%s` |
| 查版本 | `select sqlite_version()` | `select version()` |

---

## 四、查（SELECT (select) = 查询 / si lai ke te 斯莱科特）

> 先在 psql 里连接数据库：`psql -U postgres -d message_board`
> 然后直接输入 SQL，结尾加分号 `;`

### 4.1 基本查询

| 序号 | 命令 | 翻译 | 说明 |
|------|------|------|------|
| 4.1.1 | `select * from users;` | select=查询, from=从, *=所有 | 查所有用户 |
| 4.1.2 | `select * from messages;` | messages=留言表 | 查所有留言 |
| 4.1.3 | `select * from chat_messages;` | chat=聊天 | 查所有聊天记录 |
| 4.1.4 | `select * from user_config;` | config=配置 | 查 API Key |

### 4.2 指定列

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.2.1 | `select email, role from users;` | 只看邮箱和角色 |
| 4.2.2 | `select id, username, content from messages;` | 只看编号、用户名、内容 |
| 4.2.3 | `select username, content from messages limit 3;` | 只看前3条的用户名和内容 |

### 4.3 条件筛选（WHERE (where) = 哪里 / wei er 威尔）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.3.1 | `select * from users where role = 'admin';` | role=角色，查管理员 |
| 4.3.2 | `select * from users where role = 'user';` | 查普通用户 |
| 4.3.3 | `select * from messages where username = 'alice';` | 查 alice 的留言 |
| 4.3.4 | `select * from messages where reply_to is null;` | is null=为空，只查原始留言 |
| 4.3.5 | `select * from messages where reply_to is not null;` | is not null=不为空，只查回复 |

### 4.4 排序（ORDER BY (order by) = 排序 / ao de bai 奥得拜）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.4.1 | `select * from messages order by id desc;` | desc=降序，最新的在前 |
| 4.4.2 | `select * from messages order by id asc;` | asc=升序，最早的在前 |
| 4.4.3 | `select * from messages order by created_at desc;` | 按发布时间倒序 |

### 4.5 限制条数（LIMIT (limit) = 限制 / li mi te 利米特）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.5.1 | `select * from messages limit 3;` | 只看前3条 |
| 4.5.2 | `select * from messages order by id desc limit 5;` | 看最新5条 |
| 4.5.3 | `select * from messages limit 5 offset 10;` | offset=跳过，跳过10条取5条 |

**LIMIT (limit) vs OFFSET (offset)：**

```
跳过10条 → 取5条
           ┌──────────────────┐
第1-10条   │ 跳过              │
第11-15条  │ 取出来 ✅          │
第16条...  │ 后面的不管          │
           └──────────────────┘
```

### 4.6 模糊搜索（LIKE (like) = 模糊匹配 / lai ke 来科）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.6.1 | `select * from users where email like '%qq.com';` | %=任意字符，查 qq.com 结尾的 |
| 4.6.2 | `select * from messages where content like '%Python%';` | 查内容包含"Python"的 |
| 4.6.3 | `select * from users where email like 'alice%';` | 查以 alice 开头的 |

**PostgreSQL 额外支持 ILIKE（不分大小写）：**

```sql
-- LIKE：区分大小写
select * from users where email like '%@QQ.COM';     -- 查不到（小写 qq.com 才匹配）

-- ILIKE：不区分大小写（PostgreSQL 特有）
select * from users where email ilike '%@QQ.COM';    -- 能查到 ✅
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `ILIKE (ilike)` | ✅ 固定 | 不区分大小写匹配 | ai lai ke 埃来科 |

### 4.7 统计（COUNT (count) = 计数 / kao en te 靠恩特）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.7.1 | `select count(*) from users;` | 统计用户总数 |
| 4.7.2 | `select count(*) from messages;` | 统计留言总数 |
| 4.7.3 | `select count(*) from users where role = 'admin';` | 统计管理员数量 |
| 4.7.4 | `select count(*) from messages where reply_to is not null;` | 统计回复数量 |

### 4.8 分组统计（GROUP BY (group by) = 分组 / gu ru pu bai 古入普拜）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.8.1 | `select username, count(*) from messages group by username;` | 每人发了几条留言 |
| 4.8.2 | `select role, count(*) from users group by role;` | 每种角色有多少人 |

### 4.9 去重（DISTINCT (distinct) = 不重复 / di si ting ke te 迪斯廷科特）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.9.1 | `select distinct username from messages;` | 看哪些人发过留言（不重复） |
| 4.9.2 | `select distinct role from users;` | 看有哪些角色 |

### 4.10 多重条件（AND (and) = 并且 / an de 安德, OR (or) = 或者 / ao 奥）

| 序号 | 命令 | 译文 |
|------|------|------|
| 4.10.1 | `select * from messages where reply_to is not null and username = 'alice';` | alice 的回复 |
| 4.10.2 | `select * from users where role = 'admin' or role = 'user';` | 管理员或普通用户 |
| 4.10.3 | `select * from messages where username = 'alice' or username = 'bob';` | alice 或 bob 的留言 |

### 4.11 范围查询（IN (in) / BETWEEN (between) / 大小比较）

```sql
-- IN = 在列表里
select * from users where email in ('alice@qq.com', 'bob@qq.com');

-- BETWEEN = 在范围内
select * from messages where id between 5 and 10;

-- 大小比较
select * from messages where id > 10;          -- 大于
select * from messages where id >= 10;         -- 大于等于
select * from messages where id < 5;           -- 小于
select * from messages where id != 10;         -- 不等于
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `IN (in)` | 在...里 | yin 因 |
| `BETWEEN (between)` | 在...之间 | bi twi en 比推恩 |
| `>` | 大于 | |
| `<` | 小于 | |
| `!=` | 不等于 | |
| `>=` | 大于等于 | |
| `<=` | 小于等于 | |

---

## 五、增（INSERT (insert) = 插入 / yin se te 因瑟特）

### 5.1 插入用户

```sql
insert into users (email, password, role) values ('new@qq.com', '123456', 'user');
```

### 5.2 插入留言

```sql
-- 发一条新留言
insert into messages (username, content, user_email) values ('new', '你好', 'new@qq.com');

-- 回复 id=1 的留言
insert into messages (username, content, reply_to, user_email) values ('new', '回复', 1, 'new@qq.com');
```

### 5.3 插入其他表

```sql
-- 新增 AI 聊天记录
insert into chat_messages (user_email, role, content, model) values ('test@qq.com', 'user', '你好', 'deepseek-v4-flash');

-- 新增 API Key
insert into user_config (email, api_key) values ('test@qq.com', 'sk-test');
```

### 5.4 插入冲突处理（PostgreSQL 特有）

```sql
-- 如果有冲突（email重复），不报错也不做任何事
insert into users (email, password) values ('alice@qq.com', '123')
    on conflict (email) do nothing;

-- 如果有冲突，更新密码（UPSERT = 插入或更新）
insert into users (email, password) values ('alice@qq.com', 'newpass')
    on conflict (email) do update set password = excluded.password;
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `ON CONFLICT (on conflict)` | 当冲突时 | on ken fu li ke te 昂肯弗利科特 |
| `DO NOTHING (do nothing)` | 什么都不做 | |
| `DO UPDATE (do update)` | 执行更新 | |
| `excluded` | 被排除的值（指你试图插入的新值） | ek si klu ti de 埃斯克卢提得 |

---

## 六、改（UPDATE (update) = 更新 / a pu dei te 阿普得特）

### 6.1 改角色

```sql
-- 把某用户设为管理员
update users set role = 'admin' where email = 'user@qq.com';

-- 把某用户降为普通用户
update users set role = 'user' where email = 'admin@qq.com';
```

### 6.2 改密码

```sql
update users set password = 'newpass123' where email = 'user@qq.com';
```

### 6.3 改留言

```sql
update messages set content = '新内容' where id = 1;
```

### 6.4 改多个字段

```sql
-- 同时改角色和密码
update users set role = 'admin', password = 'admin123' where email = 'user@qq.com';
```

### 6.5 带条件更新的缩写

```sql
-- 更新并返回被改的数据（PostgreSQL 特有！）
update users set role = 'admin' where email = 'user@qq.com' returning *;

-- 只返回指定列
update users set role = 'admin' where email = 'user@qq.com' returning email, role;
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `RETURNING (returning)` | 返回 | rui te ning 瑞特宁 |

### ⚠️ 注意

```sql
-- 正确：有 where，只改一条
update users set role = 'admin' where email = 'user@qq.com';

-- 危险：没有 where，所有用户都变成 admin！
update users set role = 'admin';
```

---

## 七、删（DELETE (delete) = 删除 / di li te 迪利特）

### 7.1 删留言

```sql
delete from messages where id = 1;
delete from messages where username = 'test';
delete from messages where user_email = 'test@qq.com';
```

### 7.2 删用户

```sql
delete from users where email = 'test@qq.com';
```

### 7.3 删聊天记录

```sql
delete from chat_messages where user_email = 'test@qq.com';
```

### 7.4 删除并返回（PostgreSQL 特有）

```sql
delete from messages where id = 1 returning *;
```

### 7.5 清空表（TRUNCATE (truncate) = 截断 / te rang kei te 特朗科特）

```sql
-- DELETE 逐行删，慢，但可以配合 where
delete from messages;

-- TRUNCATE 瞬间清空整张表，更快，不能加 where
truncate table messages;
```

| 对比 | DELETE | TRUNCATE |
|------|--------|----------|
| 速度 | 慢（逐行删） | 快（瞬间） |
| WHERE | ✅ 可以加条件 | ❌ 不能加 |
| 自增ID | 不重置 | 重置 |

### ⚠️ 注意

```sql
-- 正确：有 where
delete from messages where id = 1;

-- 危险：没有 where，全部留言删光！
delete from messages;
```

---

## 八、高级查询

### 8.1 表连接（JOIN (join) = 连接 / jion 照因）

```sql
-- 查留言时带上留言者的邮箱和角色
select messages.*, users.role
from messages
join users on messages.user_email = users.email;
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `JOIN (join)` | 连接 | jion 照因 |
| `ON (on)` | 匹配条件 | on 昂 |

### 8.2 子查询

```sql
-- 查发了留言的用户（子查询）
select * from users where email in (
    select distinct user_email from messages where user_email is not null
);
```

### 8.3 聚合函数

```sql
select count(*) from messages;           -- 总数
select max(id) from messages;            -- 最大 id
select min(id) from messages;            -- 最小 id
select avg(id) from messages;            -- 平均 id（平均编号）
select sum(id) from messages;            -- id 总和
```

| 函数 | 翻译 | 拼音 |
|------|------|------|
| `MAX (max)` | 最大值 | mai ke si 麦克斯 |
| `MIN (min)` | 最小值 | min 民 |
| `AVG (avg)` | 平均值 | ei vi ji 埃维基 |
| `SUM (sum)` | 总和 | sa mu 萨姆 |

---

## 九、PostgreSQL 特有函数

### 9.1 时间相关

```sql
select now();                              -- 当前时间
select current_date;                       -- 当前日期
select current_time;                       -- 当前时间
select extract(year from now());           -- 提取年份
select age(timestamp '2024-01-01');        -- 计算距今多久
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `now()` | 当前时间 | nao 闹 |
| `current_date` | 当前日期 | ke ren te dei te 科任特嘚特 |
| `extract` | 提取 | ek si te ai ke te 埃克斯忒科特 |
| `age()` | 年龄 | ei zhi 埃之 |

### 9.2 字符串相关

```sql
select upper(email) from users;            -- 转大写
select lower(email) from users;            -- 转小写
select length(content) from messages;      -- 字符串长度
select substring(content, 1, 10) from messages;     -- 截取前10个字
select concat(username, ': ', content) from messages; -- 拼接字符串
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `upper` | 大写 | a po 阿波 |
| `lower` | 小写 | lou er 漏尔 |
| `length` | 长度 | leng ke si 棱克斯 |
| `substring` | 截取 | sa bu si te rui en 萨布斯特瑞恩 |
| `concat` | 拼接 | ken kai te 肯开特 |

### 9.3 类型转换

```sql
-- 字符串转整数
select '123'::integer;

-- 整数转字符串
select 123::text;

-- 时间转字符串
select now()::text;
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `::` | 类型转换（PostgreSQL 特有语法） | |

### 9.4 COALESCE (coalesce)（处理空值 / kou e les 扣额勒斯）

```sql
-- SQLite 用 ifnull
-- ifnull(reply_to, 0)

-- PostgreSQL 用 coalesce（可以接多个参数）
select coalesce(reply_to, 0) from messages;           -- 如果 reply_to 是空，显示 0
select coalesce(reasoning, '无深度思考') from messages; -- 如果 reasoning 是空，显示"无深度思考"
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `COALESCE (coalesce)` | 合并 | kou e les 扣额勒斯 |

---

## 十、psql 常用命令（元命令）

| 命令 | 翻译 | 拼音 | 作用 |
|------|------|------|------|
| `\l` | list | li si te 利斯特 | 查看所有数据库 |
| `\c 库名` | connect | ke nai ke te 科奈科特 | 切换数据库 |
| `\dt` | display tables | tei bou er si 忒伯尔斯 | 查看所有表 |
| `\d 表名` | describe | di si ke rai bu 迪斯克莱布 | 查看表结构 |
| `\du` | display users | yo ze si 优则斯 | 查看所有用户 |
| `\di` | display indexes | yin dai ke si 因戴克斯 | 查看所有索引 |
| `\q` | quit | kui te 奎特 | 退出 psql |
| `\?` | help | hai er pu 海尔普 | 查看所有 psql 命令 |
| `\!` | shell |  | 临时执行系统命令（如 `\! cls`） |
| `\x` | expanded |  | 切换竖排显示（数据列太多时用） |
| `\timing` | timing | tai ming 太明 | 显示每条 SQL 执行时间 |

### \x 竖排显示示例

```sql
-- 当一行太长时，用 \x 切换显示模式
\x on
select * from users where email = 'alice@qq.com';
```

显示效果：
```
-[ RECORD 1 ]----------
email     | alice@qq.com
password  | 加密的乱码
role      | user
created_at| 2026-01-01 12:00:00
```

---

## 十一、PostgreSQL 数据类型

| 类型 | 翻译 | 拼音 | 说明 | 举例 |
|------|------|------|------|------|
| `serial` | 自增 | sei rui ao 塞瑞奥 | 整数自动增长，替代 autoincrement | `id serial primary key` |
| `integer` | 整数 | yin te zhi 因特之 | 普通整数 | `reply_to integer` |
| `text` | 文本 | tai ke si te 太科斯特 | 不限长度字符串 | `content text` |
| `boolean` | 布尔 | bo li en 伯利恩 | true/false | `is_admin boolean default false` |
| `timestamp` | 时间戳 | tai mu si tai mu pu 太姆斯太姆普 | 日期+时间 | `created_at timestamp` |
| `date` | 日期 | dei te 嘚特 | 只有日期 | `birthday date` |
| `json` | JSON | jei sen 杰森 | JSON 数据 | `metadata json` |
| `jsonb` | JSON二进制 | jei sen bi 杰森比 | 更快的 JSON（可索引） | `data jsonb` |

---

## 十二、关键词速查

| 关键词 | 翻译 | 拼音 | 类别 |
|--------|------|------|------|
| `SELECT (select)` | 查询 | si lai ke te 斯莱科特 | 查 |
| `FROM (from)` | 从 | fu rang mu 弗让姆 | 查 |
| `WHERE (where)` | 条件 | wei er 威尔 | 查/改/删 |
| `ORDER BY (order by)` | 排序 | ao de bai 奥得拜 | 查 |
| `DESC (desc)` | 降序 | di shen ding 迪申丁 | 查 |
| `ASC (asc)` | 升序 | ei sheng ke 埃升克 | 查 |
| `LIMIT (limit)` | 限制 | li mi te 利米特 | 查 |
| `OFFSET (offset)` | 跳过 | ao fu sai te 奥夫赛特 | 查 |
| `LIKE (like)` | 模糊匹配 | lai ke 来科 | 查 |
| `ILIKE (ilike)` | 不区分大小写 | ai lai ke 埃来科 | 查 |
| `COUNT (count)` | 计数 | kao en te 靠恩特 | 查 |
| `GROUP BY (group by)` | 分组 | gu ru pu bai 古入普拜 | 查 |
| `DISTINCT (distinct)` | 去重 | di si ting ke te 迪斯廷科特 | 查 |
| `AND (and)` | 并且 | an de 安德 | 查 |
| `OR (or)` | 或者 | ao 奥 | 查 |
| `IS NULL (is null)` | 为空 | yi si na er 衣斯纳尔 | 查 |
| `IS NOT NULL (is not null)` | 不为空 | yi si nao te na er 衣斯闹特纳尔 | 查 |
| `IN (in)` | 在列表里 | yin 因 | 查 |
| `BETWEEN (between)` | 在范围 | bi twi en 比推恩 | 查 |
| `INSERT INTO (insert into)` | 插入到 | yin se te yin tu 因瑟特因图 | 增 |
| `VALUES (values)` | 值 | wai liu zi 外刘子 | 增 |
| `ON CONFLICT (on conflict)` | 冲突时 | on ken fu li ke te 昂肯弗利科特 | 增/改 |
| `RETURNING (returning)` | 返回 | rui te ning 瑞特宁 | 增/改/删 |
| `UPDATE (update)` | 更新 | a pu dei te 阿普得特 | 改 |
| `SET (set)` | 设置 | sai te 赛特 | 改 |
| `DELETE (delete)` | 删除 | di li te 迪利特 | 删 |
| `TRUNCATE (truncate)` | 截断 | te rang kei te 特朗普科特 | 删 |
| `JOIN (join)` | 连接 | jion 照因 | 查（高级） |
| `COALESCE (coalesce)` | 合并空值 | kou e les 扣额勒斯 | 函数 |
| `NOW() (now())` | 当前时间 | nao 闹 | 函数 |
| `SERIAL (serial)` | 自增 | sei rui ao 塞瑞奥 | 类型 |

---

## 十三、SQLite vs PostgreSQL 区别速查

| 功能 | SQLite | PostgreSQL |
|------|--------|------------|
| **自增** | `id integer primary key autoincrement` | `id serial primary key` |
| **占位符** | `?` | `%s` |
| **空值处理** | `ifnull(列, 默认值)` | `coalesce(列, 默认值)` |
| **当前时间函数** | `datetime('now')` | `now()` |
| **插入冲突** | `insert or ignore` | `on conflict do nothing` |
| **插入或替换** | `insert or replace` | `on conflict do update set ...` |
| **查看表** | `.tables` | `\dt` |
| **查看结构** | `pragma table_info(表名)` | `\d 表名` |
| **模糊匹配不区分大小写** | 不支持（需要 like + lower） | `ilike` |
| **更新/删除返回数据** | 不支持 | `returning *` |
| **系统信息** | PostgreSQL 有自己的系统视图 | `\l` 查看数据库列表 |
