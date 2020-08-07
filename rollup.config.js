import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

const isProduction = process.env.NODE_ENV === 'production';

const terserOpts = {
  compress: {ecma: 2015, module: true},
  mangle: {module: true},
  output: {ecma: 2015},
  parse: {ecma: 2015},
  rename: {},
}

export default (async () => ({
  output: {
    format: 'es',
    sourcemap: true,
    entryFileNames: '[name].[hash].js',
  },
  plugins: [
    resolve(),
    commonjs(),
    isProduction && (await import('rollup-plugin-terser')).terser(terserOpts),
  ]
}))();
