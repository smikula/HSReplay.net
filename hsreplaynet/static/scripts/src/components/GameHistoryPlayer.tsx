import * as React from "react";


interface GameHistoryPlayerProps extends React.ClassAttributes<GameHistoryPlayer> {
	name: string;
	heroId: string;
	won: boolean;
}

interface GameHistoryPlayerState {}

export default class GameHistoryPlayer extends React.Component<GameHistoryPlayerProps, GameHistoryPlayerState> {
	constructor(props: GameHistoryPlayerProps, context: any) {
		super(props, context);
	}

	render(): JSX.Element {
		return (<figure className={this.props.won ? "winner" : "loser"}>
			<img src={JOUST_STATIC_URL + "card-art/" + this.props.heroId + ".jpg"}/>
			<figcaption>{this.props.name}</figcaption>
		</figure>);
	}
}
