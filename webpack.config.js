"use strict";

const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const fs = require("fs");
const spawnSync = require("child_process").spawnSync;

const exportSettings = [
	"STATIC_URL", "JOUST_STATIC_URL", "HEARTHSTONE_ART_URL"
];

const isWindows = /^win/.test(process.platform);
const managePy = path.resolve(__dirname, "./manage.py")

let spawnCommand = isWindows ? "python" : managePy;
let spawnArgs = ["show_settings"].concat(exportSettings);
if (isWindows) {
	spawnArgs.splice(0, 0, managePy);
}

const exportedSettings = JSON.parse(
	spawnSync(spawnCommand, spawnArgs, {encoding: "utf-8"}).stdout
);
const settings = exportSettings.reduce((obj, current) => {
	obj[current] = JSON.stringify(exportedSettings[current]);
	return obj;
}, {});


module.exports = {
	context: __dirname,
	entry: {
		my_replays: path.resolve(__dirname, "./hsreplaynet/static/scripts/src/my_replays"),
		replay_detail: path.resolve(__dirname, "./hsreplaynet/static/scripts/src/replay_detail"),
	},
	output: {
		path: path.resolve(__dirname, "./hsreplaynet/static/bundles/"),
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
					"ts-loader",
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
		new BundleTracker({path: __dirname, filename: "./build/webpack-stats.json"}),
		new webpack.DefinePlugin(settings),
	],
};
