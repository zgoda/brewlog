import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import babel from "@rollup/plugin-babel";

const isProduction = process.env.NODE_ENV === 'production';

const terserOpts = {
  ecma: 2015,
  compress: {module: true},
  mangle: {module: true},
  rename: {},
  safari10: true
}

export default (async () => ({
  output: {
    format: 'es',
    sourcemap: true,
    entryFileNames: '[name].[hash].js',
  },
  plugins: [
    resolve(),
    babel(),
    commonjs(),
    isProduction && (await import('rollup-plugin-terser')).terser(terserOpts),
  ]
}))();
