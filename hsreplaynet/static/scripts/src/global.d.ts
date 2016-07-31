// various global module definitions
// this file should be picked up automatically by the typescript compiler

declare module "clipboard" {
	export default class Clipboard {
		constructor(selector: any, options?: any);
		destroy(): void;
		on(event: string, func: any): any;
	}
}

declare var STATIC_URL;
declare var JOUST_STATIC_URL;
