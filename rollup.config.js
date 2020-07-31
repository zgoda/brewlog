import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

const isProduction = process.env.FLASK_ENV === 'production';

const terserOpts = {
  compress: {ecma: 2015, module: true},
  mangle: {module: true},
  output: {ecma: 2015},
  parse: {ecma: 2015},
  rename: {},
}

export default (async () => ({
  input: {
    dashboard: 'src/brewlog/static/js/dashboard.js'
  },
  output: {
    dir: 'src/brewlog/static/dist',
    format: 'es',
    sourcemap: true
  },
  plugins: [
    resolve(),
    commonjs(),
    isProduction && (await import('rollup-plugin-terser')).terser(terserOpts)
  ]
}))();
