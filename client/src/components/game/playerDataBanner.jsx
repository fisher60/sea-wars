import { Component } from "react";

export default class Banner extends Component {

    render() {
        return (
            <div>
                <h1>Player Banner</h1>
                <div>
                    <ul>
                        <li>Money: {this.props.player ? this.props.player.money : "loading"}</li>
                    </ul>
                </div>
            </div>
        )
    }
}