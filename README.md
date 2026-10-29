# agent-team

让 AI 把活拆给**有名字的成员**，而不是派一个你看不见过程的黑盒代理。

一个 WorkBuddy 技能。装好之后，遇到能并行的任务，AI 会自己建团队、给每个成员起名派工，你在侧边栏看着它们各干各的。

> 只支持 WorkBuddy。五步流程绑的是它的团队工具，别的工具没有同名能力。

---

## 为什么要有它

AI 编程工具里的「分工」通常是这样的：你让它查三件事，它派出三个子代理，你屏幕上只剩三张转圈的状态卡片。它们读了哪些文件、跑到哪一步、是不是已经跑偏了，你一概不知道。等它回来，你才看到结果——对或者不对，都只能接受。

团队模式是同一个动作的另一种做法：

| | 子代理 | 团队 |
|---|---|---|
| 你能看到什么 | 一张状态卡片 | 每个成员的名字、任务、当前动作 |
| 成员之间 | 互不相识 | 共享任务列表，能互相发消息 |
| 跑偏的时候 | 跑完才知道 | 中途就能看见 |

默认往往是第一种。省事，但对使用者不透明。这个技能改的是这个默认。

## 安装

把仓库克隆成技能目录下的一个文件夹。

```bash
git clone https://github.com/eggacheb/agent-team-skill.git ~/.workbuddy/skills/agent-team
```

Windows 上 `~` 是 `C:\Users\<你的名字>`。

只想给某一个项目用的话，把路径换成那个项目里的 `.workbuddy/skills/agent-team`，提交进版本库，同事拉下来就有。

### 让 AI 自己装

不想碰命令行，把下面整段丢给你的 AI：

```
帮我装一个 WorkBuddy 技能。

仓库：https://github.com/eggacheb/agent-team-skill

1. 克隆到技能目录，目录名用 agent-team：
   git clone https://github.com/eggacheb/agent-team-skill.git ~/.workbuddy/skills/agent-team
2. 读一遍里面的 SKILL.md，确认 frontmatter 的 name 和 description 都在。
3. 装完告诉我：它在什么情况下会被触发，你自己会怎么用它。
```

## 它为什么会自己触发

技能有两种装法，区别只在 `description`：

| | 模型触发（本仓库） | 只有手打 |
|---|---|---|
| 怎么开始 | AI 自己判断该用就用 | 你打 `/agent-team` |
| 上下文成本 | 每条消息都带着一行 description | 零 |
| 适合 | 希望它「想起来就用」 | 偶尔用一次、想完全掌控 |

这个技能用的是前者。`description` 常驻在每一轮上下文里，AI 拿它跟手上的活比对，命中就去读正文。所以你不用打命令，也不用说「用团队」。

触发词是 description 的最后半句：**「要派子代理时先读这一条」**。它卡的是一个具体时刻——AI 决定「这件事要不要派出去做」的那一瞬。少了这半句，技能容易被当成又一条背景说明，读到也未必想起来。

### 怎么验

装完问它一句「把 A 模块和 B 模块各查一遍」。预期是它**自己建团队、贴出一张成员表**，而不是直接闷头干活。

注意能验的和不能验的：装好当次就能确认它**加载得起来**，但「会不会被触发」要等一个真的能裂开的任务，当场验不了。

### 没触发怎么办

改 `description`，别改正文。正文只在触发之后才被读到，改了不解决问题。

两件事按顺序试：

- 把最后那半句往前挪，放到最前面
- 加上你实际会说的词。比如你常说「这几个模块分别看看」，就把这句加进去

改完重启会话，再问一次那个能触发的问题。

### 想改成只有手打

在 frontmatter 里加一行：

```yaml
disable-model-invocation: true
```

之后只有打 `/agent-team` 才会加载。上下文成本归零，代价是你得记得它存在。

## 什么时候用，什么时候不用

这是整个技能里最要紧的部分。**大多数任务不需要团队。**

建团队的前提是任务能裂成**两条以上互不依赖的线**，且每条都要真读代码、真翻文档。判据是独立性：两条线能不能同时开工、互不等待。

不建的情况：

- **一条线**，哪怕很长——自己做
- **几条线但每条一两分钟**（改配置、查符号）——自己做更快
- **前后强依赖**（B 必须等 A 的结论）——这是流水线，不是并行
- **纯对话、纯解释**

没有这道门槛的技能会把「改一行配置」也做成一场三幕剧：建团队、发三张票、收三份报告。那比黑盒更烦人。

## 它让 AI 做什么

| 步 | 动作 | 要点 |
|---|---|---|
| 1 | 建团队 | 建的同时就得到一份共享任务列表 |
| 2 | 写派工单 | 任务描述就是成员的全部工作说明 |
| 3 | 派成员 | 起角色名，后台跑，不阻塞对话 |
| 4 | 收与并 | 汇报只当索引，结论回产出文件里核 |
| 5 | 收队 | 先逐个请退，再删团队 |

## 核心其实只有一件事：派工单

成员看不到你和用户的对话。它拿到的只有任务描述。

所以派工单必须自包含：目标、边界（哪里只读、只许写哪一个文件）、方法（搜索关键词和入口文件）、产出（绝对路径、语言、语气、标行号）、收尾（怎么汇报）。

含糊的派工单回来的是含糊的结果。见 `SKILL.md` 末尾那份完整样例——写十行，省掉一轮返工。

## 一次真实运行

一段早期版本的实际使用，三个成员并行：

| 成员 | 任务 | 产出 |
|---|---|---|
| `voice-digger` | 挖某参考项目里「长按消息 → 合成语音」的链路 | 201 行，带行号 |
| `ui-digger` | 拆同一项目的对话页视觉参数 | 397 行，含 Tailwind 映射 |
| `mapper` | 盘点自己项目的现状与改动面 | 250 行，含四类清单 |

结果里有两条推翻了我原本的假设：那个项目根本没有「长按合成语音」，而且界面其实是 WebView 里的网页而不是原生布局。两条都是成员先发现的。

也踩到三个坑，都写进 `SKILL.md` 了：团队还有成员在跑时删不掉、成员的话传不回主上下文、成员容易写和文档一样长的汇报。

## 文件

```
agent-team-skill/
├── SKILL.md    ← 技能本体，AI 读的是这份
├── README.md   ← 你正在看的
└── LICENSE
```

## English

A WorkBuddy skill that makes the model fan work out to a **named team** — members with names, tasks and visible progress in the sidebar — instead of anonymous subagents you can't observe.

It is a gate first and a procedure second: a team only pays off when the work splits into two or more genuinely independent lines, each needing real digging. Everything else is cheaper done directly.

```bash
git clone https://github.com/eggacheb/agent-team-skill.git ~/.workbuddy/skills/agent-team
```

Built for WorkBuddy; its team tools are the target of the five-step loop.

## License

MIT
