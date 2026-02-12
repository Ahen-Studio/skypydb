#[path = "../basic_implementation/schema.rs"]
//Load the schema file
mod schema;

use base64::engine::general_purpose::STANDARD as BASE64_STANDARD;
use base64::Engine;
use dotenv::from_filename;
use skypydb::{json_map, ReactiveClient, Result, SkypydbError};

fn main() -> Result<()> {
    // Load environment variables from .env.local file
    let _ = from_filename(".env.local");

    // Load encryption key from environment. Fail if not found
    let encryption_key = std::env::var("ENCRYPTION_KEY")
        .ok_or_else(|| {
            SkypydbError::validation("Missing ENCRYPTION_KEY. Set it in environment or .env.local.")
        })?;

    // Load salt key from environment. Fail if not found
    let salt_encoded = std::env::var("SALT_KEY")
        .ok_or_else(|| {
            SkypydbError::validation("Missing SALT_KEY. Set it in environment or .env.local.")
        })?;

    // Decode salt from base64
    let salt = BASE64_STANDARD
        .decode(salt_encoded)
        .map_err(|error| SkypydbError::validation(format!("Invalid SALT_KEY: {error}")))?;

    //Create a new client with encryption field set
    let client = ReactiveClient::new(
        "./db/_generated/skypydb_secure_rust.db",
        Some(encryption_key),
        Some(salt),
        Some(vec!["message".to_string()]),
    )?;
    let schema = schema::build_schema()?;

    //Get or create tables from the schema
    let tables = client.get_or_create_tables(&schema)?;

    //Error handling for tables
    let success_table = tables
        .get("success")
        .ok_or_else(|| skypydb::SkypydbError::table_not_found("Table 'success' not found"))?;

    //Add data to the tables
    let inserted = success_table.add(json_map! {
        "component" => "AuthService",
        "action" => "login",
        "message" => "User logged in successfully",
        "user_id" => "user123",
    })?;
    println!("Inserted: {inserted:?}");

    //Search for data
    let results = success_table.search(
        None,
        json_map! {
            "user_id" => "user123",
        },
    )?;

    //Print results
    println!("Decrypted results:");
    for result in results {
        println!("{result}");
    }

    Ok(())
}