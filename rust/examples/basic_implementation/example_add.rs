#[path = "schema.rs"]
//Load the schema file
mod schema;

use skypydb::{json_map, ReactiveClient, Result};

fn main() -> Result<()> {
    //Create a new client
    let client = ReactiveClient::new("./db/_generated/skypydb_rust.db", None, None, None)?;
    let schema = schema::build_schema()?;

    //Get or create tables from the schema
    let tables = client.get_or_create_tables(&schema)?;

    //Error handling for tables
    let success_table = tables
        .get("success")
        .ok_or_else(|| skypydb::SkypydbError::table_not_found("Table 'success' not found"))?;
    let warning_table = tables
        .get("warning")
        .ok_or_else(|| skypydb::SkypydbError::table_not_found("Table 'warning' not found"))?;
    let error_table = tables
        .get("error")
        .ok_or_else(|| skypydb::SkypydbError::table_not_found("Table 'error' not found"))?;

    //Add data to the tables
    let success_ids = success_table.add(json_map! {
        "component" => "AuthService",
        "action" => "login",
        "message" => "User logged in successfully",
        "user_id" => "user123",
    })?;

    let warning_ids = warning_table.add(json_map! {
        "component" => "AuthService",
        "action" => "login_attempt",
        "message" => "Multiple failed login attempts",
        "user_id" => "user456",
        "details" => "5 failed attempts in 5 minutes",
    })?;

    let error_ids = error_table.add(json_map! {
        "component" => "DatabaseService",
        "action" => "connection",
        "message" => "Connection timeout",
        "user_id" => "system",
        "details" => "Timeout after 30 seconds",
    })?;

    //Search for data in the table
    let inserted_success = success_table.search(
        None,
        json_map! {
            "id" => success_ids.clone(),
        },
    )?;
    let inserted_warning = warning_table.search(
        None,
        json_map! {
            "id" => warning_ids.clone(),
        },
    )?;
    let inserted_error = error_table.search(
        None,
        json_map! {
            "id" => error_ids.clone(),
        },
    )?;

    //Print the results
    for row in inserted_success {
        println!("  [success] {row:?}");
    }
    for row in inserted_warning {
        println!("  [warning] {row:?}");
    }
    for row in inserted_error {
        println!("  [error]   {row:?}");
    }

    Ok(())
}