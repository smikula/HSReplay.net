import * as React from "react";
import * as ReactDOM from "react-dom";
import GameHistoryList from "./components/GameHistory";


function renderReplayListing() {
	let r = $.getJSON("/api/v1/games", {username: $("body").data("username")}, function(data) {
		console.log(data)
		if (data.count) {
			ReactDOM.render(
				<GameHistoryList games={data["results"]}/>,
				document.getElementById("my-games-container")
			);
		}
	});
}

renderReplayListing();
