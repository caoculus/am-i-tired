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
// use sqlx::{postgres::PgPoolOptions, PgPool};
use tokio::{fs::File, io::AsyncWriteExt};
use tower_http::cors::CorsLayer;
use tracing::*;

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
