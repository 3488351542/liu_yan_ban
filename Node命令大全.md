# Node.js 命令大全

> Node.js = JavaScript 运行环境（nao dou jie si 闹斗杰斯）
> npm = Node Package Manager = 包管理器（en pi em 恩皮埃姆）
> npx = Node Package Execute = 包执行器（en pi ke si 恩皮克斯）

### 例子中出现的单词发音

| 英文 | 拼音 | 中文 |
|------|------|------|
| app | ai pu 爱普 | 应用 |
| server | se ve 瑟沃 | 服务器 |
| build | bi er de 比尔德 | 构建 |
| dev | di wei 迪维 | 开发 |
| start | si da te 斯达特 | 启动 |
| hello | ha lou 哈漏 | 你好 |
| my-app | mai ai pu 迈爱普 | 我的应用 |
| my-project | mai pu ruo jie ke te 迈普若杰克特 | 我的项目 |
| express | yi ke si pu re si 伊克斯普瑞斯 | Web框架 |
| jest | jie si te 杰斯特 | 测试工具 |
| react | rui ai ke te 瑞埃克特 | React前端库 |
| ejs | yi jie si 伊杰斯 | 模板引擎 |
| nodemon | nao de men 闹德门 | 自动重启工具 |
| gulp | ga er pu 嘎尔普 | 构建工具 |
| modules | mao dou er si 冒斗尔斯 | 模块 |
| lock | lao ke 涝克 | 锁定 |

---

## 一、Node.js 基础

### 1.1 node — 运行 JavaScript 文件

```bash
node 文件名.js
node app.js
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `node` | ✅ **固定** | Node.js 运行命令 | nao de 闹德 |
| `文件名.js` | ❌ **自定义** | 你要运行的 JS 文件 | |
| `.js` | ✅ **固定** | JavaScript 文件后缀 | jie si 杰斯 |

**例子：**

| 你要做什么 | 命令 |
|-----------|------|
| 运行 app.js | `node app.js` |
| 运行 server.js | `node server.js` |

---

### 1.2 node -v — 查看版本

```bash
node -v
node --version
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `-v` | ✅ **固定** | version = 版本 | ve shen 沃申 |
| `--version` | ✅ **固定** | 版本（完整写法） | |

**例子：** `node -v` → 输出 `v22.14.0`

---

### 1.3 交互模式（REPL）

```bash
node
```

直接输入 `node` 回车，进入交互模式，可以一行行写 JS：

```
> 1 + 1
2
> console.log("hello")
hello
> .exit    ← 退出
```

| 参数 | 翻译 | 拼音 |
|------|------|------|
| `.exit` | 退出交互模式 | yi ke si te 伊科斯特 |
| `console.log` | 控制台输出 | ken sou log 肯搜涝格 |

---

## 二、npm — 包管理

> npm = Node Package Manager = 包管理器（en pi em 恩皮埃姆）
> package = 包（pai ke ji 派克及）
> manager = 管理器（mai ni zhe 麦尼者）

### 2.1 npm init — 初始化项目（创建 package.json）

```bash
npm init
npm init -y
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `init` | ✅ **固定** | initialize = 初始化 | i ni she lai zi 伊尼舍来子 |
| `-y` | ✅ **固定** | yes = 全部默认（跳过提问） | ye si 耶斯 |

**作用：** 创建 `package.json` 文件

---

### 2.2 npm install — 安装依赖

```bash
npm install 包名
npm install 包名@版本
npm i 包名
npm i express              # express = Web框架（yi ke si pu re si 伊克斯普瑞斯）
npm i express@4.18.0       # 装指定版本
npm i react react-dom      # 一次性装多个
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `install` | ✅ **固定** | 安装 | in si tao er 因斯掏尔 |
| `i` | ✅ **固定** | install 简写 | |
| `包名` | ❌ **自定义** | 你要装的库名 | `express` |
| `@版本` | ✅ **固定** | at = 指定版本号 | ai te 埃特 |

**安装后发生了什么：**
```
项目文件夹/
├── node_modules/    ← modules = 模块（mao dou er 冒斗尔）
├── package.json     ← 记录装了哪些包
└── package-lock.json ← lock = 锁定记录具体版本
```

