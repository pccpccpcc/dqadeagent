const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    host: 'localhost',
    open: false,
    proxy: {
      '/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        ws: false
      }
    }
  },
  
  // 生产环境配置
  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',
  
  // 输出目录
  outputDir: 'dist',
  
  // 静态资源目录
  assetsDir: 'static',
  
  // 是否在开发环境下通过 eslint-loader 在每次保存时 lint 代码
  lintOnSave: false,
  
  // 是否使用包含运行时编译器的 Vue 构建版本
  runtimeCompiler: true,
  
  // 生产环境是否生成 sourceMap 文件
  productionSourceMap: false,
  
  // webpack配置
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  },
  
  // CSS相关配置
  // css: {
  //   loaderOptions: {
  //     scss: {
  //       additionalData: `@import "@/styles/variables.scss";`
  //     }
  //   }
  // }
})

