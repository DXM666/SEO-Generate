import babel from '@rollup/plugin-babel';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import replace from '@rollup/plugin-replace';
import terser from '@rollup/plugin-terser';
import postcss from 'rollup-plugin-postcss';
import serve from 'rollup-plugin-serve';
import livereload from 'rollup-plugin-livereload';
import url from '@rollup/plugin-url';
import json from "@rollup/plugin-json";

const isProd = process.env.NODE_ENV === 'production';

export default {
  input: 'src/index.jsx',
  output: {
    file: 'dist/bundle.js',
    format: 'iife',
    sourcemap: !isProd,
    globals: {
      'react': 'React',
      'react-dom': 'ReactDOM',
      'antd': 'antd',
      'http': 'http',
      'https': 'https',
      'url': 'url',
      'stream': 'stream',
      'assert': 'assert',
      'tty': 'tty',
      'util': 'util',
      'os': 'os',
      'zlib': 'zlib',
      'path': 'path',
      'fs': 'fs'
    }
  },
  plugins: [
    resolve({
      extensions: ['.js', '.jsx'],
      browser: true,
      preferBuiltins: false
    }),
    json(),
    commonjs({
      include: /node_modules/,
      requireReturnsDefault: 'auto'
    }),
    replace({
      preventAssignment: true,
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    }),
    babel({
      babelHelpers: 'bundled',
      presets: ['@babel/preset-env', '@babel/preset-react'],
      extensions: ['.js', '.jsx'],
      exclude: 'node_modules/**',
    }),
    postcss({
      plugins: [],
      minimize: isProd,
      extract: 'bundle.css',
    }),
    url({
      include: ['**/*.svg', '**/*.png', '**/*.jpg', '**/*.gif'],
      limit: 8192,
    }),
    !isProd && serve({
      contentBase: ['dist', 'public'],
      port: 3000,
      historyApiFallback: true,
    }),
    !isProd && livereload('dist'),
    isProd && terser(),
  ],
  external: [
    'react',
    'react-dom',
    'antd',
    'http',
    'https',
    'url',
    'stream',
    'assert',
    'tty',
    'util',
    'os',
    'zlib',
    'path',
    'fs'
  ]
};
