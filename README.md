# Antigravity Flow (`antigravity-flow`)

<p align="center">
  <img src="assets/logo.svg" width="128" height="128" alt="Google Flow Plugin Logo" />
</p>

<p align="center">
  <strong>Production-Grade AI Filmmaking & Multimodal Generation Engine for Google Flow</strong>
</p>

<p align="center">
  <a href="https://github.com/qq136692547-cmyk/antigravity-flow/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://qq136692547-cmyk.github.io/"><img src="https://img.shields.io/badge/author-qq136692547--cmyk-purple.svg" alt="Author"></a>
  <a href="https://flow.google.com"><img src="https://img.shields.io/badge/Google%20Flow-Veo%203.1%20%7C%20Omni%201.2-green.svg" alt="Google Flow"></a>
  <a href="https://github.com/qq136692547-cmyk/antigravity-flow"><img src="https://img.shields.io/badge/version-0.3.0-orange.svg" alt="Version"></a>
</p>

![Google Flow Hero Banner](assets/hero-banner.jpg)

An Antigravity plugin that packages **Google Flow** ([flow.google.com](https://flow.google.com)) as an automated, industrial AI filmmaking and creative-tools workflow powered by Antigravity's built-in `browser` subagent — requiring zero external MCP servers, daemon processes, or headless Playwright binaries.

---

## Key Capabilities

- **Veo 3.1 Five-Slot Grammar**: Turn creative ideas into production-ready prompts using the mandatory `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] . [Audio Sentences]` sequence.
- **Velocity Adverb Weight Lowering**: Automatically converts numerical weights (e.g., `(pan:1.4)`, `::2`) into natural velocity adverbs (`subtle`, `smooth`, `steady`, `deliberate`, `rapid`, `sweeping`) calibrated for Veo 3.1 and Omni 1.2 Flash.
- **Live Credit Sniffer (Single Source of Truth)**: Real-time UI indicator inspection (`Generating will use <N> credits`). Automatically runs zero-credit tasks in `auto` mode and safely gates paid generation in `checkpoint` mode.
- **Character Consistency via Ingredients**: Seamlessly connects `@handles` across shots, manages 6 starter character archetypes, and handles start/end keyframe choreography.
- **Scene Sequencing & Clip Editor**: Sequences shots, extracts keyframes (`Save frame`), performs timeline extensions (`Extend`), and triggers in-place video edits.
- **Creative Tools Studio**: Browse 34 curated templates, spotlight community tools, or build custom zero-credit interactive creative tools in `Create tool`.
- **4-Tier Download Submenu**: Export directly to `270p Animated GIF`, `720p Original size`, `1080p Upscaled` (0 credits), or `4K Upscaled · 50 credits` (mandatory confirmation gate).

---

## Installation

### From GitHub

```bash
agy plugin install https://github.com/qq136692547-cmyk/antigravity-flow
```

### Local Development

```bash
git clone https://github.com/qq136692547-cmyk/antigravity-flow.git
# Link into your Antigravity plugins directory:
ln -s "$(pwd)/antigravity-flow" ~/.gemini/config/plugins/antigravity-flow
```

---

## Operating Contract (`rules/AGENTS.md`)

When active, `rules/AGENTS.md` governs browser navigation and safety bounds:

1. **Direct Canonical URL**: Navigates directly to `https://flow.google.com/` (preventing redundant SSO redirect hops).
2. **Fast-Path Authentication**: Uses above-the-fold visual signals, user avatar, and network HTTP 200 telemetry to bypass login prompts if already authenticated.
3. **Credit Gating**:
   - `0 credits`: Executes automatically without interruption (`auto` mode).
   - `> 0 credits`: Halts in `checkpoint` mode, displays exact credit quote, and awaits user confirmation.
   - `4K Upscaled (50 credits)`: Hard-gated checkpoint requiring explicit single-turn confirmation.
4. **Sandboxed File Staging**: Uploads stage through `<Artifact>/browser_sandbox/uploads/`, references through `browser_sandbox/references/`, and downloads stage to `browser_sandbox/downloads/`.

---

## Included Skills

| Skill | Mode | Role | Key Reference |
| :--- | :--- | :--- | :--- |
| **`flow-director`** | Autonomous | Storyboard planner, Veo 3.1 5-slot grammar, velocity adverb lowering | `references/veo-prompt-guide.md` |
| **`flow-ingredients`** | Autonomous | Character archetype creator, reference library, 0-credit image generator | None |
| **`flow-generate`** | Autonomous | Video & image shot generator, live credit sniffer, batch runner | None |
| **`flow-scene-builder`** | Autonomous | Scene sequencing, timeline extensions, frame extraction, clip editor | None |
| **`flow-tools`** | Autonomous | Curated template runner, community tool explorer, custom tool builder | `references/tools-catalog.md` |
| **`flow-sync`** | Manual Only | Zero-credit 7-surface live audit crawler for UI drift and model deprecation | `references/audit-checklist.md` |

---

## Veo 3.1 Prompting Formula

Structure prompts according to the 5-slot formula:

```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] . [Audio Sentences]
```

### Example
```
Low-angle tracking shot, 35mm anamorphic lens, slow steady push-in, @detective_chen walks cautiously forward through the rain-slicked alleyway, tall brick walls adorned with buzzing holographic neon signs, cinematic teal and amber color grade with photorealistic volumetric smoke. Ambient noise: steady rainfall dripping onto metal fire escapes. SFX: leather boots splashing softly in puddles. @detective_chen speaks in a calm whisper: "The trace ends here."
```

---

## Autonomy Modes

- **`checkpoint` Mode (Default)**: The agent configures model parameters, calculates exact credit cost via the Live Credit Sniffer, presents a pre-flight table, and awaits confirmation before clicking `Start generation`.
- **`auto` Mode (Full-Auto)**: Mention `"auto mode"`, `"full-auto"`, `"run unattended"`, or `"without asking"` to execute planning, ingredient setup, shot rendering, and local downloads end-to-end without per-shot confirmation.

---

## Verification Suite

Run the comprehensive 5-tier test suite:

```bash
python tests/run_tests.py
```

Test coverage:
- **Tier 1**: Manifest Schema & Skill Integrity (frontmatter, author metadata, references).
- **Tier 2**: Live Credit Sniffer & Plan Badge Parsing (Pro 0-credit vs Free charge regex).
- **Tier 3**: Autonomy Modes & Security Bounds (auto vs checkpoint, 4K upscale gate).
- **Tier 4**: Veo 3.1 5-Slot Grammar & Storyboard Parser (AST validation, velocity adverbs).
- **Tier 5**: Adversarial Hardening (Zero-CJK codebase check, ReDoS safety, deprecation check).

---

## Author & License

- Author: **qq136692547-cmyk** ([Personal Hub](https://qq136692547-cmyk.github.io/))
- Repository: [GitHub](https://github.com/qq136692547-cmyk/antigravity-flow)
- License: MIT

---

# 中文使用与架构进阶指南

## 1. 项目定位与生态闭环

`antigravity-flow` 是专为 Google Flow (`https://flow.google.com`) 打造的工业级多模态影视生成插件。它与 `antigravity-aistudio`（云端深度思考与代码分流）形成双轮驱动，构建起从**文本构思 -> 分镜拆解 -> 角色资产库 -> 视频分镜生成 -> 时间线剪辑 -> 4K高清导出**的完整自动化链路。

## 2. 核心架构与风控状态机

```mermaid
flowchart TD
    User["用户泛视觉需求\n(画概念图 / 做视频 / 排分镜)"] --> Router{"意图前置分流\n(免固定口令)"}
    Router -->|"视觉资产/角色插画"| Ing["flow-ingredients\n(Nano Banana 2.1)"]
    Router -->|"分镜策划/剧本拆解"| Dir["flow-director\n(Veo 3.1 5-Slot Grammar)"]
    Router -->|"视频镜头渲染"| Gen["flow-generate\n(Live Credit Sniffer)"]
    Router -->|"场景拼接/长片剪辑"| Scene["flow-scene-builder"]
    Router -->|"创意工具工坊"| Tools["flow-tools"]

    subgraph SnifferLogic ["实时积分嗅探风控状态机"]
        Gen --> CheckSniffer["读取界面实时指示牌\nGenerating will use <N> credits"]
        CheckSniffer --> CostJudge{"N 是否 == 0 ?"}
        CostJudge -->|"N == 0 (Pro/Ultra 0积分)"| AutoMode["【auto 模式】\n全自动免打扰极速生成"]
        CostJudge -->|"N > 0 (消耗积分)"| CheckpointMode["【checkpoint 模式】\n汇报扣费数值 + 等待单次确认"]
        AutoMode --> UpscaleJudge{"是否为 4K 超分 ?\n(50 credits)"}
        UpscaleJudge -->|"是"| CheckpointMode
        UpscaleJudge -->|"否"| Proceed["放行生成与本地下载入库"]
    end
```

## 3. 六大核心技能详细分工

1. **`flow-director`（分镜总监）**：
   - 零积分消耗。将故事梗概拆解为结构化 `storyboard.md`。
   - 严格遵循 Veo 3.1 五段式镜头语法，自动将数字权重降级为镜头速度副词。
2. **`flow-ingredients`（资产与角色库）**：
   - 管理 6 种官方角色预设原型，支持一键上传与 Nano Banana 2.1 零积分生图。
3. **`flow-generate`（视频分镜渲染）**：
   - 内置实时积分嗅探器，精准识别免费与扣积分模式，支持 4 档分辨率下载。
4. **`flow-scene-builder`（时间线剪辑器）**：
   - 进入 `/project/<id>/edit/<clipId>` 剪辑模式，实现视频拼接、单帧提取（`Save frame`）与延展（`Extend`）。
5. **`flow-tools`（创意工具工坊）**：
   - 操作 34 款官方与社区创意工具，支持 0 积分一句话构建专属轻应用。
6. **`flow-sync`（零消耗巡检自愈）**：
   - 仅手动触发（`disable-model-invocation: true`）。针对 Flow 网页 7 大交互界面进行只读巡检，自愈漂移与废弃模型。

## 4. Veo 3.1 运镜副词速查表

| 运镜强度 | 替代的数字权重 | 推荐速度副词短语 | 典型示例 |
| :--- | :--- | :--- | :--- |
| **极微弱** | `0.2 - 0.4` | `subtle, barely perceptible` | `Subtle, barely perceptible camera drift` |
| **平缓柔和** | `0.5 - 0.8` | `smooth, gentle, measured` | `Smooth, gentle crane down revealing subject` |
| **基准标准** | `1.0` | `steady, cinematic, controlled` | `Steady, controlled tracking shot alongside car` |
| **明确动感** | `1.2 - 1.5` | `deliberate, pronounced, brisk` | `Deliberate, pronounced dolly push-in` |
| **极速戏剧** | `1.6 - 2.0` | `rapid, sweeping, dramatic` | `Rapid, sweeping whip pan to the horizon` |