---

### 2.3 npm install -g — 全局安装

```bash
npm install -g 包名
npm install -g @openai/codex    # codex = AI编程工具（kou dai ke si 寇代克斯） CLI = 命令行工具（xi li ai 希利埃）
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `-g` | ✅ **固定** | global = 全局 | glou bo 格娄伯 |

**区别：**
```
不加 -g：装在当前项目文件夹，只在这个项目里能用
加   -g：装在系统里，所有地方都能用
```

---

### 2.4 npm install --save-dev — 开发依赖

```bash
npm install 包名 --save-dev
npm install 包名 -D
npm i jest -D              # jest = 测试工具（jie si te 杰斯特） -D = 开发依赖
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `--save-dev` | ✅ **固定** | save dev = 保存为开发依赖 | sei fu dai fu 塞夫代夫 |
| `-D` | ✅ **固定** | --save-dev 简写 | di 迪 |

**区别：**
```
普通依赖：项目上线也需要（如 express、react）
开发依赖：只在写代码时用，上线不需要（如 测试工具）
```

---

### 2.5 npm uninstall — 卸载包

```bash
npm uninstall 包名
npm un 包名
npm un gulp                # 卸载 gulp
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `uninstall` | ✅ **固定** | 卸载 | an in si tao er 安因斯掏尔 |
| `un` | ✅ **固定** | uninstall 简写 | an 安 |

---

### 2.6 npm update — 更新包

```bash
npm update 包名             # 更新指定包
npm update                 # 更新所有包
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `update` | ✅ **固定** | 更新 | a pu dei te 阿普得特 |

---

### 2.7 npm list — 查看已安装的包

```bash
npm list                   # 查看当前项目装的包
npm list -g                # 查看全局装的包
npm list --depth=0         # 只看顶层，不看依赖的依赖
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `list` | ✅ **固定** | 列表 | li si te 利斯特 |
| `--depth=0` | ✅ **固定** | depth = 层级，0=只看直接依赖 | dai pu si 代普斯 |

---

### 2.8 npm run — 运行脚本

```bash
npm run 脚本名
npm run dev                # 运行 dev 脚本
npm run build              # 运行 build 脚本
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `run` | ✅ **固定** | 运行 | ran 软 |
| `脚本名` | ❌ **自定义** | 你在 package.json 里定义的名字 | |
| `dev` | ❌ **自定义** | development = 开发模式 | di wei 迪维 |
| `build` | ❌ **自定义** | 构建 / 打包 | bi er de 比尔德 |

**脚本定义在 package.json 里：**

```json
{
  "scripts": {
    "dev": "node app.js",
    "build": "node build.js"
  }
}
```

---

### 2.9 常用 npm 简写

| 完整命令 | 简写 | 翻译 |
|---------|------|------|
| `npm install` | `npm i` | 安装 |
| `npm uninstall` | `npm un` | 卸载 |
| `npm --save-dev` | `npm -D` | 开发依赖 |
| `npm --global` | `npm -g` | 全局 |

---

## 三、npx — 临时运行

> npx = Node Package Execute = 包执行器（en pi ke si 恩皮克斯）
> execute = 执行（ai ke si kiu te 埃克斯求特）

### 3.1 npx — 直接运行

```bash
npx 包名
npx 包名 参数          # 参数是传给包的，不是传给 npx 的
npx --help             # help = 查看帮助（hai er pu 海尔普）
npx --version          # version = 查看版本（ve shen 沃申）

npx create-react-app my-app    # create-react-app = React项目模板
npx next dev                   # next = Next.js框架（nai ke si te 奈科斯特）
npx cowsay "hello"             # cowsay = 会说话的牛（kao sei 靠赛） hello = 你好（ha lou 哈漏）
npx skills add https://...     # skills = 技能工具，add = 添加（该工具的自己的参数）
```

| 参数 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `npx` | ✅ **固定** | Node 包执行器 | en pi ke si 恩皮克斯 |
| `包名` | ❌ **自定义** | 你要用的工具 | |
| `参数` | ❌ **自定义** | 传给工具的参数（不是npx的参数） | |

**npx vs npm install 的区别：**

