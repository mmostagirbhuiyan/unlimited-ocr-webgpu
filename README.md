# unlimited-ocr-local

Run Baidu's [Unlimited-OCR](https://github.com/baidu/Unlimited-OCR) locally via llama.cpp with structured bounding box output.

3B MoE model (500M active), MIT license. Produces element-level OCR with pixel coordinates in a single pass.

## Prerequisites

- Python 3.10+
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) >= 0.3.31 with [PR #2324](https://github.com/abetlen/llama-cpp-python/pull/2324) (passthrough template fix for multimodal)
- GGUF model files from [sahilchachra/Unlimited-OCR-GGUF](https://huggingface.co/sahilchachra/Unlimited-OCR-GGUF)

## Quick Start

```bash
pip install llama-cpp-python huggingface-hub

python -c "
from huggingface_hub import hf_hub_download
hf_hub_download('sahilchachra/Unlimited-OCR-GGUF', 'Unlimited-OCR-Q4_K_M.gguf', local_dir='models')
hf_hub_download('sahilchachra/Unlimited-OCR-GGUF', 'mmproj-Unlimited-OCR-F16.gguf', local_dir='models')
"

python ocr.py your_document.png
```

## Output Format

```
header [20, 43, 243, 104]INVOICE #1234
text [23, 468, 377, 528]Widget A 5 $10.00
```

Each line: `element_type [x1, y1, x2, y2]text_content`

Element types include `header`, `text`, `title`, `table`, `image`, `image_caption`.

## How It Works

Uses llama-cpp-python with `MTMDChatHandler` (llama.cpp native multimodal). The model encodes images through a dual vision encoder (CLIP-L-14 + SAM ViT-B) and generates structured OCR output with bounding boxes.

GPU acceleration via Metal (macOS), CUDA (Linux/Windows), or CPU fallback.

## Known Issue

Requires [PR #2324](https://github.com/abetlen/llama-cpp-python/pull/2324) on llama-cpp-python. Without it, models with passthrough chat templates produce empty output for multimodal input. Install from the PR branch:

```bash
pip install git+https://github.com/mmostagirbhuiyan/llama-cpp-python@fix/mtmd-passthrough-template-multimodal
```

## Attribution

- [Baidu Unlimited-OCR](https://github.com/baidu/Unlimited-OCR) (MIT License)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- GGUF conversion by [sahilchachra](https://huggingface.co/sahilchachra/Unlimited-OCR-GGUF)

## License

MIT
