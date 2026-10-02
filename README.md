# parallel-bible

六语圣经对读笔记：English、中文、Français、Deutsch、Italiano、Latina。主体采用新教 66 卷范围及 **KJV 的 1,189 章、31,102 节坐标**，一章一个 Markdown 文件。其他传统的增补段落单列，范围不同不等于漏卷。

Six-language parallel Bible in Markdown, with one file per chapter. The main text uses the 66-book Protestant canon and KJV coordinates. Different verse boundaries are documented; a shared number does not by itself establish textual equivalence.

| 显示标签 | 所据文本 |
| --- | --- |
| English | CrossWire KJV，经 scrollmapper 数字导出；含该见证的拼写、诗篇篇题及附记 |
| 中文 | CrossWire ChiUn 和合本繁体数字导出，使用 OpenCC t2s 转为简体并去除分词空格；不是另一个出版社的“新标点版” |
| Français | Louis Segond 1910，midvash `lsg` 数据快照 |
| Deutsch | Lutherbibel 1912，midvash `luth1912` 数据快照；方括号内原分节编号保留 |
| Italiano | midvash 标称 Diodati 1649 的 `diodati` 数据快照 |
| Latina | midvash `vulg` 数据快照；另从 CrossWire Vulgate 导出补入 Ruth 4:22、Amos 9:15 |

译本名称是数字提供者的标识。本项目没有声称已逐页比对各历史印本，也没有把不同拉丁译本拼成一个“无异文”版本。准确来源、下载文件摘要及处理规则见 [SOURCES.md](SOURCES.md)；检查结果见 [校勘说明](Audit/校勘说明.md)。

## 阅读方式

每节依次列出六种语言。各译本原文保持自身用词；人物链接显示原语言拼写，如 `[[People/Moses|摩西]]`。三个词条目录分别为 [人物](People/README.md)、[地名](Places/README.md)及[其他专名](Names/README.md)。同名者在词条内按 STEPBible 身份标识分列，不能仅凭同名认定同一人。

- `〔原编号 …〕`：本行原文的来源坐标不同于主标题的 KJV 坐标。
- `〔合读对应 …〕`、`〔合读见 …〕`：一句或一段跨越两种分节方式，完整原文保留一次，其余位置给出链接；不凭猜测拆句。
- `〔所据数字底本此处无独立文本…〕`：来源确无可用独立文本，须参照校勘说明；不等同于“原圣经漏译”。
- 拉丁语独立篇题放在章首；底本所含《但以理书》增补原文见 [附录](Appendix/vulg.md)。本附录不代表完整收录其他正典体系。

## 校验与重建

```sh
python3 tools/validate.py
python3 tools/rebuild.py
```

两项操作只需 Python 3 标准库，无须联网。`data/` 保存固定的文本快照、分节对应和专名资料；`Audit/` 保存校勘决策、底本空缺及改动记录。校验涵盖全部章、节、六语行、内部链接及来源片段保全。通过自动检查不等于完成每一处语言和文本史问题的学术审定。

## 使用与授权

历史译本与数字数据、专名资料的授权须分别理解。STEPBible 派生专名与分节数据按 **CC BY 4.0** 署名；其他具体来源见 [SOURCES.md](SOURCES.md)。KJV 在英国的出版权限另受当地制度约束，不能概括为“全球无条件公共领域”。