```bash
# npm：先装再用
npm install -g create-react-app
create-react-app my-app

# npx：一步到位，用完自动删
npx create-react-app my-app
```

**npx 的好处：**
- 不用全局安装一大堆工具
- 每次用都是最新版本
- 用完自动清理

---

## 四、package.json — 项目配置文件

> package = 包（pai ke ji 派克及）
> json = JavaScript Object Notation = JSON格式（jie sen 杰森）

### 4.1 package.json 结构

```json
{
  "name": "my-project",          // name = 项目名（自定义）
  "version": "1.0.0",            // version = 版本号（自定义）
  "description": "我的项目",      // description = 描述（自定义）
  "main": "app.js",              // main = 入口文件（自定义）
  "scripts": {                   // scripts = 脚本（si ke rui pu ci 斯科瑞普次）
    "dev": "node app.js",        // dev = development = 开发（di wei 迪维）
    "start": "node app.js"       // start = 启动（si da te 斯达特）
  },
  "dependencies": {              // dependencies = 生产依赖（di pao den xi si 迪抛登西斯）
    "express": "^4.18.0"
  },
  "devDependencies": {           // devDependencies = 开发依赖（di wei di pao den xi si 迪维迪抛登西斯）
    "jest": "^29.0.0"
  }
}
```

| 字段 | 固定/自定义 | 翻译 | 拼音 |
|------|-----------|------|------|
| `name` | ❌ **自定义** | 项目名 | nei mu 内姆 |
| `version` | ❌ **自定义** | 版本号 | ve shen 沃申 |
| `description` | ❌ **自定义** | 描述 | di si ke rui pu shen 迪斯科瑞普申 |
| `main` | ❌ **自定义** | 入口文件 | mei yin 梅因 |
| `scripts` | ❌ **自定义** | 可运行的脚本 | si ke rui pu ci 斯科瑞普次 |
| `dependencies` | ✅ **固定** | 生产依赖 | di pao den xi si 迪抛登西斯 |
| `devDependencies` | ✅ **固定** | 开发依赖 | di wei di pao den xi si 迪维迪抛登西斯 |
| `json` | ✅ **固定** | JSON 格式 | jie sen 杰森 |

---

## 五、日常完整流程

### 5.1 新建一个 Node.js 项目

```bash
mkdir my-project          # mkdir = 创建文件夹
cd my-project             # cd = 进入文件夹
npm init -y               # init = 初始化，-y = 全部默认
npm i express             # i = install = 安装
node app.js               # node = 运行 JS 文件
```

### 5.2 日常开发

```bash
npm install                # 根据 package.json 装所有依赖
npm run dev                # run = 运行，dev = 开发模式
npm run build              # build = 打包构建
```

### 5.3 装包常用命令

```bash
npm i express                       # 装一个包
npm i express ejs                   # 装多个包
npm i -D jest                       # -D = 开发依赖
npm i -g nodemon                    # -g = 全局安装
npm un express                      # un = uninstall = 卸载
npm update                          # update = 更新
npm list --depth=0                  # list = 列表
```

---

## 六、命令速查表

| 命令 | 翻译 | 拼音 | 用途 |
|------|------|------|------|
| `node -v` | Node 版本 | - | 看 Node 版本 |
| `node 文件.js` | 运行文件 | - | 运行 JS 文件 |
| `npm init -y` | 初始化 | i ni she lai zi 伊尼舍来子 | 创建 package.json |
| `npm i 包` | 安装 | in si tao er 因斯掏尔 | 装依赖 |
| `npm i -g 包` | 全局安装 | glou bo 格娄伯 | 装到系统全局 |
| `npm i -D 包` | 开发依赖 | di wei 迪维 | 只在开发用 |
| `npm un 包` | 卸载 | an in si tao er 安因斯掏尔 | 删掉包 |
| `npm update` | 更新 | a pu dei te 阿普得特 | 升级包 |
| `npm list` | 列表 | li si te 利斯特 | 看装了啥 |
| `npm run 名` | 运行脚本 | ran 软 | 运行自定义命令 |
| `npx 包` | 临时运行 | en pi ke si 恩皮克斯 | 用一次就删 |
