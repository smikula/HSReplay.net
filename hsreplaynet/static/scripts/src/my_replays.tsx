import * as React from "react";
import * as ReactDOM from "react-dom";
import GameHistoryList from "./components/GameHistoryList";
import {image, cardArt} from "./helpers";



function renderReplayListing() {
	let r = $.getJSON("/api/v1/games", {username: $("body").data("username")}, function(data) {
		if (data.count) {
			ReactDOM.render(
				<GameHistoryList
					image={image}
					cardArt={cardArt}
					games={data["results"]}
				/>,
				document.getElementById("my-games-container")
			);
		}
	});
}

renderReplayListing();
