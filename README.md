# Kyrgyz Inflection Generator

> A rule-based Kyrgyz morphological inflection generator written in Python.

**Kyrgyz Inflection Generator** 是一个用于自动生成吉尔吉斯语（Кыргыз тили）词形变化的 Python 项目。

项目将吉尔吉斯语的部分形态学规则编码为可执行程序，根据词干自动生成名词和动词的不同变化形式，并可以将生成结果批量导出为 **CSV、JSON、Excel 和 SQLite**。

它既可以作为吉尔吉斯语词形研究与实验工具，也可以作为词典、语言学习软件和自然语言处理项目的数据生成基础。

---

## Features

* 🇰🇬 吉尔吉斯语词形自动生成
* 🔤 基于元音和谐选择后缀
* 🔊 根据词尾处理辅音变化
* 📚 名词复数生成
* 🧩 名词格变化
* 👤 名词领属变化
* 🗣️ 动词人称变化
* ⏱️ 动词时态生成
* 🚫 动词否定形式
* 📦 支持批量处理词表
* 📊 使用 Pandas 生成结构化数据
* 🧪 提供自动化测试
* 💾 支持 CSV / JSON / Excel / SQLite 输出

---

## Why This Project?

吉尔吉斯语属于黏着语。

一个词可以通过不断添加后缀表达：

```text
词根
  ↓
复数
  ↓
领属
  ↓
格
  ↓
其他语法信息
```

例如，一个名词并不是只有一个固定形式。

```text
китеп
```

可以根据语法环境产生：

```text
китеп
китептер
китепте
китептин
китебим
...
```

如果手动为词典中的每一个词填写全部词形，不仅工作量巨大，而且容易出现重复劳动。

这个项目采用另一种方式：

```text
词根 + 语言规则 → 自动生成词形
```

因此词典只需要维护基础词汇和必要的例外信息，大量规则性词形可以由程序生成。

---

# Architecture

```text
Dictionary Source
      │
      ▼
 nouns.json / verbs.json
      │
      ▼
 Grammar Rules
      │
      ├── Noun Grammar
      │
      └── Verb Grammar
      │
      ▼
 Inflection Generator
      │
      ▼
 Pandas DataFrame
      │
      ├── CSV
      ├── JSON
      ├── Excel
      └── SQLite
```

整个系统分为三个主要部分：

### 1. Vocabulary Data

保存词典中的基础词形。

### 2. Grammar Engine

根据吉尔吉斯语语法规则计算后缀与词干变化。

### 3. Dataset Generator

将规则应用到大量词汇，并输出结构化词形数据库。

---

# Noun Inflection

名词规则主要位于：

```text
src/grammar.py
```

项目根据：

* 最后一个元音
* 元音和谐
* 词尾是否为元音
* 词尾辅音类别
* 清辅音 / 浊辅音
* 特殊词形

决定应该使用的后缀。

---

## Plural

例如：

```text
китеп
```

生成：

```text
китептер
```

而不只是简单地给所有词增加固定后缀。

程序会根据词尾和元音环境选择：

```text
-лар
-лер
-лор
-лөр

-дар
-дер
-дор
-дөр

-тар
-тер
-тор
-төр
```

等对应形式。

项目也允许处理不规则形式。

---

# Cases

当前规则模块包含多种名词格与相关派生形式。

例如：

### Locative

表示“在……”。

```text
китеп → китепте
```

### Ablative

表示“从……”。

### Genitive

表示所属关系。

```text
китеп → китептин
```

### Dative

表示方向或目标。

### Accusative

表示确定宾语。

### Instrumental

通过：

```text
менен
```

构成相关形式。

此外规则模块还包含：

* locative modifier
* caritive
* comparative

等形式。

---

# Possessive Inflection

项目还实现了吉尔吉斯语名词的领属变化。

包括：

```text
my
your_singular
your_polite
his_her
our
your_plural
your_plural_polite
their
```

例如：

```text
китеп
```

第一人称单数领属形式：

```text
китебим
```

这里不仅添加领属后缀，还会处理部分词干辅音变化：

```text
п → б
```

因此：

