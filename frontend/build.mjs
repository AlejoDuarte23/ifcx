import { build } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(here, '..');

await build({
  entryPoints: [resolve(projectRoot, 'src/ifcx/static/viewer.js')],
  outfile: resolve(projectRoot, 'src/ifcx/static/viewer.bundle.js'),
  nodePaths: [resolve(here, 'node_modules')],
  bundle: true,
  format: 'esm',
  platform: 'browser',
  target: ['es2022'],
  minify: true,
  sourcemap: true,
  legalComments: 'inline',
  logLevel: 'info',
});
