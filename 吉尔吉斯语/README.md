# 吉尔吉斯语词形变化生成器

## 项目用途

自动生成吉尔吉斯语名词变化表，并预留动词及其他词类的扩展入口。

## 当前状态

名词生成器已完成，第一版动词生成器已实现。

## 运行方式

```bash
python src/main.py
```

## 输出说明

```text
output/kyrgyz.xlsx：总 Excel，包含名词、动词等多个 Sheet
output/kyrgyz_nouns.xlsx：名词单独 Excel
output/kyrgyz.csv：名词 CSV
output/kyrgyz.json：名词 JSON
output/kyrgyz.db：SQLite 数据库
```

## 目录结构

```text
src/
  main.py：主入口文件
  generator.py：统一调度所有词类生成器
  noun_generator.py：名词生成器
  verb_generator.py：动词生成器占位
  grammar.py：名词语法规则和通用规则
  verb_grammar.py：动词语法规则占位
  utils.py：读取、导出、路径处理工具
data/
  nouns.json / nouns.txt：名词数据
  verbs.json / verbs.txt：动词数据占位
output/：生成结果
tests/：基础测试
```

## 未来计划

动词复杂规则、形容词、代词、更多词库、准确性校验。
