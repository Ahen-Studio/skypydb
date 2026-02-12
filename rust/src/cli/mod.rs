//! Command-line interface for Skypydb.

use std::fs;
use std::io::Write;
use std::path::Path;

use base64::engine::general_purpose::STANDARD as BASE64_STANDARD;
use base64::Engine;
use clap::{Parser, Subcommand};
use dialoguer::Select;

use crate::errors::{Result, SkypydbError};
use crate::security::EncryptionManager;
use crate::server::run_dashboard_server;

#[derive(Debug, Parser)]
#[command(
    name = "skypydbrust",
    about = "Skypydb CLI - Reactive and Vector Embedding Database",
    version
)]
pub struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Debug, Subcommand)]
pub enum Commands {
    /// Interactive mode.
    Dev,
    /// Initialize project files and encryption keys.
    Init,
    /// Start dashboard API server.
    Dashboard {
        #[arg(long, default_value = "0.0.0.0")]
        host: String,
        #[arg(long, default_value_t = 8000)]
        port: u16,
    },
    /// Alias for dashboard command.
    Serve {
        #[arg(long, default_value = "0.0.0.0")]
        host: String,
        #[arg(long, default_value_t = 8000)]
        port: u16,
    },
    /// Print a new encryption key and salt.
    Keygen,
}

pub async fn run() -> Result<()> {
    let cli = Cli::parse();

    match cli.command.unwrap_or(Commands::Dev) {
        Commands::Dev => run_dev().await,
        Commands::Init => init_project(),
        Commands::Dashboard { host, port } | Commands::Serve { host, port } => {
            println!("Starting Skypydb dashboard API on http://{host}:{port}");
            run_dashboard_server(&host, port).await
        }
        Commands::Keygen => {
            print_keys()?;
            Ok(())
        }
    }
}

async fn run_dev() -> Result<()> {
    let options = vec![
        "create a new project",
        "launch the dashboard api server",
        "no thanks",
    ];

    let choice = Select::new()
        .with_prompt("Welcome to Skypydb! What would you like to do?")
        .items(&options)
        .default(0)
        .interact_opt()
        .map_err(|error| SkypydbError::database(error.to_string()))?;

    match choice {
        Some(0) => init_project(),
        Some(1) => run_dashboard_server("0.0.0.0", 8000).await,
        _ => {
            println!("Exiting.");
            Ok(())
        }
    }
}

fn init_project() -> Result<()> {
    let cwd = std::env::current_dir().map_err(|error| SkypydbError::database(error.to_string()))?;

    let db_dir = cwd.join("db");
    let generated_dir = db_dir.join("_generated");
    let schema_file = db_dir.join("schema.rs");

    fs::create_dir_all(&generated_dir)
        .map_err(|error| SkypydbError::database(error.to_string()))?;

    if !schema_file.exists() {
        fs::write(&schema_file, schema_template())
            .map_err(|error| SkypydbError::database(error.to_string()))?;
    }

    write_env_file(&cwd)?;
    update_gitignore(&cwd)?;

    println!("Initialized project.");
    println!("Write your Skypydb schema in {}", schema_file.display());
    println!("Use `skypydbrust dashboard` to run the dashboard API server.");

    Ok(())
}

fn print_keys() -> Result<()> {
    let encryption_key = EncryptionManager::generate_key();
    let salt = EncryptionManager::generate_salt(32)?;

    println!("ENCRYPTION_KEY={encryption_key}");
    println!("SALT_KEY={}", BASE64_STANDARD.encode(salt));
    Ok(())
}

fn write_env_file(cwd: &Path) -> Result<()> {
    let encryption_key = EncryptionManager::generate_key();
    let salt = EncryptionManager::generate_salt(32)?;

    let content = format!(
        "ENCRYPTION_KEY={encryption_key}\nSALT_KEY={}\n",
        BASE64_STANDARD.encode(salt)
    );

    let env_path = cwd.join(".env.local");
    fs::write(env_path, content).map_err(|error| SkypydbError::database(error.to_string()))
}

fn update_gitignore(cwd: &Path) -> Result<()> {
    let gitignore_path = cwd.join(".gitignore");

    let mut lines = if gitignore_path.exists() {
        fs::read_to_string(&gitignore_path)
            .map_err(|error| SkypydbError::database(error.to_string()))?
            .lines()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
    } else {
        Vec::new()
    };

    if !lines.iter().any(|line| line.trim() == ".env.local") {
        lines.push(".env.local".to_string());
        let mut file = fs::File::create(&gitignore_path)
            .map_err(|error| SkypydbError::database(error.to_string()))?;
        let body = if lines.is_empty() {
            String::new()
        } else {
            format!("{}\n", lines.join("\n"))
        };
        file.write_all(body.as_bytes())
            .map_err(|error| SkypydbError::database(error.to_string()))?;
    }

    Ok(())
}

fn schema_template() -> String {
    let mut lines = Vec::<String>::new();
    lines.push("use skypydb::schema::value;".to_string());
    lines.push(
        "use skypydb::{columns, define_schema, define_table, tables, Result, Schema};".to_string(),
    );
    lines.push(String::new());
    lines.push("pub fn build_schema() -> Result<Schema> {".to_string());
    lines.push("    let example = define_table(columns! {".to_string());
    lines.push("        \"message\" => value::string(),".to_string());
    lines.push("        \"source\" => value::optional(value::string()),".to_string());
    lines.push("    })".to_string());
    lines.push("    .index(\"by_source\", vec![\"source\"])?;".to_string());
    lines.push(String::new());
    lines.push("    Ok(define_schema(tables! {".to_string());
    lines.push("        \"example\" => example,".to_string());
    lines.push("    }))".to_string());
    lines.push("}".to_string());
    lines.join("\n")
}
