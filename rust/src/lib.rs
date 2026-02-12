pub mod cli;
pub mod clients;
pub mod database_linker;
pub mod embeddings;
pub mod errors;
pub mod reactive;
pub mod schema;
pub mod security;
pub mod server;
pub mod table;
pub mod vector;

pub use clients::{Collection, ReactiveClient, VectorClient};
pub use database_linker::{DatabaseLinker, DatabaseType, DbLink, DiscoveredDbLink};
pub use embeddings::{
    get_embedding_function, EmbeddingFunction, OllamaEmbedding, OpenAIEmbedding,
    SentenceTransformerEmbedding,
};
pub use errors::{Result, SkypydbError};
pub use reactive::{DataMap, ReactiveDatabase};
pub use schema::{define_schema, define_table, value, Schema, TableDefinition, Validator};
pub use security::{EncryptionManager, InputValidator};
pub use server::{build_router, run_dashboard_server, DashboardApi};
pub use table::Table;
pub use vector::{CollectionInfo, VectorDatabase, VectorGetResult, VectorQueryResult};

#[macro_export]
macro_rules! columns {
    ($( $key:expr => $value:expr ),* $(,)?) => {{
        let mut map = ::std::collections::BTreeMap::new();
        $(
            map.insert($key.to_string(), $value);
        )*
        map
    }};
}

#[macro_export]
macro_rules! tables {
    ($( $key:expr => $value:expr ),* $(,)?) => {{
        let mut map = ::std::collections::BTreeMap::new();
        $(
            map.insert($key.to_string(), $value);
        )*
        map
    }};
}

#[macro_export]
macro_rules! json_map {
    ($( $key:expr => $value:expr ),* $(,)?) => {{
        let mut map = ::serde_json::Map::new();
        $(
            map.insert($key.to_string(), ::serde_json::json!($value));
        )*
        map
    }};
}
