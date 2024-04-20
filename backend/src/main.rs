use axum::{
    extract::{
        ws::{self, WebSocket},
        WebSocketUpgrade,
    },
    response::Response,
    routing::get,
    Router,
};
use color_eyre::eyre::Result;
use tokio::{fs::File, io::AsyncWriteExt};
use tracing::*;

// TODO: auth routes?

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    // build our application with a route
    let app = Router::new().route("/", get(ws_test));

    // run it
    let listener = tokio::net::TcpListener::bind(":::3000").await.unwrap();
    info!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}

async fn ws_test(ws: WebSocketUpgrade) -> Response {
    ws.on_upgrade(|ws| async { _ = handle_ws(ws).await })
}

#[tracing::instrument(skip_all, err(Debug))]
async fn handle_ws(mut ws: WebSocket) -> Result<()> {
    info!("Got connection");

    let now = chrono::offset::Local::now();
    let mut f = File::create(&format!("{now}.webm")).await?;
    while let Some(res) = ws.recv().await {
        let msg = res?;
        match msg {
            ws::Message::Binary(new_data) => {
                info!("Got binary");
                f.write_all(&new_data).await?;
            }
            ws::Message::Close(_) => {
                info!("Connection closed");
                break;
            }
            _ => {}
        }
    }
    // TODO: Do some stuff with the data
    Ok(())
}