```text
китеп
   ↓
китебим
```

而不是简单拼接字符串。

---

# Verb Inflection

动词规则主要位于：

```text
src/verb_grammar.py
```

动词生成器位于：

```text
src/verb_generator.py
```

---

## Persons

当前系统处理以下人称：

```text
мен
сен
сиз
ал
биз
силер
сиздер
алар
```

对应：

```text
I
you
you (polite)
he / she
we
you (plural)
you (plural polite)
they
```

---

# Verb Forms

当前动词规则包括：

### Present / Future

生成一般现在或将来相关形式。

### Present Continuous

通过副动词形式与：

```text
жат
```

组合生成进行形式。

例如：

```text
оку
```

可以生成：

```text
окуп жатамын
окуп жатасың
окуп жатат
окуп жатышат
```

---

### Past

根据词干和人称生成过去时形式。

---

### Negative Past

生成过去时否定形式。

例如：

```text
оку
```

可以生成：

```text
окубодум
окубоду
окубошту
```

---

### Negative Future

例如：

```text
оку
```

可以生成：

```text
окубайт
окушпайт
```

---

### Imperative

支持命令式与否定命令式的基础生成规则。

---

# Vowel Harmony

词形生成的核心之一是吉尔吉斯语元音和谐。

程序会寻找词中的最后一个元音，并将其划分到对应元音组。

例如：

```text
а / я / ы
е / э / и
о / ё / у / ю
ө / ү
```

然后根据不同语法后缀选择：

```text
а / е / о / ө
```

或：

```text
ы / и / у / ү
```

等对应元音。

---

# Consonant Rules

程序还会根据词尾辅音类别调整后缀。

例如区分：

```text
voiceless consonants
voiced consonants
sonorants
vowels
```

这会影响：

```text
д / т
г / к
б / п
л / д / т
```

等后缀辅音的选择。

部分词形还包含词干辅音软化，例如：

```text
к → г
п → б
```

---

# Input Data

英文版项目的数据目录：

```text
data/
├── nouns.json
├── nouns.txt
├── verbs.json
└── verbs.txt
```

程序优先读取 JSON。

如果 JSON 不存在，也可以读取 TXT。

---

## Noun JSON

名词数据可以使用：

```json
{
  "nouns": [
    {
      "singular": "китеп",
      "meaning_zh": "书"
    }
  ]
}
```

主要字段：

```text
singular
meaning_zh
```

---

## Verb JSON

动词数据：

```json
{
  "verbs": [
    {
      "infinitive": "окуу",
      "stem": "оку",
      "meaning_zh": "读"
    }
  ]
}
```

主要字段：

```text
infinitive
stem
meaning_zh
```

---

# Generation Pipeline

批量生成流程：

```text
nouns.json
     │
     ▼
load_nouns()
     │
     ▼
generate_nouns_df()
     │
     ┐
     │
     ├── generate_all()
     │
     ┘
verbs.json
     │
     ▼
load_verbs()
     │
     ▼
generate_verbs_df()
     │
     ▼
export_all_formats()
```

---

# Output Formats

运行生成器后，结果会写入：

```text
output/
```

当前支持：

```text
kyrgyz.xlsx
kyrgyz.json
kyrgyz.db
kyrgyz_nouns.csv
kyrgyz_verbs.csv
```

---

## Excel

```text
kyrgyz.xlsx
```

包含多个 Sheet：

```text
Nouns
Verbs
```

适合人工检查、编辑和语言资料整理。

---

## CSV

分别生成：

```text
kyrgyz_nouns.csv
kyrgyz_verbs.csv
```

适合数据分析、批量处理以及导入其他系统。

---

## JSON

```text
kyrgyz.json
```

结构大致为：

```json
{
  "nouns": [],
  "verbs": []
}
```

适合：

* Web
* Flutter
* React Native
* API
* NLP 工具

使用。

---

## SQLite

```text
kyrgyz.db
```

数据库包含：

```text
nouns
verbs
```

两个主要数据表。

适合直接作为词典或语言应用的数据源。

---

# Project Structure

仓库目前包含中文和英文两个版本。

