import * as React from "react";
import * as ReactDOM from "react-dom";
import ShareGameDialog from "./components/ShareGameDialog";

declare var onJoustTurn: (turn: number) => void;

let turn = null;

function renderShareDialog() {
	ReactDOM.render(
		<ShareGameDialog url={$("#share-game-dialog").data("url")} turn={turn}/>,
		document.getElementById("share-game-dialog")
	);
}

onJoustTurn = (newTurn: number): void => {
	turn = newTurn;
	renderShareDialog();
};

renderShareDialog();
