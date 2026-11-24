// Grader entrypoint for the news-image-20261123 v2 front page.
// Purpose: put the pre-rendered entry.png where the grader looks for it.
// The grader passes MAKEFUN_OUTPUT_DIR (else we fall back to /output);
// we create that folder and copy the PNG that sits next to this script,
// resolved from the script path so the working directory does not matter.
// No network, no randomness: the PNG is already baked, we only copy it.
import { mkdirSync, copyFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const here = dirname(fileURLToPath(import.meta.url));
mkdirSync(outDir, { recursive: true });
copyFileSync(resolve(here, "entry.png"), join(outDir, "entry.png"));
