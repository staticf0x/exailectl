const webpack = require('webpack');
const path = require('path');

module.exports = {
    entry: './js/main.js',
    output: {
        path: path.resolve(__dirname, 'js'),
        filename: 'exailectl.js'
    },
    resolve: {
        alias: {
          'vue$': 'vue/dist/vue.esm.js'
        }
      }
}
