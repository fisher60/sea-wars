import { Component } from "react";
import Banner from "./playerDataBanner";
import Loading from "./loadingScrean";

export default class Game extends Component {
    constructor(props) {
        super(props);

        this.state = {
            ws: null,
            dataFromServer: null
        };
    }

    componentDidMount() {
        this.connect();
    }

    timeout = 250; // Initial timeout duration 
    currentReconnectAttempts = 0;
    maxRecconnectAttempts = 10;

    /**
     * @function connect
     * This function establishes the connect with the websocket and also ensures constant reconnection if connection closes
     */
    connect = () => {
        var ws = new WebSocket("ws://localhost:8000/ws");
        let that = this; // cache the this
        var connectInterval;

        // websocket onopen event listener
        ws.onopen = () => {
            that.timeout = 250; // reset timer to 250 on open of websocket connection 
            clearTimeout(connectInterval); // clear Interval on on open of websocket connection
        };

        ws.onmessage = evt => {
            // listen to data sent from the websocket server
            const message = JSON.parse(evt.data)
            this.setState({dataFromServer: message})
            
            if (document.cookie === ""){
                document.cookie = `token=${this.state.dataFromServer.message.player.uuid}`
            }
        };

        // websocket onclose event listener
        ws.onclose = e => {
            if (this.currentReconnectAttempts < this.maxRecconnectAttempts){
                this.currentReconnectAttempts += 1;
                console.log(
                    `Socket is closed. Reconnect will be attempted in ${Math.min(
                        10000 / 1000,
                        (that.timeout + that.timeout) / 1000
                    )} second.`,
                    e.reason
                );
                that.timeout = that.timeout + that.timeout; //increment retry interval
                connectInterval = setTimeout(this.check, Math.min(10000, that.timeout)); //call check function after timeout
            }
        };

        // websocket onerror event listener
        ws.onerror = err => {
            console.error(
                "Socket encountered error: ",
                err.message,
                "Closing socket"
            );

            ws.close();
        };
    };

    check = () => {
        const { ws } = this.state;
        if (!ws || ws.readyState === WebSocket.CLOSED){
            this.connect(); //check if websocket instance is closed, if so call `connect` function.
        } 
        else{
            this.currentReconnectAttempts = 0;
        }
    };

    render() {
        if (this.state.dataFromServer){
            return (
                <div>
                    <h1 className="text-3xl font-bold underline">Hello Fish</h1>
                    <Banner player={ this.state.dataFromServer.message.player } />
                    <p>Data: { JSON.stringify(this.state.dataFromServer) }</p>
                </div>
            )
        }
        else {
            return (
                <Loading />
            )
        }
    }
}