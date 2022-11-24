import { Component } from "react";

export default class Banner extends Component {

    render() {
        return (
            <div className="border-2 rounded border-slate-300">
                <h1>Player: { this.props.player.uuid }</h1>
                <div className="flex gap-2">
                    <span>Money: { this.props.player.money }</span>
                    <span>Money: { this.props.player.money }</span>
                </div>
            </div>
        )
    }
}