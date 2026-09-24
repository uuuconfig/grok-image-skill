# Batch JSONL format

Write one JSON object per line. Each text-to-image job requires `prompt` and may override generation or output settings.

```jsonl
{"prompt":"A blue ceramic mug on white","out":"mug.png"}
{"prompt":"A red paper kite in a clear sky","size":"1536x1024","quality":"low","n":2,"out":"kite.png"}
```

Supported generation fields are `prompt`, `size`, `quality`, `n`, `out`, and `model`. `size` must be one of `1024x1024`, `1536x1024`, or `1024x1536`; `quality` remains a local CLI value (`low`, `medium`, `high`, or `auto`) and is not sent to the API.

Do not use edit/inpaint jobs in a batch. If a job contains `operation` set to `edit`, `inpaint`, or `mask`, or includes `image`, `images`, or `mask`, the job is marked failed locally and no API request is sent.

Use unique output names. When `n` is greater than one, the CLI adds `-1`, `-2`, and so on before the extension. The batch command prints a JSON summary and exits nonzero if any job fails.
