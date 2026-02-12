//! Dashboard API for monitoring Skypydb databases.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use crate::database_linker::DatabaseLinker;
use crate::errors::{Result, SkypydbError};
use crate::reactive::{DataMap, ReactiveDatabase};
use crate::vector::{VectorDatabase, VectorGetResult, VectorQueryResult};

#[derive(Clone, Default)]
pub struct DashboardApi {
    pub health: HealthApi,
    pub tables: TableApi,
    pub vector: VectorApi,
    pub statistics: StatisticsApi,
    pub links: LinksApi,
}

impl DashboardApi {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn get_summary(&self, main_path: Option<&str>, vector_path: Option<&str>) -> Value {
        let health = self.health.check(main_path, vector_path);
        let stats = self.statistics.get_all(main_path, vector_path);

        json!({
            "status": health.get("status").cloned().unwrap_or(Value::String("degraded".to_string())),
            "timestamp": health.get("timestamp").cloned().unwrap_or_else(|| json!(now_nanos())),
            "summary": {
                "tables": stats.get("tables").cloned().unwrap_or_else(|| json!({})),
                "collections": stats.get("collections").cloned().unwrap_or_else(|| json!({})),
            },
            "health_details": health.get("databases").cloned().unwrap_or_else(|| json!({})),
            "database_links": self.links.list_all(),
        })
    }
}

#[derive(Clone, Default)]
pub struct LinksApi;

impl LinksApi {
    pub fn list_all(&self) -> Value {
        json!(DatabaseConnection::discover_links())
    }
}

#[derive(Clone, Default)]
pub struct HealthApi;

impl HealthApi {
    pub fn check(&self, main_path: Option<&str>, vector_path: Option<&str>) -> Value {
        let mut status = json!({
            "timestamp": now_nanos(),
            "status": "healthy",
            "databases": {},
        });

        self.check_main(&mut status, main_path);
        self.check_vector(&mut status, vector_path);
        status
    }

    fn check_main(&self, status: &mut Value, main_path: Option<&str>) {
        let database_result = DatabaseConnection::get_main(main_path);
        let database_status = match database_result {
            Ok(database) => {
                let table_count = database.get_all_tables_names().map(|tables| tables.len());
                match table_count {
                    Ok(table_count) => json!({
                        "status": "connected",
                        "tables": table_count,
                    }),
                    Err(error) => {
                        set_degraded_status(status);
                        json!({
                            "status": "error",
                            "error": error.to_string(),
                        })
                    }
                }
            }
            Err(error) => {
                set_degraded_status(status);
                json!({
                    "status": "error",
                    "error": error.to_string(),
                })
            }
        };

        if let Some(databases) = status.get_mut("databases").and_then(Value::as_object_mut) {
            databases.insert("main".to_string(), database_status);
        }
    }

    fn check_vector(&self, status: &mut Value, vector_path: Option<&str>) {
        let database_result = DatabaseConnection::get_vector(vector_path);
        let database_status = match database_result {
            Ok(database) => {
                let collection_count = database
                    .list_collections()
                    .map(|collections| collections.len());
                match collection_count {
                    Ok(collection_count) => json!({
                        "status": "connected",
                        "collections": collection_count,
                    }),
                    Err(error) => {
                        set_degraded_status(status);
                        json!({
                            "status": "error",
                            "error": error.to_string(),
                        })
                    }
                }
            }
            Err(error) => {
                set_degraded_status(status);
                json!({
                    "status": "error",
                    "error": error.to_string(),
                })
            }
        };

        if let Some(databases) = status.get_mut("databases").and_then(Value::as_object_mut) {
            databases.insert("vector".to_string(), database_status);
        }
    }
}

#[derive(Clone, Default)]
pub struct TableApi;

impl TableApi {
    pub fn list_all(&self, main_path: Option<&str>) -> Result<Value> {
        let database = DatabaseConnection::get_main(main_path)?;
        let table_names = database.get_all_tables_names()?;

        let mut result = Vec::new();
        for table_name in table_names {
            result.push(self.get_info(&database, &table_name));
        }

        Ok(Value::Array(result))
    }

    pub fn get_schema(&self, table_name: &str, main_path: Option<&str>) -> Result<Value> {
        let database = DatabaseConnection::get_main(main_path)?;

        Ok(json!({
            "name": table_name,
            "columns": database.get_table_columns_names(table_name)?,
            "config": database.get_table_config(table_name)?,
        }))
    }

