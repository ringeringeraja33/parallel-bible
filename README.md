# parallel-bible

Public-domain Bible translations as Markdown, **one file per chapter**, with every verse laid out as a small table so multiple languages line up side by side. Aligned across languages by a shared *Testament › Book › Chapter › Verse* coordinate.

> 公共领域的圣经译本，以 Markdown 存储，**一章一个文件**。每一节都是一个小表格，多语言内容并列对照，按照「约 › 书 › 章 › 节」的统一结构对齐。

## Languages included / 已收录语言

| Code | Translation | 译本 |
| --- | --- | --- |
| English | King James Version (KJV, 1769) | 詹姆士王译本 |
| 中文 | Chinese Union Version, New Punctuation (和合本) | 新标点和合本 |

More languages will be added over time — each new language is simply a new row added to every verse table.

> 后续会陆续加入更多语言：每种新语言只是在每个节的表格里新增一行。

## Structure / 目录结构

```
1-Old Testament/
  01-Genesis/
    Genesis 01.md
    Genesis 02.md
    ...
2-New Testament/
  43-John/
    John 03.md
    ...
```

- **Testament** and **book** folders are numbered to preserve canonical order.
- Book and file names are in English so the same verse sits at the same path regardless of language.
- Each file is one chapter; chapter numbers are zero-padded so they sort correctly.

> 「约」和「书」的文件夹带有序号以保持圣经原有顺序；文件夹与文件名统一使用英文，使同一节经文在任何语言下都位于相同路径；每个文件对应一章，章号补零以保证排序正确。

## Verse format / 单节格式

Each verse is a heading followed by a two-column table — column 1 is the language, column 2 is the text:

```markdown
## 1

| Language | Content |
| --- | --- |
| English | In the beginning God created the heaven and the earth. |
| 中文 | 起初神创造天地。 |
```

To add a language, add a labeled row to each verse's table (e.g. `| Français | Au commencement… |`).

> 每一节是一个标题加一个两列表格：第一列为语言，第二列为内容。新增语言时，只需在每一节的表格中加入对应的一行。

## Contents / 内容规模

- 66 books / 66 卷
- 1,188 chapters / 1,188 章
- 31,082 verses / 31,082 节

## Sources & license / 来源与授权

Both the King James Version (1769) and the Chinese Union Version (和合本, 1919) are in the **public domain**. The text here is reproduced from a public-domain parallel edition and may be freely used, copied, and redistributed.

> 詹姆士王译本（1769）与和合本（1919）均属**公共领域**，可自由使用、复制与再分发。
