import { nodeResolve } from '@rollup/plugin-node-resolve';
import { terser } from "rollup-plugin-terser";

export default {
  plugins: [
    nodeResolve(),
    terser({
      compress: {ecma: 2015, module: true},
      mangle: {module: true},
      output: {ecma: 2015},
      parse: {ecma: 2015},
      rename: {},
    })
  ]
};
