---
name: grok-image
description: Generate raster images through the OpenAI-compatible Grok Imagine API using grok-imagine-image-quality, GROK_API_URL, and GROK_API_KEY. Use when Codex should create one or many images, illustrations, product shots, covers, website assets, or visual variants with Grok.
---

# Grok Image

Generate images with the bundled Grok-specific CLI. Prefer this skill's executable over the built-in image generation tool whenever this skill is active. The CLI targets an OpenAI-compatible `/v1/images/generations` endpoint and uses the fixed model `grok-imagine-image-quality` by default.

## API contract

The service base URL comes from `GROK_API_URL`. Do not ask the user to provide a complete endpoint. The CLI appends the path as follows:

- `${GROK_API_URL}/v1/images/generations`
- If `GROK_API_URL` already ends in `/v1`: `${GROK_API_URL}/images/generations`

The default base URL is `https://api.x.ai` when `GROK_API_URL` is unset. Set `GROK_API_KEY` locally; never put it in prompts, files, logs, or responses.

The HTTP JSON payload is intentionally:

```json
{
  "model": "grok-imagine-image-quality",
  "prompt": "...",
  "size": "1024x1024",
  "n": 1,
  "response_format": "b64_json"
}
```

The local CLI keeps `--quality` for compatibility and validation (`low`, `medium`, `high`, or `auto`), but **never sends `quality` to the API**. Valid sizes are exactly `1024x1024`, `1536x1024`, and `1024x1536`; invalid sizes are rejected locally.

The response parser accepts both `data[].b64_json` and `data[].url`, preferring Base64 when present and downloading URL results when needed.

## Select the executable

Choose once from the current operating system and CPU architecture:

- Windows x64: `bin/grok-image-windows-amd64.exe`
- Windows ARM64: `bin/grok-image-windows-arm64.exe`
- macOS Intel: `bin/grok-image-darwin-amd64`
- macOS Apple Silicon: `bin/grok-image-darwin-arm64`

On macOS, run `chmod +x <executable>` if execute permission was not preserved. Do not compile from source during normal use.

## Workflow

1. Decide whether the request is one image, multiple variants, or a batch of distinct text-to-image assets.
2. Collect the prompt, intended use, exact text, visual constraints, and avoid items.
3. Preserve detailed prompts; clarify generic prompts only as needed and do not invent brands, people, slogans, or unrelated objects.
4. Run the selected executable with `generate` for one prompt or `generate-batch` for JSONL jobs.
5. Inspect each output for subject, composition, text accuracy, constraints, and visible artifacts.
6. If revision is needed, submit a new text-to-image request; do not use `edit` for this model.
7. Report absolute output paths, the final prompt or prompt set, size, local quality label, and model.

## Prompt structure

Use only relevant lines:

```text
Asset type: <where the image will be used>
Primary request: <the user's request>
Scene/backdrop: <environment>
Subject: <main subject>
Style/medium: <photo, illustration, 3D, etc.>
Composition/framing: <camera angle, crop, placement, negative space>
Lighting/mood: <lighting and mood>
Color palette: <palette notes>
Text (verbatim): "<exact text>"
Constraints: <must keep or include>
Avoid: <must not include>
```

Do not add detail merely to fill the schema. For text in images, quote it verbatim and request exact rendering.

## Generate one image

```powershell
& "<skill-dir>\bin\grok-image-windows-amd64.exe" generate `
  --prompt "A small blue nebula in a glass bottle, studio product photo" `
  --size 1024x1024 `
  --quality auto `
  --out "output/imagegen/nebula.png"
```

Use `--prompt-file` for long prompts. Use `--n` for variants of the same prompt. Distinct assets belong in separate calls or a batch. The CLI writes `response_format: "b64_json"` and does not send the local quality label.

## Edit and mask behavior

Grok Imagine does not provide image-editing, inpaint, or mask operations through this skill. The `edit` subcommand and its `--image` / `--mask` flags remain defined for caller compatibility, but every `edit` invocation is rejected locally without any network request with this exact message:

```text
grok-imagine-image-quality does not support image-editing / inpaint / mask operations. Only text-to-image generation (generate / generate-batch) is available.
```

For a desired revision, create a new text-to-image request and explicitly restate the invariants that should remain unchanged.

## Generate a batch

Read [references/batch-format.md](references/batch-format.md) before preparing a batch. Then run:

```powershell
& "<skill-dir>\bin\grok-image-windows-amd64.exe" generate-batch `
  --input "tmp/imagegen/jobs.jsonl" `
  --out-dir "output/imagegen" `
  --concurrency 2
```

Batch jobs are text-to-image only. Jobs marked with `operation: edit`, `operation: inpaint`, or `operation: mask`, or containing `image`, `images`, or `mask`, fail locally and do not submit an API request.

## Python fallback

If the native executable times out while a direct API request is reachable, use the no-dependency Python fallback. It supports generation, multiple outputs, Base64 and URL responses, the same size whitelist, local quality validation, and `--dry-run`:

```powershell
python "<skill-dir>\bin\grok-image-python.py" `
  --prompt "A small blue nebula in a glass bottle, studio product photo" `
  --size 1024x1024 `
  --quality low `
  --out "output/imagegen/nebula.png"
```

Use `--dry-run` to inspect the final endpoint and actual HTTP payload without requiring a key or making a network request.

## Configuration and safety

- Require `GROK_API_KEY` for network requests. If absent, tell the user to set it locally and confirm when ready; never ask them to paste it into chat.
- Read the service base from `GROK_API_URL`; default to `https://api.x.ai`.
- Default to model `grok-imagine-image-quality`, size `1024x1024`, and local quality `auto` in the native CLI. The Python fallback defaults its local quality to `low` for smoke tests.
- Save project-bound assets inside the current project. The CLI default is `output/imagegen/`.
- Do not overwrite files unless the user explicitly authorizes it and `--force` is passed.
- Native transparent output is not part of this skill's API contract. Do not promise it or silently switch tools.

## Failure handling

- The CLI retries network timeouts and HTTP 429/500/502/503/504/524 failures with bounded backoff.
- On repeated timeout, try `--quality low`, a square size, fewer concurrent jobs, or the Python fallback. Quality is local-only and does not change the HTTP payload.
- Do not retry authentication, validation, unsupported-operation, or other ordinary 4xx errors.
- Never expose an Authorization header or full key when reporting errors.
