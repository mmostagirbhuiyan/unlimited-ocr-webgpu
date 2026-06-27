export interface OCRBBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface OCRBlock {
  type: string;
  bbox: OCRBBox;
  text: string;
}

export interface OCRResult {
  raw: string;
  blocks: OCRBlock[];
  text: string;
  inferenceTimeMs: number;
}

/**
 * Parse the structured output from Unlimited-OCR.
 * Format: element_type [x1, y1, x2, y2] text content
 * Example: header [20, 43, 243, 100]INVOICE #1234
 */
export function parseOCROutput(raw: string): OCRBlock[] {
  const blocks: OCRBlock[] = [];
  const pattern = /^(\w+)\s+\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\](.*)$/;

  for (const line of raw.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    const match = trimmed.match(pattern);
    if (match) {
      blocks.push({
        type: match[1],
        bbox: {
          x1: parseInt(match[2], 10),
          y1: parseInt(match[3], 10),
          x2: parseInt(match[4], 10),
          y2: parseInt(match[5], 10),
        },
        text: match[6].trim() || match[6],
      });
    }
  }

  return blocks;
}

/**
 * Convert OCRBlocks to a plain text string (concatenated block text).
 */
export function blocksToText(blocks: OCRBlock[]): string {
  return blocks.map(b => b.text).join('\n');
}

/**
 * Convert OCRBlocks to the LocalRedact OCRWord format for redaction overlay compatibility.
 */
export function blocksToOCRWords(blocks: OCRBlock[]): Array<{
  text: string;
  bbox: { x0: number; y0: number; x1: number; y1: number };
  confidence: number;
}> {
  return blocks.map(block => ({
    text: block.text,
    bbox: {
      x0: block.bbox.x1,
      y0: block.bbox.y1,
      x1: block.bbox.x2,
      y1: block.bbox.y2,
    },
    confidence: 0.95,
  }));
}
