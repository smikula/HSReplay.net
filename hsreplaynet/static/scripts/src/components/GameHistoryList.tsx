import * as React from "react";
import GameHistoryItem from "./GameHistoryItem";
import {GameReplay, CardArtProps, ImageProps, GlobalGamePlayer} from "../interfaces";
import GameHistorySearch from "./GameHistorySearch";


interface GameHistoryListProps extends ImageProps, CardArtProps, React.ClassAttributes<GameHistoryList> {
	games: GameReplay[];
}

interface GameHistoryListState {
	query?: string;
}

export default class GameHistoryList extends React.Component<GameHistoryListProps, GameHistoryListState> {

	constructor(props: GameHistoryListProps, context: any) {
		super(props, context);
		this.state = {
			query: document.location.hash.substr(1) || "",
		}
	}

	componentDidUpdate(prevProps: GameHistoryListProps, prevState: GameHistoryListState, prevContext: any): void {
		location.replace("#" + this.state.query);
	}

	render(): JSX.Element {
		let columns = [];
		let terms = this.state.query.toLowerCase().split(" ").map((word: string) => word.trim()).filter((word: string) => {
			return !!word;
		});
		this.props.games.filter((game: GameReplay): boolean => {
			if (!terms.length) {
				return true;
			}
			let matchingPlayer = false;
			game.global_game.players.forEach((player: GlobalGamePlayer): void => {
				let name = player.name.toLowerCase();
				terms.forEach((term: string) => {
					if (name.startsWith(term)) {
						matchingPlayer = true;
					}
				});
			});
			let matchingBuild = false;
			terms.forEach((term: string) => {
				if (+term && game.build == +term) {
					matchingBuild = true;
				}
			});
			if (matchingPlayer || matchingBuild) {
				return true;
			}
			return false;
		}).forEach((game: GameReplay, i: number) => {
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
			<div className="row">
				<div className="col-lg-2 col-lg-push-10">
					<GameHistorySearch
						query={this.state.query}
						setQuery={(query: string) => this.setState({query: query})}
					/>
				</div>
				<div className="col-lg-10 col-lg-pull-2">
					<div className="row">
						{columns}
					</div>
				</div>
			</div>
		);
	}
}
