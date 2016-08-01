import {MetricsBackend, Point} from "./MetricsBackend";


export default class BatchingMiddleware implements MetricsBackend {
	private backend: MetricsBackend;
	private points: Point[] = [];
	private interval: number = null;
	private timeout: number = 15 * 1000;

	constructor(backend: MetricsBackend, interval?: number) {
		this.backend = backend;
		if (interval) {
			this.timeout = interval;
		}
	}

	private _consume(async: boolean = true) {
		let points = this.points;
		this.points = [];
		this.backend.writePoints(points);
		if (async != this.backend["async"]) {
			this.backend["async"] = async;
		}
	}

	private _onPush() {
		if (this.interval) {
			return;
		}
		this.interval = window.setInterval(() => this._consume(), this.timeout);
		$(window).on("beforeunload", () => {
			let async = true;
			if (/Firefox\/\d+/.test(navigator.userAgent)) {
				// send final request synchronous in Firefox
				async = false;
			}
			this._consume(async);
		});
	}

	public writePoint(series: string, values: Object, tags?: Object) {
		let point: Point = {
			series: series,
			values: values,
		};
		if (tags) {
			point.tags = tags;
		}
		this.points.push(point);
		this._onPush();
	}

	public writePoints(points: Point[]) {
		this.points = this.points.concat(points);
		this._onPush();
	}
}