    pub fn get_data(
        &self,
        table_name: &str,
        limit: usize,
        offset: usize,
        main_path: Option<&str>,
    ) -> Result<Value> {
        let database = DatabaseConnection::get_main(main_path)?;
        let all_data = database.get_all_data(table_name)?;
        Ok(self.paginate(all_data, limit, offset))
    }

    pub fn search(
        &self,
        table_name: &str,
        query: Option<String>,
        limit: usize,
        filters: Option<DataMap>,
        main_path: Option<&str>,
    ) -> Result<Value> {
        let database = DatabaseConnection::get_main(main_path)?;
        let mut results =
            database.search(table_name, query.as_deref(), &filters.unwrap_or_default())?;

        if limit > 0 && results.len() > limit {
            results.truncate(limit);
        }

        Ok(json!({
            "data": results,
            "total": results.len(),
            "limit": limit,
        }))
    }

    fn get_info(&self, database: &ReactiveDatabase, table_name: &str) -> Value {
        let row_count = database
            .get_all_data(table_name)
            .map(|rows| rows.len())
            .unwrap_or_default();
        let columns = database
            .get_table_columns_names(table_name)
            .unwrap_or_default();
        let config = database.get_table_config(table_name).ok().flatten();

        json!({
            "name": table_name,
            "row_count": row_count,
            "columns": columns,
            "config": config,
        })
    }

    fn paginate(&self, data: Vec<DataMap>, limit: usize, offset: usize) -> Value {
        let total = data.len();
        let start = offset.min(total);
        let end = if limit == 0 {
            total
        } else {
            (offset + limit).min(total)
        };

        json!({
            "data": data[start..end].to_vec(),
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": end < total,
        })
    }
}

#[derive(Clone, Default)]
pub struct VectorApi;

impl VectorApi {
    pub fn list_all(&self, vector_path: Option<&str>) -> Result<Value> {
        let database = DatabaseConnection::get_vector(vector_path)?;
        let collections = database.list_collections()?;

        let result = collections
            .into_iter()
            .map(|collection| {
                let document_count = database.count(&collection.name).unwrap_or_default();
                json!({
                    "name": collection.name,
                    "document_count": document_count,
                    "metadata": collection.metadata,
                })
            })
            .collect::<Vec<_>>();

        Ok(Value::Array(result))
    }

    pub fn get_details(&self, collection_name: &str, vector_path: Option<&str>) -> Value {
        let database = match DatabaseConnection::get_vector(vector_path) {
            Ok(database) => database,
            Err(error) => {
                return json!({
                    "name": collection_name,
                    "exists": false,
                    "error": error.to_string(),
                });
            }
        };

        match database.get_collection(collection_name) {
            Ok(Some(collection)) => json!({
                "name": collection_name,
                "exists": true,
                "document_count": database.count(collection_name).unwrap_or_default(),
                "metadata": collection.metadata,
            }),
            Ok(None) => json!({
                "name": collection_name,
                "exists": false,
                "error": "Collection not found",
            }),
            Err(error) => json!({
                "name": collection_name,
                "exists": false,
                "error": error.to_string(),
            }),
        }
    }

    pub fn get_documents(
        &self,
        collection_name: &str,
        document_ids: Option<Vec<String>>,
        metadata_filter: Option<Value>,
        limit: usize,
        offset: usize,
        vector_path: Option<&str>,
    ) -> Value {
        let database = match DatabaseConnection::get_vector(vector_path) {
            Ok(database) => database,
            Err(error) => {
                return json!({
                    "ids": [],
                    "documents": [],
                    "metadatas": [],
                    "total": 0,
                    "error": error.to_string(),
                });
            }
        };

        let result = database.get(
            collection_name,
            document_ids,
            metadata_filter,
            None,
            Some(vec!["documents".to_string(), "metadatas".to_string()]),
        );

        match result {
            Ok(result) => self.paginate_get_result(result, limit, offset),
            Err(error) => json!({
                "ids": [],
                "documents": [],
                "metadatas": [],
                "total": 0,
                "error": error.to_string(),
            }),
        }
    }

