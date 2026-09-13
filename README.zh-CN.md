# 吉尔吉斯语词形生成器

**[English](README.md) | 简体中文**

一个使用 Python 编写、基于规则的 **吉尔吉斯语形态生成引擎与数据集生成器**。

项目不会手工保存每一个词形，而是把名词和动词的语法规则编码成程序，再根据词汇数据自动生成真实词形，并导出为结构化数据。

```text
词元
  +
形态规则
  ↓
生成词形
  ↓
CSV / JSON / Excel / SQLite
```

项目目标是提供可复用的语言基础设施，可供词典、语言学习工具、搜索、NLP、离线应用和其他吉尔吉斯语软件使用。

---

## 主要能力

名词方向包括复数、格变化、领属、元音和谐、辅音相关后缀选择、词干变化和部分特殊形式。

动词方向包括人称变化、时态、进行结构、过去时、否定形式和命令式等。

形态生成保持确定性：相同输入和规则会得到相同结果，便于测试和回归验证。

---

## 统一后的数据结构

词汇数据统一放在：

```text
data/
├── nouns.json
├── nouns.txt
├── verbs.json
└── verbs.txt
```

项目不再维护中文、英文两套重复代码，而是使用统一核心加本地化层。

支持的界面/释义本地化目前包括：

```text
en
zh
ru
```

---

## 输出

统一生成器会输出 canonical 数据和本地化数据：

```text
output/
├── canonical/
│   ├── kyrgyz.json
│   └── kyrgyz.db
├── en/
├── zh/
└── ru/
```

每个本地化目录都会包含 Excel、JSON、SQLite，以及名词和动词 CSV。

canonical 数据使用规范化词元、义项、释义、名词词形和动词词形结构，方便 Flutter 词典、搜索和其他程序直接消费。

---

## 项目结构

```text
kyrgyz-inflection-generator/
├── data/
├── docs/
├── locales/
├── src/
│   ├── canonical.py
│   ├── dictionary.py
│   ├── generator.py
│   ├── grammar.py
│   ├── i18n.py
│   ├── lexicon.py
│   ├── main.py
│   ├── noun_generator.py
│   ├── sqlite_lexicon.py
│   ├── utils.py
│   ├── verb_generator.py
│   └── verb_grammar.py
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── README.zh-CN.md
```

---

## 开始使用

克隆仓库：

```bash
git clone https://github.com/chengyang1017/kyrgyz-inflection-generator.git
cd kyrgyz-inflection-generator
```

安装依赖：

```bash
pip install -r requirements-dev.txt
```

生成全部语言版本：

```bash
python src/main.py --locale all
```

只生成英文版本：

```bash
python src/main.py --locale en
```

---

## 测试

运行：

```bash
pytest
```

当前测试不仅覆盖基础名词和动词规则，也覆盖 canonical lexical model、词典查询、SQLite 词库、本地化和结构化词汇数据。

---

## 设计原则

核心原则仍然是：

```text
能够通过明确规则推导的词形，不交给 AI 猜。
```

底层形态系统保持规则化、可复现和可测试；AI 可以放在例句生成、学习内容等上层功能。

---

## 可应用方向

- 吉尔吉斯语词典
- 词形查询工具
- Flutter / Web 语言应用
- 搜索归一化
- 离线词典
- NLP 预处理
- Morphology API
- 语言学数据集

---

## 状态

**持续开发中。**

仓库目前已经完成统一多语言核心、规范化 lexical model、字典查询、SQLite 词库支持、自动测试和多格式导出。