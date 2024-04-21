# syntax=docker/dockerfile:1.5

FROM rust:1.77.2 as build

RUN cargo new backend
COPY ./Cargo.toml ./Cargo.lock /backend/

WORKDIR /backend
RUN --mount=type=cache,target=/usr/local/cargo/registry cargo build --release

ENV AI_SERVER_ADDR 107.218.158.102:3001

COPY ./src /backend/src
RUN --mount=type=cache,target=/usr/local/cargo/registry <<EOF
  set -e
  touch /backend/src/main.rs
  cargo build --release
EOF

ENTRYPOINT [ "/backend/target/release/backend" ]
