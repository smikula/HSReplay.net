import * as React from "react";
import Clipboard from "clipboard";

interface ShareGameDialogProps extends React.ClassAttributes<ShareGameDialog> {
	url: string;
	turn: number;
}

interface ShareGameDialogState {
	linkToTurn?: boolean;
	confirming?: boolean;
}

export default class ShareGameDialog extends React.Component<ShareGameDialogProps, ShareGameDialogState> {

	private clipboard: Clipboard;
	private input: HTMLInputElement;
	private timeout: number = null;

	constructor(props: ShareGameDialogProps, context: any) {
		super(props, context);
		this.state = {
			linkToTurn: false,
			confirming: false,
		};
	}

	componentDidMount(): void {
		this.clipboard = new Clipboard("#replay-share-copy-url", {
			text: (elem): string => this.buildUrl()
		});
		this.clipboard.on("success", () => {
			this.setState({confirming: true});
			window.clearTimeout(this.timeout);
			this.timeout = window.setTimeout(() => {
				this.setState({confirming: false});
				this.timeout = null;
			}, 1000);
		});
	}

	componentWillUnmount(): void {
		this.clipboard.destroy();
		window.clearTimeout(this.timeout);
	}

	protected buildUrl(): string {
		let url = this.props.url;
		if (this.props.turn && this.state.linkToTurn) {
			url += "#turn=" + Math.ceil(this.props.turn / 2) + (this.props.turn % 2 ? "a" : "b");
		}
		return url;
	}

	protected onChangeLinkToTurn(e): void {
		this.setState({linkToTurn: !this.state.linkToTurn});
	}

	render(): JSX.Element {
		return <form>
			<div className="input-group">
				<input type="text" readonly id="replay-share-url" className="form-control"
					   value={this.buildUrl()}
					   onSelect={(e) => this.input.setSelectionRange(0, this.input.value.length)}
					   ref={(node) => this.input = node}/>
				<span className="input-group-btn">
                     <button className="btn btn-default" id="replay-share-copy-url"
							 type="button">{this.state.confirming ? "Copied!" : "Copy"}</button>
                </span>
			</div>
			<fieldset>
				<div className="checkbox">
					<label>
						<input type="checkbox" id="replay-share-link-turn" checked={this.state.linkToTurn}
							   onChange={(e) => this.onChangeLinkToTurn(e)}/> Start at current turn
					</label>
				</div>
			</fieldset>
		</form>;
	}
}
