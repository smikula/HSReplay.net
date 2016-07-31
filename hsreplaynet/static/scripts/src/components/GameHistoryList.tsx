import * as React from "react";
import GameHistoryItem from "./GameHistoryItem";
import {GameReplay, CardArtProps, ImageProps} from "../interfaces";


interface GameHistoryListProps extends ImageProps, CardArtProps, React.ClassAttributes<GameHistoryList> {
	games: GameReplay[];
}

interface GameHistoryListState {}

export default class GameHistoryList extends React.Component<GameHistoryListProps, GameHistoryListState> {

	constructor(props: GameHistoryListProps, context: any) {
		super(props, context);
	}

	render(): JSX.Element {
		return <div class="row">
			{this.props.games.map(
				(game: GameReplay, i: number) => {
					var startTime: Date = new Date(game.global_game.match_start);
					var endTime: Date = new Date(game.global_game.match_end);
					return <GameHistoryItem
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
					/>;
				}
			)}
		</div>;
	}
}
