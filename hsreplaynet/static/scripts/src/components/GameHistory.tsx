import * as React from "react";


interface GameHistoryPlayerProps extends React.ClassAttributes<GameHistoryItem> {
	name: string;
	heroId: string;
	won: boolean;
}

interface GameHistoryPlayerState {}


export class GameHistoryPlayer extends React.Component<GameHistoryPlayerProps, GameHistoryPlayerState> {
	constructor(props: GameHistoryPlayerProps, context: any) {
		super(props, context);
	}

	render(): JSX.Element {
		return (<figure className={this.props.won ? "winner" : "loser"}>
			<img src={"https://static.hsreplay.net/static/joust/card-art/" + this.props.heroId + ".jpg"}/>
			<figcaption>{this.props.name}</figcaption>
		</figure>);
	}
}


interface GameHistoryItemProps extends React.ClassAttributes<GameHistoryItem> {
	shortid: string;
	players: Array<Object>;
	startTime: Date;
	endTime: Date;
	gameType: number;
	disconnected: boolean;
	turns: number;
	won: boolean;
}

interface GameHistoryItemState {}

function humanTime(seconds) {
	// TODO: use something better
	var days = Math.floor((seconds % 31536000) / 86400);
	var hours = Math.floor(((seconds % 31536000) % 86400) / 3600);
	var mins = Math.floor((((seconds % 31536000) % 86400) % 3600) / 60);
	if (days) {
		return days + " days";
	}
	if (hours) {
		return hours + " hours";
	}
	return mins + " minutes";
}

export class GameHistoryItem extends React.Component<GameHistoryItemProps, GameHistoryItemState> {
	constructor(props: GameHistoryItemProps, context: any) {
		super(props, context);
	}

	getDuration(): string {
		var seconds = this.props.endTime.getTime() - this.props.startTime.getTime();
		console.log(this.props.startTime, this.props.startTime.getTime());
		console.log(this.props.endTime, this.props.endTime.getTime());
		return humanTime(seconds / 1000);
	}

	getPlayedTime(): string {
		var seconds = new Date().getTime() - this.props.endTime.getTime();
		return humanTime(seconds / 1000) + " ago";
	}

	getIcon(): JSX.Element {
		if (this.props.disconnected) {
			return <img src="/static/images/dc.png" className="hsreplay-type" alt="Disconnected"/>;
		}
		if (this.props.gameType == 16) {
			return <img src="/static/images/brawl.png" className="hsreplay-type" alt="Tavern Brawl"/>;
		}
		return null;
	}

	render(): JSX.Element {
		return (<div className="col-xs-12 col-sm-6 col-md-4 col-lg-3 game-history-item">
			<a href={"/replay/" + this.props.shortid} className={this.props.won ? "won" : "lost"}>
				<div className="hsreplay-involved">
					<img src="/static/images/vs.png" className="hsreplay-versus"/>
					{this.props.players.map(function(player, i) {
						return <GameHistoryPlayer name={player["name"]} heroId={player["hero_id"]} won={player["final_state"] == 4}/>;
					})}
				</div>
				<div className="hsreplay-details">
					<dl>
						<dt>Played</dt>
						<dd>{this.getPlayedTime()}</dd>
						<dt>Duration</dt>
						<dd>{this.getDuration()}</dd>
						<dt>Turns</dt>
						<dd>{Math.floor(this.props.turns / 2)} turns</dd>
					</dl><div>
						{this.getIcon()}
					</div>
				</div>
			</a>
		</div>);
	}
}


interface GameHistoryListProps extends React.ClassAttributes<GameHistoryList> {
	games: Array<Object>;
}

interface GameHistoryListState {}

export default class GameHistoryList extends React.Component<GameHistoryListProps, GameHistoryListState> {

	constructor(props: GameHistoryListProps, context: any) {
		super(props, context);
	}

	render(): JSX.Element {
		return <div class="row">
			{this.props.games.map(
				function(game, i) {
					var startTime: Date = new Date(game["global_game"].match_start);
					var endTime: Date = new Date(game["global_game"].match_end);
					return <GameHistoryItem
						shortid={game["shortid"]}
						players={game["global_game"].players}
						startTime={startTime}
						endTime={endTime}
						gameType={game["global_game"].game_type}
						disconnected={game["disconnected"]}
						turns={game["global_game"].num_turns}
						won={game["won"]}
					/>;
				}
			)}
		</div>;
	}
}
