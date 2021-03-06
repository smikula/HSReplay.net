import * as React from "react";
import GameHistoryItem from "./GameHistoryItem";
import {GameReplay, CardArtProps, ImageProps} from "../interfaces";


interface GameHistoryListProps extends ImageProps, CardArtProps, React.ClassAttributes<GameHistoryList> {
	games: GameReplay[];
}

interface GameHistoryListState {
}

export default class GameHistoryList extends React.Component<GameHistoryListProps, GameHistoryListState> {

	constructor(props: GameHistoryListProps, context: any) {
		super(props, context);
	}

	render(): JSX.Element {
		let columns = [];
		this.props.games.forEach((game: GameReplay, i: number) => {
			var startTime: Date = new Date(game.global_game.match_start);
			var endTime: Date = new Date(game.global_game.match_end);
			if (i > 0) {
				if (!(i % 2)) {
					columns.push(<div className="clearfix visible-sm-block"></div>);
				}
				if (!(i % 3)) {
					columns.push(<div className="clearfix visible-md-block"></div>);
				}
				if (!(i % 4)) {
					columns.push(<div className="clearfix visible-lg-block"></div>);
				}
			}
			columns.push(
				<GameHistoryItem
					key={i}
					cardArt={this.props.cardArt}
					image={this.props.image}
					shortid={game.shortid}
					players={game.global_game.players}
					startTime={startTime}
					endTime={endTime}
					gameType={game.global_game.game_type}
					disconnected={game.disconnected}
					turns={game.global_game.num_turns}
					won={game.won}
				/>
			);
		});
		return (
			<div class="row">
				{columns}
			</div>
		);
	}
}