    pub fn search(
        &self,
        collection_name: &str,
        query_text: &str,
        n_results: usize,
        metadata_filter: Option<Value>,
        vector_path: Option<&str>,
    ) -> Value {
        let database = match DatabaseConnection::get_vector(vector_path) {
            Ok(database) => database,
            Err(error) => {
                return json!({
                    "results": [],
                    "query": query_text,
                    "error": error.to_string(),
                });
            }
        };

        let result = database.query(
            collection_name,
            None,
            Some(vec![query_text.to_string()]),
            n_results,
            metadata_filter,
            None,
            Some(vec![
                "documents".to_string(),
                "metadatas".to_string(),
                "distances".to_string(),
            ]),
        );

        match result {
            Ok(result) => self.format_query_result(result, query_text, n_results),
            Err(error) => json!({
                "results": [],
                "query": query_text,
                "error": error.to_string(),
            }),
        }
    }

    fn paginate_get_result(&self, result: VectorGetResult, limit: usize, offset: usize) -> Value {
        let total = result.ids.len();
        let start = offset.min(total);
        let end = if limit == 0 {
            total
        } else {
            (offset + limit).min(total)
        };

        let ids = result.ids[start..end].to_vec();
        let documents = result
            .documents
            .unwrap_or_default()
            .into_iter()
            .skip(start)
            .take(end - start)
            .collect::<Vec<_>>();
        let metadatas = result
            .metadatas
            .unwrap_or_default()
            .into_iter()
            .skip(start)
            .take(end - start)
            .collect::<Vec<_>>();

        json!({
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": end < total,
        })
    }

    fn format_query_result(
        &self,
        result: VectorQueryResult,
        query_text: &str,
        n_results: usize,
    ) -> Value {
        let ids = result.ids.first().cloned().unwrap_or_default();
        let documents = result
            .documents
            .as_ref()
            .and_then(|documents| documents.first().cloned())
            .unwrap_or_default();
        let metadatas = result
            .metadatas
            .as_ref()
            .and_then(|metadatas| metadatas.first().cloned())
            .unwrap_or_default();
        let distances = result
            .distances
            .as_ref()
            .and_then(|distances| distances.first().cloned())
            .unwrap_or_default();

        let mut formatted = Vec::new();
        for (index, id) in ids.iter().enumerate() {
            formatted.push(json!({
                "id": id,
                "document": documents.get(index).cloned().unwrap_or(None),
                "metadata": metadatas.get(index).cloned().unwrap_or(None),
                "similarity_score": distances.get(index).copied().unwrap_or_default(),
            }));
        }

        json!({
            "results": formatted,
            "query": query_text,
            "n_results": n_results,
        })
    }
}

#[derive(Clone, Default)]
pub struct StatisticsApi;

impl StatisticsApi {
    pub fn get_all(&self, main_path: Option<&str>, vector_path: Option<&str>) -> Value {
        let mut stats = json!({
            "timestamp": now_nanos(),
            "tables": {
                "count": 0,
                "total_rows": 0,
            },
            "collections": {
                "count": 0,
                "total_documents": 0,
            },
        });

        self.collect_tables(&mut stats, main_path);
        self.collect_collections(&mut stats, vector_path);
        stats
    }

    fn collect_tables(&self, stats: &mut Value, main_path: Option<&str>) {
        let outcome = (|| -> Result<(usize, usize)> {
            let database = DatabaseConnection::get_main(main_path)?;
            let table_names = database.get_all_tables_names()?;
            let total_rows = table_names
                .iter()
                .map(|table| database.get_all_data(table).map(|rows| rows.len()))
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .sum::<usize>();
            Ok((table_names.len(), total_rows))
        })();

        match outcome {
            Ok((count, total_rows)) => {
                if let Some(table_stats) = stats.get_mut("tables").and_then(Value::as_object_mut) {
                    table_stats.insert("count".to_string(), json!(count));
                    table_stats.insert("total_rows".to_string(), json!(total_rows));
                }
            }
            Err(error) => {
                if let Some(table_stats) = stats.get_mut("tables").and_then(Value::as_object_mut) {
                    table_stats.insert("error".to_string(), json!(error.to_string()));
                }
            }
        }
    }

