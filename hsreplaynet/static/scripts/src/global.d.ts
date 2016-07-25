// various global module definitions
// this file should be picked up automatically by the typescript compiler

declare module "clipboard" {
	export default class Clipboard {
		constructor(selector: any, options?: any);
		destroy(): void;
		on(event: string, func: any): any;
	}
}
