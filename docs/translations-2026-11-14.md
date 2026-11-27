# 资源词库翻译记录（2026-11-14）

## 范围与来源

- 资源清单由 Painter 自带 API 枚举：`Shelf.resources()` → `gui_name()`（= 资源架显示名），
  共 **1485** 个去重名称，实测与界面 DisplayRole 完全一致。
- 官方 `.qm` 提取 3994 条只覆盖界面文本；资源架名称全部由人工词条提供。

## 术语表（固定译法）

| 英文 | 中文 | 备注 |
|---|---|---|
| Fabric | 织物 | 资源家族前缀，不用「布料」混用 |
| Grunge | 脏旧 | 统一，不译「垃圾」 |
| MatFinish / MatFx | 表面处理 / 材质效果 | 区分两类资源 |
| Concrete Asphalt / Cast / Coarse | 沥青混凝土 / 浇筑混凝土 / 粗质混凝土 | 不拆成两个词 |
| Leather Grain / Skin / Suede / Reptile Skin | 粒面皮革 / 光面皮革 / 麂皮 / 爬行动物皮革 | |
| Jersey | 汗布 | 纺织专名，不译「运动衫」 |
| Ripstop / Spacer Mesh | 防撕裂 / 间隔网布 | 纺织专名 |
| Houndstooth / Herringbone | 千鸟格 / 人字纹 | |
| Earthenware / Terracotta | 陶器 / 赤陶 | |
| Bokeh | 散景光斑 | |
| Parting Line | 分模线 | 模具术语 |
| Cavity | 缝隙 | 智能遮罩语境 |
| Base Color / Base color | 基础颜色 | 官方 .qm 译「底色」，已覆盖；与 Base Color Intensity 等统一 |
| Base Surface | 基础表面 | 官方 .qm 译「底面」，材质属性分组名 |
| Mask / mask | 遮罩 | 官方混用「遮罩/蒙版」，按 App 内多数与教程用词统一遮罩 |
| Filter / Filters | 滤镜 | 官方「过滤器」，统一滤镜；列表筛选（Filter by path）仍作「筛选」 |
| Specular | 高光 | 官方「镜面」，统一高光；字面 Mirror 材质仍作「镜面」 |
| Opacity | 不透明度 | 官方多处译「透明度」，语义相反 |
| Alpha / Alphas | Alpha（透明度）/ Alpha | 官方「透贴」 |
| Metallic | 金属度 | 官方「金属光泽」 |
| Environment | 环境 | 官方「背景」，指 IBL 环境而非视口背景 |
| Grunge | 脏旧 | 官方「垃圾摇滚」（音乐流派误译） |
| Smudge / Splat / Leak / Stain | 涂抹 / 飞溅 / 渗漏 / 污斑 | |
| Sign ... | ……标志 | 后置中心词 |
| Shape ... | ……形 | 后置中心词 |

## 结构规则

- 复合名按「中心词后置」写自然中文：`Circle Split Rounded` → `圆角分割圆形`。
- 资源家族用 ` · ` 分隔前缀与细分：`Fabric Lace` → `织物 · 蕾丝`。
- 编号资源保留阿拉伯数字与原编号格式：`Grunge Map 007` → `脏旧贴图 007`、`Grunge Map 7` 不改写。
- 拼写错误按原键保留（`Grunge Croncrete ...`、`Fetl Tip Large`、`Salt Course`、`Kyle's Inkbox - Chopped␠`），译文按正确语义。

## 明确不翻译

| 类别 | 例 | 原因 |
|---|---|---|
| 字体名（30） | `Almendra`、`Source Han Sans Light` | 字体族名是标识 |
| 着色器 ID（17） | `pbr-metal-rough`、`asm-metal-rough` | 技术标识，翻译会误导 |
| 色彩空间/LUT（约 19） | `ACES_UE4_Log`、`cineon`、`gamma1-8`、`sRGBf` | 行业标准名 |
| 品牌/艺术家名 | `Studio Tomoco`、`Kyle's ...` 前缀保留 Kyle | 专名 |

## 覆盖率

- 1485 个资源名中 **1414** 条有中文（95.2%）。
- 剩余 71 条为上述字体/着色器/色彩空间专名，按上表刻意保留英文。
- 运行时词库合计 **5435** 条（界面 3994 + 资源 1441，含少量重叠）。

## 待复核

- `Leather Skin → 光面皮革`、`Shutter Parting Line → 百叶分模线`、`Welding Gum → 焊瘤`
  三处依赖上下文，若实际资源外观不符再调整。
