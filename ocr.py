#!/usr/bin/env python3
"""Run Unlimited-OCR locally via llama.cpp. Produces structured OCR with bounding boxes."""
import argparse
import base64
import os
import re
import sys
import time


def main():
    parser = argparse.ArgumentParser(description="Unlimited-OCR local inference")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("--model-dir", default="models", help="Directory containing GGUF files")
    parser.add_argument("--model", default="Unlimited-OCR-Q4_K_M.gguf")
    parser.add_argument("--mmproj", default="mmproj-Unlimited-OCR-F16.gguf")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--gpu-layers", type=int, default=-1, help="-1 for all layers on GPU")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    model_path = os.path.join(args.model_dir, args.model)
    mmproj_path = os.path.join(args.model_dir, args.mmproj)

    for p, name in [(model_path, "model"), (mmproj_path, "mmproj"), (args.image, "image")]:
        if not os.path.exists(p):
            print(f"Error: {name} not found at {p}", file=sys.stderr)
            sys.exit(1)

    from llama_cpp import Llama
    from llama_cpp.llama_chat_format import MTMDChatHandler

    handler = MTMDChatHandler(clip_model_path=mmproj_path)
    llm = Llama(
        model_path=model_path,
        chat_handler=handler,
        n_ctx=args.max_tokens + 1024,
        n_gpu_layers=args.gpu_layers,
        verbose=False,
    )

    with open(args.image, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    start = time.time()
    result = llm.create_chat_completion(
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                {"type": "text", "text": "document parsing."},
            ],
        }],
        max_tokens=args.max_tokens,
        temperature=0.0,
    )
    elapsed = time.time() - start

    text = result["choices"][0]["message"]["content"]

    if args.json:
        import json
        blocks = parse_blocks(text)
        print(json.dumps({"blocks": blocks, "inference_ms": round(elapsed * 1000)}, indent=2))
    else:
        print(text)
        print(f"\n[{elapsed:.1f}s inference]", file=sys.stderr)


def parse_blocks(raw):
    blocks = []
    pattern = re.compile(r'^(\w+)\s+\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\](.*)$')
    for line in raw.split('\n'):
        m = pattern.match(line.strip())
        if m:
            blocks.append({
                "type": m.group(1),
                "bbox": [int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))],
                "text": m.group(6).strip(),
            })
    return blocks


if __name__ == "__main__":
    main()
