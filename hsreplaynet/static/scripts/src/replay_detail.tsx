import * as React from "react";
import * as ReactDOM from "react-dom";
import ShareGameDialog from "./components/ShareGameDialog";

declare var onJoustSetting: (turn?: number, reveal?: boolean, swap?: boolean) => void;

let turn = null;
let reveal = null;
let swap = null;

function renderShareDialog() {
	ReactDOM.render(
		<ShareGameDialog url={$("#share-game-dialog").data("url")} showLinkToTurn={true}
						 turn={turn} reveal={reveal} swap={swap}/>,
		document.getElementById("share-game-dialog")
	);
}

onJoustSetting = (newTurn?: number, newReveal?: boolean, newSwap?: boolean): void => {
	if(typeof newTurn !== "undefined") {
		turn = newTurn;
	}
	if(typeof newReveal !== "undefined") {
		reveal = newReveal;
	}
	if(typeof newSwap !== "undefined") {
		swap = newSwap;
	}
	renderShareDialog();
};

renderShareDialog();
