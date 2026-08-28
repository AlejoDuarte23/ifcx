import { build } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(here, '..');

const entryPoint = resolve(projectRoot, 'src/ifcx/static/viewer.ts');
const shared = {
  entryPoints: [entryPoint],
  format: 'esm',
  platform: 'browser',
  target: ['es2022'],
  legalComments: 'inline',
  logLevel: 'info',
};

await Promise.all([
  build({
    ...shared,
    outfile: resolve(projectRoot, 'src/ifcx/static/viewer.bundle.js'),
    nodePaths: [resolve(here, 'node_modules')],
    bundle: true,
    minify: true,
    sourcemap: true,
  }),
  build({
    ...shared,
    outfile: resolve(projectRoot, 'src/ifcx/static/viewer.js'),
    bundle: false,
  }),
]);
