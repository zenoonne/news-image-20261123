// main.ts — grader entrypoint for the news-image-20261123 front page.
// Resolve where the grader wants the entry (MAKEFUN_OUTPUT_DIR, else /output),
// make sure that directory exists, and copy the pre-rendered entry.png beside
// this script into it. Pure copy: no network, no randomness, no side effects.
import { mkdirSync, copyFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const here = dirname(fileURLToPath(import.meta.url));
mkdirSync(outDir, { recursive: true });
copyFileSync(resolve(here, "entry.png"), join(outDir, "entry.png"));
