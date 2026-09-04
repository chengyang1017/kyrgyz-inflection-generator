# 吉尔吉斯语词形生成器

**[English](README.md) | 简体中文**

一个使用 Python 编写的、基于规则的 **吉尔吉斯语形态生成引擎与数据集生成器**。

这个项目不是把每一个词形都手工存进数据库，而是把可复用的吉尔吉斯语语法规则编码成程序，再把这些规则应用到词汇数据上，自动生成名词与动词的词形变化，并输出为结构化数据。

```text
词元
  +
形态规则
  ↓
生成词形
  ↓
CSV / JSON / Excel / SQLite
```

这个项目的目标不是只做一个“看结果的小工具”，而是建立可以继续供词典、语言学习工具、搜索、NLP 与其他吉尔吉斯语软件复用的语言基础设施。

---

## 截图

> 这里先保留截图占位。准备好图片后放到 `docs/screenshots/` 即可。

### 名词词形生成

📸 **截图占位：** `docs/screenshots/noun-forms.png`

### 动词词形生成

📸 **截图占位：** `docs/screenshots/verb-forms.png`

### Excel 数据集

📸 **截图占位：** `docs/screenshots/excel-output.png`

### JSON / 结构化输出

📸 **截图占位：** `docs/screenshots/json-output.png`

### 规则测试

📸 **截图占位：** `docs/screenshots/tests.png`

---

## 项目能做什么

当前生成器的核心是**确定性的形态规则**，而不是让 AI 猜测词形。

### 名词

名词引擎目前处理的方向包括：

- 复数
- 格变化
- 领属变化
- 元音和谐
- 根据词尾辅音选择后缀
- 词干音变
- 部分特殊词形

例如：

```text
китеп
  ↓ 复数
китептер

китеп
  ↓ 位格
китепте

китеп
  ↓ 属格
китептин

китеп
  ↓ 第一人称领属
китебим
```

最后一个例子不是简单把后缀接上去，而是需要先处理词干辅音：

```text
п → б
```

---

### 动词

动词引擎目前覆盖的方向包括：

- 人称变化
- 现在 / 将来相关形式
- 现在进行结构
- 过去时
- 否定形式
- 命令式

例如：

```text
оку
  ↓ 进行形式
окуп жатамын

оку
  ↓ 过去时否定
окубодум

оку
  ↓ 将来 / 非过去否定
окубайт
```

---

## 为什么采用规则生成

吉尔吉斯语属于黏着语，一个基础词可以通过多个后缀和音系变化形成大量表面形式。

最直接的做法是：

```text
word
word_form_1
word_form_2
word_form_3
...
```

把所有词形都手工维护。

但大量形式其实是可以通过规则推导的。

这个项目采用：

```text
词元
+
元音和谐
+
辅音规则
+
格 / 领属 / 时态规则
        ↓
可重复生成的词形
```

这样数据可以随规则重新生成，也更容易测试、校验和扩展。

---

## 形态生成流程

```text
词汇数据
 nouns.json / verbs.json
          │
          ▼
      语法规则
      │      │
      ▼      ▼
    名词    动词
      │      │
      └──┬───┘
         ▼
 Pandas DataFrame
         │
  ┌──────┼──────┬────────┐
  ▼      ▼      ▼        ▼
 CSV    JSON   Excel   SQLite
```

只要输入词汇和规则实现相同，程序就会得到相同输出，因此整个词形层是可测试、可复现的。

---

## 元音和谐

后缀选择会受到词干最后相关元音的影响。

规则模块会判断元音所属类别，再选择对应的后缀元音。

常见分组包括：

```text
а / я / ы
е / э / и
о / ё / у / ю
ө / ү
```

并进一步影响：

```text
а / е / о / ө
ы / и / у / ү
```

等后缀形式。

---

## 辅音相关规则

程序也会根据词尾声音类别决定后缀。

包括区分：

- 元音
- 清辅音
- 浊辅音
- 响音

这会影响：

```text
д / т
г / к
б / п
л / д / т
```

等后缀辅音选择。

部分词形还会发生词干音变：

```text
к → г
п → б
```

---

## 输入数据

当前英文实现位于：

```text
kyrgyz-inflection-generator-en/
```

词汇数据位于：

