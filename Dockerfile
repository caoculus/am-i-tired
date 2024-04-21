# syntax=docker/dockerfile:1.5

FROM rust:1.77.2 as build1

RUN cargo new backend
COPY ./backend/Cargo.toml ./backend/Cargo.lock /backend/

WORKDIR /backend
RUN --mount=type=cache,target=/usr/local/cargo/registry cargo build --release

ENV AI_SERVER_ADDR 107.218.158.102:3001

COPY ./backend/src /backend/src
RUN --mount=type=cache,target=/usr/local/cargo/registry <<EOF
  set -e
  touch /backend/src/main.rs
  cargo build --release
EOF

FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
COPY ./frontend /frontend
WORKDIR /frontend


FROM base AS prod-deps
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile

FROM base as build2
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
RUN pnpm run build

FROM base
COPY --from=build1 /backend/target/release/backend /backend-bin
COPY --from=prod-deps /frontend/app/node_modules /frontend/app/node_modules
COPY --from=build2 /frontend/dist /frontend/dist

EXPOSE 3000 8080

# TODO: This needs to be a shell script
CMD ["/backend-bin"]
