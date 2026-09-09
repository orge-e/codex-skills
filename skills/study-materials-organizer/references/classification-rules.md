# Classification Rules

## Category markers

- `知识清单与方法归纳`: `知识清单`, `知识必备`, `题型必备`, `思维导图`, `方法归纳`
- `复习讲义`: `讲义`, `高频考点`
- `专项训练`: `专项训练`, `专题练`, `解题思路训练`, `提优秘籍`, `典型题型归类训练`
- `通关卷与检测卷`: `通关卷`, `检测卷`, `模拟卷`, `综合训练卷`, `收官卷`, `阶段性检测`, `摸底考`, `卷`
- `课件`: `.ppt`, `.pptx`
- `素材归档`: `.png`, `.jpg`, `.jpeg`, `.emf`, `.wmf`, `.emmx`
- `压缩包`: `.zip`, `.rar`, `.7z`
- fallback: `其他待整理`

## Version markers

- `原卷版`: `原卷版`, `原卷`, `学生版`, `考试版`, `试题版`, `练习版`, `空白卷`
- `解析版`: `解析版`, `教师版`, `答案`, `详解`, `全解全析`, `参考答案`, `解析板`
- fallback: `通用版`

## Ambiguous basename patterns

Add a source prefix when the basename begins with:

- `第N讲`
- `第N课时`
- `专题N`
- `专题一/二/三...`
- `微专题N`

## Prefix priority

1. nearest chapter directory such as `第一章 直线运动`
2. nearest module-like directory such as `数列`, `圆锥曲线`, `平面解析几何`
3. nearest set/package directory such as `2025年高考数学一轮复习知识清单`
4. immediate parent directory

## Conflict handling

- same hash: treat as duplicate and keep only one file
- same destination path but different hash: keep both, rename incoming file with `补充版-`
- use move, not copy, unless the user explicitly asks to preserve source files