```text
data/
├── nouns.json
├── nouns.txt
├── verbs.json
└── verbs.txt
```

程序优先读取 JSON，也保留 TXT 回退方式。

### 名词示例

```json
{
  "singular": "китеп",
  "meaning_zh": "书"
}
```

### 动词示例

```json
{
  "infinitive": "окуу",
  "stem": "оку",
  "meaning_zh": "读"
}
```

---

## 输出格式

项目支持一次生成多种格式：

```text
output/
├── kyrgyz.xlsx
├── kyrgyz.json
├── kyrgyz.db
├── kyrgyz_nouns.csv
└── kyrgyz_verbs.csv
```

### CSV

适合人工检查、批量处理、导入其他工具或表格软件。

### JSON

适合 Web、Flutter、API 与 NLP 工具。

### Excel

分别生成名词和动词 Sheet，便于人工浏览和整理语言数据。

### SQLite

生成 `nouns` 和 `verbs` 数据表，可以直接作为离线词典或语言应用的数据源。

这些输出逻辑统一集中在 `src/utils.py`，同一批生成结果可以写入不同格式。

---

## 项目结构

```text
kyrgyz-inflection-generator/
│
├── README.md
├── README.zh-CN.md
│
├── kyrgyz-inflection-generator-en/
│   ├── data/
│   │   ├── nouns.json
│   │   ├── nouns.txt
│   │   ├── verbs.json
│   │   └── verbs.txt
│   │
│   ├── src/
│   │   ├── main.py
│   │   ├── generator.py
│   │   ├── grammar.py
│   │   ├── noun_generator.py
│   │   ├── verb_grammar.py
│   │   ├── verb_generator.py
│   │   └── utils.py
│   │
│   ├── tests/
│   └── output/
│
└── 吉尔吉斯语/
    └── ...
```

仓库同时保留中文和英文方向的项目材料，但核心思路一致：把规则编码成程序，而不是把每一个表面词形都手工维护。

---

## 核心模块

### `grammar.py`

负责名词相关形态规则，例如元音和谐、后缀选择、格变化、领属变化和词干变化。

### `noun_generator.py`

将名词规则应用到词汇数据，生成结构化名词数据集。

### `verb_grammar.py`

负责动词形态与人称等相关规则。

### `verb_generator.py`

把动词规则批量应用到源词条。

### `utils.py`

负责数据读取，以及 JSON、CSV、Excel、SQLite 等输出。

---

## 开始使用

克隆仓库：

```bash
git clone https://github.com/chengyang1017/kyrgyz-inflection-generator.git
cd kyrgyz-inflection-generator/kyrgyz-inflection-generator-en
```

安装主要依赖：

```bash
pip install pandas openpyxl pytest
```

运行生成器：

```bash
python src/main.py
```

生成结果会写入：

```text
output/
```

---

## 测试

运行：

```bash
pytest
```

测试用于防止语言规则在继续开发时发生回归。

代表性的校验包括：

```text
китеп → китептер
китеп → китепте
китеп → китептин
китеп → китебим
```

以及：

```text
оку → окуп жатамын
оку → окубодум
оку → окубайт
```

这类项目尤其需要测试，因为底层一个后缀规则出错，可能一次影响大量生成词形。

---

## 设计原则

这个项目的一个核心原则是：

```text
能够用明确语言规则推导的词形，不交给 AI 猜。
```

形态生成本身应该保持确定性和可测试性。

AI 更适合放在后续层，例如：

```text
Python 规则
   ↓
经过校验的词形
   ↓
AI 生成例句 / 学习内容
```

这样即使以后加入 AI 例句，底层词形依然有规则系统负责，不会把“语言形态正确性”和“生成式内容”混在一起。

---

## 可应用方向

生成出来的数据未来可以用于：

- 吉尔吉斯语词典
- 词形查询工具
- 语言学习 App
- 搜索归一化
- 离线移动应用
- NLP 预处理
- Morphology API
- AI 例句流水线
- 语言学数据集

---

## 状态

**持续开发中。**

当前仓库已经包含可执行的名词与动词语法规则、批量生成器、结构化词汇输入、自动化测试以及多格式数据导出。

下一阶段重点是继续扩展规则覆盖、验证更多词汇组合、提高数据质量，并把经过校验的词形连接到更丰富的语言学习内容中。
