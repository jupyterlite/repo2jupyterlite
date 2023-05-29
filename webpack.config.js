const webpack = require("webpack");
const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  entry: path.resolve(__dirname, "src", "App.jsx"),
  plugins: [
    new HtmlWebpackPlugin({
      publicPath: "/static/",
      filename: path.resolve(
        __dirname,
        "binderlite",
        "templates",
        "index.html",
      ),
      hash: true,
      title:
        "BinderLite: Run JupyterLab entirely in the browser, with your packages & notebooks",
    }),
  ],
  mode: "development",
  module: {
    rules: [
      {
        test: /\.(js|jsx)/,
        exclude: /node_modules/,
        use: "babel-loader",
      },
      {
        test: /\.(css)/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  output: {
    publicPath: "/static/",
    filename: "index.js",
    path: path.resolve(__dirname, "binderlite/static/"),
  },
  resolve: {
    extensions: [".css", ".js", ".jsx"],
  },
};
