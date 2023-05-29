const webpack = require("webpack");
const path = require("path");

module.exports = {
  entry: path.resolve(__dirname, "src", "App.jsx"),
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
    publicPath: "/",
    filename: "index.js",
    path: path.resolve(__dirname, "binderlite/static/"),
  },
  resolve: {
    extensions: [".css", ".js", ".jsx"],
  },
};
