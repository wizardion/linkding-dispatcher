const { merge } = require('webpack-merge');
const commonConfig = require('./webpack.config.js');
const openBrowser = require('react-dev-utils/openBrowser');
const path = require('path');
const dotenv = require('dotenv');

dotenv.config({
  path: path.resolve(__dirname, 'local.env'),
});

const checkUrl = process.env.CHECK_URL;
const token = process.env.BACKEND_TOKEN;
const appURL = process.env.APP_URL;
const devConfig = {
  mode: 'development',
  devServer: {
    static: './build',
    port: 8080, // Internal port matching NGINX proxy_pass
    host: '0.0.0.0', // Allows connections outside localhost if using Docker/VMs
    allowedHosts: 'all', // Prevents 'Host Invalid' errors through the proxy
    open: false,
    hot: true,
    liveReload: true,
    watchFiles: ['src/**/*.scss', 'src/**/*.html'],
    client: {
      webSocketURL: 'auto://bookmarks.local/dispatcher/ws',
    },
    onListening: function (devServer) {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }

      const { port } = devServer.server.address();
      const url = `${appURL}?url=${checkUrl}&token=${token}`;

      // Smart opener: focuses the tab if open, opens new if closed
      openBrowser(url);
    },
  },
  watchOptions: {
    aggregateTimeout: 300, // Delays the rebuild after the first change
    poll: 1000, // Check for changes only every second (if files aren't triggering reload)
    ignored: /node_modules/, // Ignore node_modules to prevent CPU spikes
  },
};

// Ensure both commonConfig and devConfig are valid objects
module.exports = merge(commonConfig, devConfig);
