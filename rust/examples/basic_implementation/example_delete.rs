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

    //Delete data from the table
    let deleted = success_table.delete(json_map! {
        "component" => "AuthService",
        "user_id" => "user123",
    })?;

    //Print the results
    if deleted.is_empty() {
        println!("No deleted data found.");
    } else {
        for item in deleted {
            println!("{item}");
        }
    }

    Ok(())
}