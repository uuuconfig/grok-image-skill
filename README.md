# Grok Image Skill

让 Codex 通过 OpenAI-compatible 的 Grok Imagine Images API，直接使用 `grok-imagine-image-quality` 生成图片。

## 功能

- 文生图
- 单图或多图生成
- JSONL 并发批量文生图
- 支持 Base64 和 URL 两种图片响应
- 自动重试网络超时、429、5xx 和 524 错误
- 输出文件覆盖保护
- API Key 不写入 Skill、提示词、日志或响应
- 内置 Windows x64/ARM64 与 macOS Intel/Apple Silicon 可执行文件
- Python 无依赖 fallback
- dry-run 请求校验

> 当前 Grok Image API 不提供 image edit、inpaint 或 mask 局部重绘接口。Skill 仍保留 `edit` 命令语法用于兼容上层调用，但会在本地直接拒绝，不会发起网络请求。

## 安装

### 让 Codex 自动安装

将本仓库地址发送给 Codex：

```text
请帮我安装这个 Skill：
https://github.com/<你的用户名>/grok-image-skill
```

### Windows PowerShell

```powershell
git clone https://github.com/<你的用户名>/grok-image-skill.git
Copy-Item grok-image-skill\grok-image "$HOME\.codex\skills\grok-image" -Recurse
```

### macOS / Linux

```bash
git clone https://github.com/<你的用户名>/grok-image-skill.git
cp -R grok-image-skill/grok-image ~/.codex/skills/grok-image
chmod +x ~/.codex/skills/grok-image/bin/grok-image-darwin-*
```

## 配置环境变量

### Windows

```powershell
[Environment]::SetEnvironmentVariable("GROK_API_URL", "https://api.x.ai", "User")
[Environment]::SetEnvironmentVariable("GROK_API_KEY", "你的API密钥", "User")
```

也可以使用反向代理的基地址：

```powershell
[Environment]::SetEnvironmentVariable("GROK_API_URL", "https://proxy.example.com", "User")
```

`GROK_API_URL` 只填写服务基地址，不要填写完整的 `/v1/images/generations`。Skill 会自动处理以下两种情况：

```text
https://api.x.ai
→ https://api.x.ai/v1/images/generations

https://proxy.example.com/v1
→ https://proxy.example.com/v1/images/generations
```

### macOS / Linux

```bash
export GROK_API_URL="https://api.x.ai"
export GROK_API_KEY="你的API密钥"
```

配置用户级环境变量后，需要完全退出并重新启动 Codex，新的环境变量才会生效。

## 在 Codex 中使用

```text
使用 $grok-image 生成一张图片：
一只戴着宇航员头盔的橘猫站在月球表面，远处可以看到地球，电影感灯光。
```

Skill 默认使用：

```text
model: grok-imagine-image-quality
size: 1024x1024
quality: auto（仅本地 CLI 标记，不发送给 API）
```

可用尺寸：

```text
1024x1024
1536x1024
1024x1536
```

## API 请求格式

Skill 实际发送的文生图 JSON 为：

```json
{
  "model": "grok-imagine-image-quality",
  "prompt": "...",
  "size": "1024x1024",
  "n": 1,
  "response_format": "b64_json"
}
```

`--quality` 参数保留用于兼容原有 Codex Image2 调用方式，但不会发送到远端 API。

Skill 同时支持解析：

```json
{"data":[{"b64_json":"..."}]}
```

和：

```json
{"data":[{"url":"https://..."}]}
```

## CLI 调试

Windows x64：

```powershell
& "grok-image/bin/grok-image-windows-amd64.exe" generate `
  --prompt "A small blue nebula in a glass bottle, studio product photo" `
  --size 1024x1024 `
  --quality low `
  --out "output/imagegen/nebula.png"
```

多图生成：

```powershell
& "grok-image/bin/grok-image-windows-amd64.exe" generate `
  --prompt "Three editorial product variations of a ceramic mug" `
  --size 1536x1024 `
  --quality high `
  --n 3 `
  --out "output/imagegen/mug.png"
```

dry-run：

```powershell
& "grok-image/bin/grok-image-windows-amd64.exe" generate `
  --prompt "A blue nebula in a glass bottle" `
  --size 1024x1024 `
  --quality low `
  --dry-run `
  --out "output/imagegen/nebula.png"
```

Python fallback：

```powershell
python "grok-image/bin/grok-image-python.py" `
  --prompt "A blue nebula in a glass bottle" `
  --size 1024x1024 `
  --quality low `
  --out "output/imagegen/nebula.png"
```

完整工作流、batch JSONL 格式和限制请查看 [`grok-image/SKILL.md`](grok-image/SKILL.md)。

## 安全说明

- 不要把真实 API Key 提交到 GitHub。
- 不要把 API Key 写进 Skill、提示词、截图或聊天消息。
- Skill 只从 `GROK_API_KEY` 环境变量读取密钥。
- `GROK_API_URL` 只应包含 API 服务基地址。

## License

[MIT](LICENSE)