```text
kyrgyz-inflection-generator/
│
├── 吉尔吉斯语/
│   ├── data/
│   ├── output/
│   ├── src/
│   └── tests/
│
└── kyrgyz-inflection-generator-en/
    │
    ├── data/
    │   ├── nouns.json
    │   ├── nouns.txt
    │   ├── verbs.json
    │   └── verbs.txt
    │
    ├── src/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── generator.py
    │   ├── grammar.py
    │   ├── noun_generator.py
    │   ├── verb_grammar.py
    │   ├── verb_generator.py
    │   └── utils.py
    │
    ├── tests/
    │   ├── test_grammar.py
    │   └── test_verb_grammar.py
    │
    └── output/
        ├── kyrgyz.xlsx
        ├── kyrgyz.json
        ├── kyrgyz.db
        ├── kyrgyz_nouns.csv
        └── kyrgyz_verbs.csv
```

---

# Getting Started

Clone the repository:

```bash
git clone https://github.com/chengyang1017/kyrgyz-inflection-generator.git
```

进入英文版目录：

```bash
cd kyrgyz-inflection-generator/kyrgyz-inflection-generator-en
```

安装数据处理依赖：

```bash
pip install pandas openpyxl
```

---

# Run

运行完整数据生成：

```bash
python src/main.py
```

程序会：

```text
读取名词
   ↓
生成名词变化

读取动词
   ↓
生成动词变化

合并结构化数据
   ↓
输出 CSV
输出 JSON
输出 Excel
输出 SQLite
```

完成后可以在：

```text
output/
```

查看生成的数据。

---

# Tests

项目包含名词和动词语法规则测试。

安装 pytest：

```bash
pip install pytest
```

运行：

```bash
pytest
```

目前测试包含类似：

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

等规则。

---

# Design Philosophy

这个项目的核心并不是：

```text
把所有词形手工写进数据库
```

而是：

```text
保存词根
   +
编码语法规则
   ↓
自动生成词形
```

例如，如果一个词理论上拥有几十甚至数百种规则组合，与其：

```text
word
word_form_1
word_form_2
word_form_3
word_form_4
...
```

全部人工维护，不如保存：

```text
lexeme
+
morphological rules
```

再由程序生成：

```text
lexeme
      │
      ├── number
      ├── case
      ├── possession
      ├── person
      ├── tense
      └── polarity
```

这使语言数据能够更加系统化，并减少大量重复数据维护工作。

---

# Possible Uses

这个生成器可以作为以下项目的数据基础：

* 📖 吉尔吉斯语词典
* 🎓 吉尔吉斯语学习软件
* 🌍 多语言词典
* 🔎 Morphological Search
* 🧠 NLP preprocessing
* 📝 拼写与语法工具
* 📊 语言数据研究
* 🗃️ Lexical database
* 📱 Flutter / React Native language apps

---

# Roadmap

* [ ] 增加更多名词规则
* [ ] 增加更多动词时态
* [ ] 扩展不规则词数据库
* [ ] 完善辅音变化
* [ ] 增加更多自动化测试
* [ ] 增加词形反向分析
* [ ] 支持输入一个词并查询全部变化
* [ ] 增加 Morphological Analyzer
* [ ] 完善词形组合规则
* [ ] 与多语言词典数据系统整合

---

# Morphological Generator vs Dictionary

这个项目本身并不是完整词典。

它负责：

```text
Lexeme
   ↓
Morphological Rules
   ↓
Inflected Forms
```

而词典系统负责：

```text
Word
   ↓
Meaning
   ↓
Grammar
   ↓
Examples
```

两者结合后，可以形成：

```text
Dictionary
     +
Inflection Generator
     ↓
Structured Language Database
```

---

# Status

This project is under active development.

当前实现主要用于语言规则建模、程序实验和结构化语言数据生成。

部分规则仍需要随着更多真实语言资料和词汇测试继续校正，因此生成结果应在正式语言学或生产环境使用前进行验证。

---

# Author

**Cheng Yang**

A language technology project focused on representing Kyrgyz morphology as reusable computational rules.

> Store the lexeme. Encode the grammar. Generate the forms.
