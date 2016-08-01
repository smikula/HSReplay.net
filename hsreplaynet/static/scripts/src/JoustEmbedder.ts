import * as Joust from "joust";
import Raven from "raven-js";
import {joustAsset, cardArt} from "./helpers";
import {EventEmitter} from "events";
import MetaDataManager from "./metadata/MetaDataManager";
import LocalStorageBackend from "./metadata/LocalStorageBackend";
import MetricsReporter from "./metrics/MetricsReporter";
import BatchingMiddleware from "./metrics/BatchingMiddleware";
import InfluxMetricsBackend from "./metrics/InfluxMetricsBackend";

export default class JoustEmbedder extends EventEmitter {
	public turn: number = null;
	public reveal: boolean = null;
	public swap: boolean = null;
	public locale: string = "enUS";

	public embed(targetId: string) {
		// find container
		let target = $("#" + targetId);
		if (!target) {
			throw new Error('Could not find target container with id "' + targetId + '"');
		}

		// setup RavenJS/Sentry
		let logger = null;
		let dsn = JOUST_RAVEN_DSN_PUBLIC;
		if (dsn) {
			let raven = Raven.config(dsn, {
				release: Joust.release(),
				environment: "development", // @todo from config
			} as any); // until typings are updated for environment
			logger = (err: string|Error) => {
				if (raven) {
					if (typeof err === "string") {
						raven.captureMessage(err);
					}
					else {
						raven.captureException(err);
					}
				}
				let message = err["message"] ? err["message"] : err;
				console.error(message);
			};
		}

		let launcher = Joust.launcher(targetId);
		if (logger) {
			launcher.logger(logger);
		}

		// setup graphics
		launcher.assets((asset: string) => joustAsset(asset));
		launcher.cardArt((cardId: string) => cardArt(cardId));

		// setup metadata
		let manager = new MetaDataManager((build: number|"latest", locale: string): string => {
			return HEARTHSTONEJSON_URL.replace(/%\(build\)s/, "" + build).replace(/%\(locale\)s/, locale);
		}, new LocalStorageBackend(), this.locale);
		launcher.metadata((build: number|null, cb: (data: any[]) => void): void => {
			manager.get(+build || "latest", (data: any[]): void => {
				cb(data);
			});
		});

		// setup influx
		let endpoint = "https://metrics.hearthsim.net:8086/write?db=hsreplaynet&u=joust&p=JeF5pgjs6GKwx8PU&precision=s"; //@todo from config
		let metrics = new MetricsReporter(
			new BatchingMiddleware(new InfluxMetricsBackend(endpoint)),
			(series: string): string => "joust_" + series
		);
		launcher.events((series, values, tags) => metrics.writePoint(series, values, tags));

		// turn linking
		if (this.turn !== null) {
			launcher.startAtTurn(this.turn);
		}
		launcher.onTurn((newTurn: number) => {
			this.turn = newTurn;
			this.emit("turn", newTurn);
		});

		if (this.reveal !== null) {
			launcher.startRevealed(this.reveal);
		}
		launcher.onToggleReveal((newReveal: boolean) => {
			this.reveal = newReveal;
			this.emit("reveal", newReveal);
		});

		if (this.swap !== null) {
			launcher.startSwapped(this.swap);
		}
		launcher.onToggleSwap((newSwap: boolean) => {
			this.swap = newSwap;
			this.emit("swap", newSwap);
		});

		// initialize joust
		let url = target.data("replayurl");
		launcher.fromUrl(url);
	}
}
