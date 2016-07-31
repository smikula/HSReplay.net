const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const fs = require("fs");
const {execSync} = require("child_process");

const exportSettings = ["STATIC_URL", "JOUST_STATIC_URL"];
const exportedSettings = JSON.parse(
	execSync("python ./manage.py show_settings " + exportSettings.join(" "))
);
const settings = Object.keys(exportedSettings).reduce((obj, current) => {
	obj[current] = JSON.stringify(exportedSettings[current]);
	return obj;
}, {});

module.exports = {
	context: __dirname,
	entry: {
		my_replays: "./hsreplaynet/static/scripts/src/my_replays",
		replay_detail: "./hsreplaynet/static/scripts/src/replay_detail",
	},
	output: {
		path: path.resolve("./hsreplaynet/static/bundles/"),
		filename: "[name]-[hash].js",
	},
	resolve: {
		modulesDirectories: ["node_modules"],
		extensions: ["", ".js", ".jsx", ".d.ts", ".ts", ".tsx"],
	},
	module: {
		loaders: [
			{
				test: /\.tsx?$/,
				loaders: [
					"babel-loader?presets[]=react&presets[]=es2015",
					"awesome-typescript-loader?disableFastEmit=true",
				],
			}
		],
	},
	externals: {
		"react": "React",
		"react-dom": "ReactDOM",
		"jquery": "jQuery",
	},
	plugins: [
		new BundleTracker({filename: "./build/webpack-stats.json"}),
		new webpack.DefinePlugin(settings),
	],
};
