//! HTTP server for the dashboard API.

use axum::extract::{Path, Query, State};
use axum::http::{HeaderMap, StatusCode};
use axum::routing::{get, post};
use axum::{Json, Router};
use serde::Deserialize;
use serde_json::{json, Value};
use tower_http::cors::{Any, CorsLayer};

use crate::errors::{Result, SkypydbError};

use super::dashboard_api::DashboardApi;

#[derive(Clone)]
struct AppState {
    api: DashboardApi,
}

type ApiResponse = std::result::Result<Json<Value>, (StatusCode, Json<Value>)>;

#[derive(Debug, Deserialize)]
struct TableDataQuery {
    limit: Option<usize>,
    offset: Option<usize>,
}

#[derive(Debug, Deserialize)]
struct TableSearchQuery {
    query: Option<String>,
    limit: Option<usize>,
}

#[derive(Debug, Deserialize)]
struct CollectionDocumentsBody {
    limit: Option<usize>,
    offset: Option<usize>,
    document_ids: Option<Vec<String>>,
    metadata_filter: Option<Value>,
}

#[derive(Debug, Deserialize)]
struct CollectionSearchBody {
    query_text: Option<String>,
    n_results: Option<usize>,
    metadata_filter: Option<Value>,
}

pub fn build_router(api: DashboardApi) -> Router {
    let state = AppState { api };

    Router::new()
        .route("/api/health", get(health_check))
        .route("/api/summary", get(get_summary))
        .route("/api/statistics", get(get_statistics))
        .route("/api/databaselinks", get(get_database_links))
        .route("/api/tables", get(list_tables))
        .route("/api/tables/:table_name/schema", get(get_table_schema))
        .route("/api/tables/:table_name/data", get(get_table_data))
        .route("/api/tables/:table_name/search", get(search_table))
        .route("/api/collections", get(list_collections))
        .route(
            "/api/collections/:collection_name",
            get(get_collection_details),
        )
        .route(
            "/api/collections/:collection_name/documents",
            post(get_collection_documents),
        )
        .route(
            "/api/collections/:collection_name/search",
            post(search_vectors),
        )
        .layer(
            CorsLayer::new()
                .allow_origin(
                    "http://localhost:3000"
                        .parse::<axum::http::HeaderValue>()
                        .expect("valid origin"),
                )
                .allow_methods(Any)
                .allow_headers(Any),
        )
        .with_state(state)
}

pub async fn run_dashboard_server(host: &str, port: u16) -> Result<()> {
    let api = DashboardApi::new();
    let app = build_router(api);

    let address = format!("{host}:{port}");
    let listener = tokio::net::TcpListener::bind(&address)
        .await
        .map_err(|error| SkypydbError::database(error.to_string()))?;

    axum::serve(listener, app)
        .await
        .map_err(|error| SkypydbError::database(error.to_string()))
}

async fn health_check(State(state): State<AppState>, headers: HeaderMap) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    let vector_path = header_value(&headers, "x-skypydb-vector-path");

    Ok(Json(
        state
            .api
            .health
            .check(main_path.as_deref(), vector_path.as_deref()),
    ))
}

async fn get_summary(State(state): State<AppState>, headers: HeaderMap) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    let vector_path = header_value(&headers, "x-skypydb-vector-path");

    Ok(Json(
        state
            .api
            .get_summary(main_path.as_deref(), vector_path.as_deref()),
    ))
}

async fn get_statistics(State(state): State<AppState>, headers: HeaderMap) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    let vector_path = header_value(&headers, "x-skypydb-vector-path");

    Ok(Json(
        state
            .api
            .statistics
            .get_all(main_path.as_deref(), vector_path.as_deref()),
    ))
}

async fn get_database_links(State(state): State<AppState>) -> ApiResponse {
    Ok(Json(state.api.links.list_all()))
}

async fn list_tables(State(state): State<AppState>, headers: HeaderMap) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    state
        .api
        .tables
        .list_all(main_path.as_deref())
        .map(Json)
        .map_err(internal_error)
}

async fn get_table_schema(
    State(state): State<AppState>,
    Path(table_name): Path<String>,
    headers: HeaderMap,
) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    state
        .api
        .tables
        .get_schema(&table_name, main_path.as_deref())
        .map(Json)
        .map_err(internal_error)
}

async fn get_table_data(
    State(state): State<AppState>,
    Path(table_name): Path<String>,
    Query(params): Query<TableDataQuery>,
    headers: HeaderMap,
) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    let limit = params.limit.unwrap_or(100);
    let offset = params.offset.unwrap_or(0);

    state
        .api
        .tables
        .get_data(&table_name, limit, offset, main_path.as_deref())
        .map(Json)
        .map_err(internal_error)
}

async fn search_table(
    State(state): State<AppState>,
    Path(table_name): Path<String>,
    Query(params): Query<TableSearchQuery>,
    headers: HeaderMap,
) -> ApiResponse {
    let main_path = header_value(&headers, "x-skypydb-path");
    let limit = params.limit.unwrap_or(100);

    state
        .api
        .tables
        .search(&table_name, params.query, limit, None, main_path.as_deref())
        .map(Json)
        .map_err(internal_error)
}

async fn list_collections(State(state): State<AppState>, headers: HeaderMap) -> ApiResponse {
    let vector_path = header_value(&headers, "x-skypydb-vector-path");
    state
        .api
        .vector
        .list_all(vector_path.as_deref())
        .map(Json)
        .map_err(internal_error)
}

async fn get_collection_details(
    State(state): State<AppState>,
    Path(collection_name): Path<String>,
    headers: HeaderMap,
) -> ApiResponse {
    let vector_path = header_value(&headers, "x-skypydb-vector-path");
    Ok(Json(
        state
            .api
            .vector
            .get_details(&collection_name, vector_path.as_deref()),
    ))
}

async fn get_collection_documents(
    State(state): State<AppState>,
    Path(collection_name): Path<String>,
    headers: HeaderMap,
    Json(body): Json<CollectionDocumentsBody>,
) -> ApiResponse {
    let vector_path = header_value(&headers, "x-skypydb-vector-path");
    let limit = body.limit.unwrap_or(100);
    let offset = body.offset.unwrap_or(0);

    Ok(Json(state.api.vector.get_documents(
        &collection_name,
        body.document_ids,
        body.metadata_filter,
        limit,
        offset,
        vector_path.as_deref(),
    )))
}

async fn search_vectors(
    State(state): State<AppState>,
    Path(collection_name): Path<String>,
    headers: HeaderMap,
    Json(body): Json<CollectionSearchBody>,
) -> ApiResponse {
    let vector_path = header_value(&headers, "x-skypydb-vector-path");
    let query_text = body.query_text.unwrap_or_default();
    let n_results = body.n_results.unwrap_or(10);

    Ok(Json(state.api.vector.search(
        &collection_name,
        &query_text,
        n_results,
        body.metadata_filter,
        vector_path.as_deref(),
    )))
}

fn header_value(headers: &HeaderMap, name: &str) -> Option<String> {
    headers
        .get(name)
        .and_then(|value| value.to_str().ok())
        .map(|value| value.to_string())
}

fn internal_error(error: SkypydbError) -> (StatusCode, Json<Value>) {
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({
            "detail": error.to_string(),
        })),
    )
}