    fn collect_collections(&self, stats: &mut Value, vector_path: Option<&str>) {
        let outcome = (|| -> Result<(usize, usize)> {
            let database = DatabaseConnection::get_vector(vector_path)?;
            let collections = database.list_collections()?;
            let total_documents = collections
                .iter()
                .map(|collection| database.count(&collection.name))
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .sum::<usize>();
            Ok((collections.len(), total_documents))
        })();

        match outcome {
            Ok((count, total_documents)) => {
                if let Some(collection_stats) =
                    stats.get_mut("collections").and_then(Value::as_object_mut)
                {
                    collection_stats.insert("count".to_string(), json!(count));
                    collection_stats.insert("total_documents".to_string(), json!(total_documents));
                }
            }
            Err(error) => {
                if let Some(collection_stats) =
                    stats.get_mut("collections").and_then(Value::as_object_mut)
                {
                    collection_stats.insert("error".to_string(), json!(error.to_string()));
                }
            }
        }
    }
}

struct DatabaseConnection;

impl DatabaseConnection {
    fn discover_links() -> Vec<Value> {
        let linker = DatabaseLinker::default();
        linker
            .discover_database_links(Some(Path::new(".")))
            .into_iter()
            .map(|entry| {
                json!({
                    "type": entry.db_type,
                    "path": entry.path,
                    "metadata_file": entry.metadata_file,
                })
            })
            .collect()
    }

    fn get_main(path_override: Option<&str>) -> Result<ReactiveDatabase> {
        let path = Self::resolve_db_path(
            path_override,
            "SKYPYDB_PATH",
            "db/_generated/skypydb.db",
            "reactive",
        )?;
        Self::require_existing(&path, "Main")?;
        ReactiveDatabase::new(path, None, None, None)
    }

    fn get_vector(path_override: Option<&str>) -> Result<VectorDatabase> {
        let path = Self::resolve_db_path(
            path_override,
            "SKYPYDB_VECTOR_PATH",
            "db/_generated/vector.db",
            "vector",
        )?;
        Self::require_existing(&path, "Vector")?;
        VectorDatabase::new(path, None)
    }

    fn resolve_db_path(
        override_path: Option<&str>,
        env_key: &str,
        default_relative: &str,
        db_type: &str,
    ) -> Result<String> {
        if let Some(path) = override_path {
            return Ok(resolve_absolute(path).to_string_lossy().to_string());
        }

        if let Ok(path) = std::env::var(env_key) {
            return Ok(resolve_absolute(path).to_string_lossy().to_string());
        }

        let linker = DatabaseLinker::default();
        for entry in linker.discover_database_links(Some(Path::new("."))) {
            if entry.db_type != db_type {
                continue;
            }
            let candidate = PathBuf::from(&entry.path);
            if candidate.exists() {
                return Ok(candidate.to_string_lossy().to_string());
            }
        }

        let default_path = resolve_absolute(default_relative);
        if default_path.exists() {
            return Ok(default_path.to_string_lossy().to_string());
        }

        let generated_dir = resolve_absolute("db/_generated");
        if generated_dir.exists() {
            let mut candidates = generated_dir
                .read_dir()
                .map_err(|error| SkypydbError::database(error.to_string()))?
                .flatten()
                .map(|entry| entry.path())
                .filter(|path| {
                    path.is_file() && path.extension().and_then(|ext| ext.to_str()) == Some("db")
                })
                .collect::<Vec<_>>();
            candidates.sort();
            if let Some(first) = candidates.first() {
                return Ok(first.to_string_lossy().to_string());
            }
        }

        Ok(default_path.to_string_lossy().to_string())
    }

    fn require_existing(path: &str, label: &str) -> Result<()> {
        if !Path::new(path).exists() {
            return Err(SkypydbError::database(format!(
                "{label} database file not found at: {path}. Set the correct path with request headers or environment variables."
            )));
        }
        Ok(())
    }
}

fn resolve_absolute(path: impl AsRef<Path>) -> PathBuf {
    let path = path.as_ref();
    if path.is_absolute() {
        return path.to_path_buf();
    }

    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let candidate = cwd.join(path);
    candidate.canonicalize().unwrap_or(candidate)
}

fn now_nanos() -> i64 {
    chrono::Utc::now().timestamp_nanos_opt().unwrap_or_default()
}

fn set_degraded_status(status: &mut Value) {
    if let Some(value) = status.get_mut("status") {
        *value = Value::String("degraded".to_string());
    }
}
