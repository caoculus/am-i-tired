use std::time::Duration;

use axum::{
    extract::{
        ws::{self, WebSocket},
        Query, WebSocketUpgrade,
    },
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use color_eyre::eyre::Result;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use tokio::{net::TcpStream, select, time::Interval};
use tokio_tungstenite::{tungstenite, MaybeTlsStream, WebSocketStream};
// use sqlx::{postgres::PgPoolOptions, PgPool};
// use tokio::{fs::File, io::AsyncWriteExt};
use futures::{
    stream::{SplitSink, SplitStream},
    SinkExt, StreamExt,
};
use tower_http::cors::CorsLayer;
use tracing::*;

// TODO: Let's do some simple authentication?

// #[derive(Clone)]
// struct AppState {
//     user_db: PgPool,
// }

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    // let conn_url = std::env!("DATABASE_URL");
    // let user_db = PgPoolOptions::new()
    //     .max_connections(5)
    //     .connect(conn_url)
    //     .await?;
    // sqlx::migrate!("./migrations").run(&user_db).await?;

    // build our application with a route
    let app = Router::new()
        .route("/", get(ws_test))
        .route("/request", post(request))
        .layer(CorsLayer::very_permissive());
    // .with_state(AppState { user_db });

    // TODO: What requests are we even receiving in the first place?

    // run it
    let listener = tokio::net::TcpListener::bind(":::3000").await.unwrap();
    info!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();

    Ok(())
}

async fn request(Json(json): Json<serde_json::Value>) -> impl IntoResponse {
    info!("Got value: {json}")
}

#[derive(Deserialize)]
struct UserQuery {
    user: String,
}

async fn ws_test(ws: WebSocketUpgrade) -> Response {
    ws.on_upgrade(|ws| async {
        if let Err(e) = handle_ws(ws).await {
            error!("Error when handling websocket: {e:?}");
        }
    })
}

// TODO: More stuff here!
// Forward things to another server

// const AI_SERVER_ADDR: &str = "ws://107.218.158.102:3001";
const AI_SERVER_ADDR: &str = "ws://localhost:3001";

#[derive(Debug, Error)]
enum HandleError {
    #[error("Wrong state")]
    WrongState,
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

async fn handle_ws(ws: WebSocket) -> Result<()> {
    info!("Got connection");
    let (ai_ws, _) = tokio_tungstenite::connect_async(AI_SERVER_ADDR).await?;
    info!("Connected to ai side");
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

// TODO: no more option, we need to send data back

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
                self.ai_tx.send(tungstenite::Message::Binary(vec![])).await?;
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
