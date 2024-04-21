use std::time::Duration;

use axum::{
    extract::{
        ws::{self, WebSocket},
        WebSocketUpgrade,
    },
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use color_eyre::eyre::Result;
use futures::{
    stream::{SplitSink, SplitStream},
    SinkExt, StreamExt,
};
use serde_json::json;
use thiserror::Error;
use tokio::{net::TcpStream, select, time::Interval};
use tokio_tungstenite::{tungstenite, MaybeTlsStream, WebSocketStream};
use tower_http::cors::CorsLayer;
use tracing::*;

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    // build our application with a route
    let app = Router::new()
        .route("/", get(ws_test))
        .route("/request", post(request))
        .layer(CorsLayer::very_permissive());

    // run it
    let listener = tokio::net::TcpListener::bind(":::3000").await.unwrap();
    info!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();

    Ok(())
}

async fn request(Json(json): Json<serde_json::Value>) -> impl IntoResponse {
    info!("Got value: {json}")
}

async fn ws_test(ws: WebSocketUpgrade) -> Response {
    ws.on_upgrade(|ws| async {
        if let Err(e) = handle_ws(ws).await {
            error!("Error when handling websocket: {e:?}");
        }
    })
}

const AI_SERVER_ADDR: &str = std::env!("AI_SERVER_ADDR");

#[derive(Debug, Error)]
enum HandleError {
    #[error("Wrong state")]
    WrongState,
    #[error("Connection timed out")]
    Timeout,
    #[error("Connection failed")]
    Failed,
    #[error("Websocket closed")]
    Closed,
    #[error("Websocket EOF")]
    Eof,
}

#[derive(Debug)]
enum HandleState {
    Data,
    Response,
    Done,
}

async fn handle_ws(mut ws: WebSocket) -> Result<()> {
    info!("Got connection");
    let Ok(connect_res) = tokio::time::timeout(
        Duration::from_secs(10),
        tokio_tungstenite::connect_async(AI_SERVER_ADDR),
    )
    .await
    else {
        info!("AI side websocket connection timed out");
        ws.send(ws::Message::Text(
            json!({ "success": false, "error": "Connection to AI timed out" }).to_string(),
        ))
        .await?;
        return Err(HandleError::Timeout.into());
    };
    let Ok((ai_ws, _)) = connect_res else {
        info!("AI side websocket connection failed");
        ws.send(ws::Message::Text(
            json!({ "success": false, "error": "Connection to AI failed" }).to_string(),
        ))
        .await?;
        return Err(HandleError::Failed.into());
    };
    info!("Connected to AI side");
    let (ai_tx, ai_rx) = ai_ws.split();
    let state = HandleState::Data;
    let ping_interval = tokio::time::interval(Duration::from_secs(5));

    HandleWs {
        ws,
        ai_tx,
        ai_rx,
        state,
        ping_interval,
    }
    .run()
    .await?;

    Ok(())
}

type WsStream = WebSocketStream<MaybeTlsStream<TcpStream>>;
struct HandleWs {
    ws: WebSocket,
    ai_tx: SplitSink<WsStream, tungstenite::Message>,
    ai_rx: SplitStream<WsStream>,
    state: HandleState,
    ping_interval: Interval,
}

impl HandleWs {
    async fn run(mut self) -> Result<()> {
        while !matches!(self.state, HandleState::Done) {
            select! {
                res = self.ws.recv() => {
                    let Some(res) = res else {
                        return Err(HandleError::Eof.into());
                    };
                    let msg = res?;
                    self.handle_client_msg(msg).await?;
                }
                res = self.ai_rx.next() => {
                    let Some(res) = res else {
                        return Err(HandleError::Eof.into());
                    };
                    let msg = res?;
                    self.handle_ai_msg(msg).await?;
                }
                _ = self.ping_interval.tick() => {
                    self.ai_tx.send(tungstenite::Message::Ping(vec![])).await?;
                }
            }
        }
        info!("Exiting run loop");
        Ok(())
    }

    async fn handle_client_msg(&mut self, msg: ws::Message) -> Result<()> {
        match msg {
            ws::Message::Binary(data) => {
                if !matches!(self.state, HandleState::Data) {
                    // ignore
                    return Ok(());
                }
                info!("Got binary data");
                self.ai_tx.send(tungstenite::Message::Binary(data)).await?;
            }
            ws::Message::Text(_) => {
                let HandleState::Data = &self.state else {
                    return Err(HandleError::WrongState.into());
                };
                info!("Got end of data");
                self.ai_tx
                    .send(tungstenite::Message::Binary(vec![]))
                    .await?;
                self.state = HandleState::Response;
            }
            ws::Message::Close(_) => {
                info!("Client websocket closed");
                return Err(HandleError::Closed.into());
            }
            _ => {}
        }
        Ok(())
    }

    async fn handle_ai_msg(&mut self, msg: tungstenite::Message) -> Result<()> {
        match msg {
            tungstenite::Message::Text(res) => {
                let HandleState::Response = &self.state else {
                    return Err(HandleError::WrongState.into());
                };
                info!("Sending response: {res}");
                self.ws.send(ws::Message::Text(res)).await?;
                self.state = HandleState::Done;
            }
            tungstenite::Message::Ping(_) => {
                self.ai_tx.send(tungstenite::Message::Pong(vec![])).await?;
            }
            tungstenite::Message::Close(_) => {
                info!("AI websocket closed");
                return Err(HandleError::Closed.into());
            }
            _ => {}
        }
        Ok(())
    }
}
