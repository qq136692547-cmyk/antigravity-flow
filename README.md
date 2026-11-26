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
  <a href="https://flow.google.com/?hl=en"><img src="https://img.shields.io/badge/Google%20Flow-Veo%203.1%20%7C%20Omni%201.2-green.svg" alt="Google Flow"></a>
  <a href="https://github.com/qq136692547-cmyk/antigravity-flow"><img src="https://img.shields.io/badge/version-0.3.2-orange.svg" alt="Version"></a>
</p>

![Google Flow Hero Banner](assets/hero-banner.jpg)

An Antigravity plugin that packages **Google Flow** ([flow.google.com](https://flow.google.com/?hl=en)) as an automated, industrial AI filmmaking and creative-tools workflow powered by Antigravity's built-in `browser` subagent — requiring zero external MCP servers, daemon processes, or headless Playwright binaries.

---

## Key Capabilities

- **Veo 3.1 & Omni 1.2 Five-Slot Grammar**: Turn creative ideas into production-ready prompts using the mandatory `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] . [Audio Sentences]` sequence across both Omni 1.2 Flash (flagship) and Veo 3.1 Lite.
- **Velocity Adverb Weight Lowering**: Automatically converts numerical weights (e.g., `(pan:1.4)`, `::2`) into natural velocity adverbs (`subtle`, `smooth`, `steady`, `deliberate`, `rapid`, `sweeping`) calibrated for Veo 3.1 and Omni 1.2 Flash.
- **Fail-Closed Live Credit Sniffer**: Real-time UI indicator inspection (`Generating will use <N> credits` or `Costs <N> credits`). If the web UI outputs `NaN credits` or unparsed text due to hydration latency, halts fail-closed for user confirmation.
- **Shared Google One AI Credit Pool Protection**: Hard spend ceiling of `MAX_CREDIT_CEILING = 60` credits per action even in `auto` mode, preventing unintended exhaustion of the credit pool shared with Antigravity.
- **Dynamic Upscale Duration Gating**: Safely gates 1080p downloads past 10s (1 credit/s) and all 4K upscales (50 credits + 5 credits/s past 10s) with mandatory confirmation checkpoints.
- **Character Consistency via Ingredients**: Seamlessly connects `@handles` across shots, manages 6 starter character archetypes, and handles start/end keyframe choreography with a randomized `8-15s` pacing jitter cooldown and `MAX_SESSION_DISPATCHES = 12` cap.
- **Anti-Risk-Control Circuit Breakers**: Enforces project reuse first, `x1` output default in `auto` mode, and zero-retry (`retry_count = 0`) hard-stop `PAUSED_*` boundaries on `ACCOUNT_VERIFICATION_REQUIRED`, `CAPTCHA_REQUIRED`, `RATE_LIMITED` (`429`), `WAF_BLOCKED` (`403` / `"unusual traffic"` / Turnstile), `SAFETY_BLOCKED`, `LOGIN_REQUIRED`, and `PAYMENT_REQUIRED`.
- **Scene Sequencing & Clip Editor**: Sequences shots, extracts keyframes (`Save frame`), performs timeline extensions (`Extend`), and enforces the invariant that inline video edits occur prior to clip extension.
- **Creative Tools Studio**: Browse 34 curated templates, spotlight community tools, or build custom zero-credit interactive creative tools in `Create tool`.
- **4-Tier Download Submenu**: Export directly to `270p Animated GIF`, `720p Original size`, `1080p Upscaled` (0 credits for <=10s), or `4K Upscaled · 50 credits` (mandatory confirmation gate).

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

1. **Direct Canonical URL & Project Reuse First**: Navigates directly to `https://flow.google.com/?hl=en` (preventing redundant SSO redirect hops and localized banner drift) and reuses open/existing `/project/<id>` projects before clicking `+ New project`.
2. **Fast-Path Authentication**: Uses above-the-fold visual signals, user avatar, and network HTTP 200 telemetry to bypass login prompts if already authenticated.
3. **Fail-Closed Credit Sniffer, Pool Protection & Anti-Risk-Control Pacing**:
   - `0 credits`: Executes automatically (`auto` mode) up to `MAX_SESSION_DISPATCHES = 12` (including `0-credit` actions) with `x1` default output count.
   - `> 0 credits`: Halts in `checkpoint` mode, displays exact credit quote, and awaits user confirmation.
   - `NaN / Unparsed`: Halts fail-closed in `checkpoint` mode if credit text contains `NaN` or fails to parse.
   - `MAX_CREDIT_CEILING = 60` & `MAX_SESSION_CREDITS = 120`: Single-action and session credit ceilings safeguard Antigravity's shared credit pool.
   - `Dynamic Upscale Gating`: Upscales >10s and all 4K upscales require explicit confirmation.
   - `Randomized Pacing Jitter`: Loops enforce an `8-15s` randomized cooldown between dispatches — no machine-speed bursts, no auto-retry/backoff, no blind refresh-resubmit, and no automated prompt softening.
   - `Zero-Retry Hard Stops (retry_count = 0)`: Immediately halts with `PAUSED_*` on `ACCOUNT_VERIFICATION_REQUIRED`, `CAPTCHA_REQUIRED`, `RATE_LIMITED`, `WAF_BLOCKED`, `SAFETY_BLOCKED`, `LOGIN_REQUIRED`, and `PAYMENT_REQUIRED`.
4. **Sandboxed File Staging**: Uploads stage through `<Artifact>/browser_sandbox/uploads/`, references through `browser_sandbox/references/`, and downloads stage to `browser_sandbox/downloads/`.

---

## Included Skills

| Skill | Mode | Role | Key Reference |
| :--- | :--- | :--- | :--- |
| **`flow-director`** | Autonomous | Storyboard planner, Veo 3.1 & Omni 1.2 5-slot grammar, velocity adverb lowering | `references/veo-prompt-guide.md` |
| **`flow-ingredients`** | Autonomous | Character archetype creator, reference library, 0-credit image generator, `8-15s` jitter pacer | None |
| **`flow-generate`** | Autonomous | Video & image shot generator, fail-closed sniffer, `x1` auto default, 12-dispatch cap, zero-retry breakers | None |
| **`flow-scene-builder`** | Autonomous | Scene sequencing, timeline extensions, frame extraction, edit-before-extend invariant | None |
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
- **`auto` Mode (Full-Auto)**: Mention `"auto mode"`, `"full-auto"`, `"run unattended"`, or `"without asking"` to execute planning, ingredient setup, shot rendering, and local downloads end-to-end without per-shot confirmation (capped at `MAX_CREDIT_CEILING = 60`).

---

## Verification Suite

Run the comprehensive 6-tier test suite:

```bash
python tests/run_tests.py
```

Test coverage (38/38 passing):
- **Tier 1**: Manifest Schema & Skill Integrity (frontmatter, author metadata, references, `v0.3.2` rules).
- **Tier 2**: Live Credit Sniffer & Plan Badge Parsing (Pro 0-credit vs Free charge regex).
- **Tier 3**: Autonomy Modes & Zero-Retry Safety Boundaries (`PAUSED_*`, `retry_count = 0`, 4K upscale gate, error classification).
- **Tier 4**: Veo 3.1 5-Slot Grammar & Storyboard Parser (AST validation, velocity adverbs).
- **Tier 5**: Adversarial Hardening (Zero-CJK & 7-bit ASCII checks, ReDoS safety, deprecation check, anti-retry clause audit).
- **Tier 6**: Live Grounding & Credit Hardening (Fail-Closed NaN sniffer, Nano Banana safety, comma-balance rejection, single & session ceilings, `MAX_SESSION_DISPATCHES = 12` including `0-credit` actions, randomized `8-15s` pacing jitter, `?hl=en` & project-reuse consistency, edit-before-extend invariant).

---

## Author & License

- Author: **qq136692547-cmyk** ([Personal Hub](https://qq136692547-cmyk.github.io/))
- Repository: [GitHub](https://github.com/qq136692547-cmyk/antigravity-flow)
- License: MIT

---

# 中文使用与架构进阶指南

## 1. 项目定位与生态闭环

`antigravity-flow` 是专为 Google Flow (`https://flow.google.com/?hl=en`) 打造的工业级多模态影视生成插件。它与 `antigravity-aistudio`（云端深度思考与代码分流）形成双轮驱动，构建起从**文本构思 -> 分镜拆解 -> 角色资产库 -> 视频分镜生成 -> 时间线剪辑 -> 4K高清导出**的完整自动化链路。

## 2. 核心架构与风控状态机

```mermaid
flowchart TD
    User["用户泛视觉需求\n(画概念图 / 做视频 / 排分镜)"] --> Router{"意图前置分流\n(免固定口令)"}
    Router -->|"视觉资产/角色插画"| Ing["flow-ingredients\n(Nano Banana 2.1 + 8-15s 随机冷却)"]
    Router -->|"分镜策划/剧本拆解"| Dir["flow-director\n(Omni 1.2 旗舰 / Veo 3.1 语法)"]
    Router -->|"视频镜头渲染"| Gen["flow-generate\n(Fail-Closed 嗅探 + 0 重试熔断)"]
    Router -->|"场景拼接/长片剪辑"| Scene["flow-scene-builder\n(先剪辑后延展铁律)"]
    Router -->|"创意工具工坊"| Tools["flow-tools"]

    subgraph SnifferLogic ["实时积分嗅探与反风控保护状态机"]
        Gen --> CheckSniffer["读取界面实时指示牌\nGenerating will use <N> credits"]
        CheckSniffer --> NanCheck{"是否包含 NaN 或解析失败 ?"}
        NanCheck -->|"是 (Fail-Closed)"| CheckpointMode["【checkpoint 模式】\n防御性暂停 + 等待人工确认"]
        NanCheck -->|"否 (合法整数 N)"| DispatchCap{"本会话调度次数 >= 12 ?\n(含 0 积分动作)"}
        DispatchCap -->|"是"| CheckpointMode
        DispatchCap -->|"否"| CeilingCheck{"单次消耗 N > 60 credits ?\n(保护反重力共享积分池)"}
        CeilingCheck -->|"是"| CheckpointMode
        CeilingCheck -->|"否"| CostJudge{"N 是否 == 0 ?"}
        CostJudge -->|"N == 0 (Pro/Ultra 0积分)"| AutoMode["【auto 模式】\n默认 x1 产出 + 8-15s 随机冷却"]
        CostJudge -->|"0 < N <= 60 (消耗积分)"| CheckpointMode
        AutoMode --> UpscaleJudge{"是否为 4K 超分或 >10s 导出 ?"}
        UpscaleJudge -->|"是"| CheckpointMode
        UpscaleJudge -->|"否"| Proceed["放行生成与本地下载入库\n(遇 429/403/验证码/安全拦截 0 重试 PAUSED_*)"]
    end
```

## 3. 六大核心技能详细分工

1. **`flow-director`（分镜总监）**：
   - 零积分消耗。将故事梗概拆解为结构化 `storyboard.md`，默认在 `auto` 模式推荐 `x1` 产出并控制单会话调度在 12 次以内。
   - 旗舰主推 `Omni 1.2 Flash`（支持 360p 极速草稿与 720p 旗舰成片），明确标注文生视频五段式语法与 12月5日 Veo Quality/Fast 下线倒计时。
2. **`flow-ingredients`（资产与角色库）**：
   - 优先复用已有 `/project/<id>` 项目，支持一键上传与 Nano Banana 2.1 零积分生图，内置 `8-15s` 随机抖动冷却与单会话 12 次调度软上限（含 0 积分动作）防 24h 限流。
3. **`flow-generate`（视频分镜渲染）**：
   - 内置 Fail-Closed 实时积分嗅探器，严防 SPA 延迟渲染导致的 `NaN credits` 漏检，设置 60 积分硬顶、`8-15s` 随机冷却与 0 重试熔断（遇 `ACCOUNT_VERIFICATION_REQUIRED`、`CAPTCHA_REQUIRED`、`RATE_LIMITED`、`WAF_BLOCKED`、`SAFETY_BLOCKED`、`LOGIN_REQUIRED`、`PAYMENT_REQUIRED` 立即暂停 `PAUSED_*`）。
4. **`flow-scene-builder`（时间线剪辑器）**：
   - 严格执行“剪辑优先于延展”铁律（Live 网页限制延展后不可再行原位编辑），延展能力独家绑定 `Omni 1.2 Flash`。
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
