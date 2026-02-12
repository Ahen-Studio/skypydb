use skypydb::schema::value;
use skypydb::{columns, define_schema, define_table, tables, Result, Schema};

pub fn build_schema() -> Result<Schema> {
    let success = define_table(columns! {
        "component" => value::string(),
        "action" => value::string(),
        "message" => value::string(),
        "details" => value::optional(value::string()),
        "user_id" => value::optional(value::string()),
    })
    .index("by_component", vec!["component"])?
    .index("by_action", vec!["action"])?
    .index("by_user", vec!["user_id"])?
    .index("by_component_and_action", vec!["component", "action"])?;

    let warning = define_table(columns! {
        "component" => value::string(),
        "action" => value::string(),
        "message" => value::string(),
        "details" => value::optional(value::string()),
        "user_id" => value::optional(value::string()),
    })
    .index("by_component", vec!["component"])?
    .index("by_action", vec!["action"])?
    .index("by_user", vec!["user_id"])?
    .index("by_component_and_action", vec!["component", "action"])?;

    let error = define_table(columns! {
        "component" => value::string(),
        "action" => value::string(),
        "message" => value::string(),
        "details" => value::optional(value::string()),
        "user_id" => value::optional(value::string()),
    })
    .index("by_component", vec!["component"])?
    .index("by_action", vec!["action"])?
    .index("by_user", vec!["user_id"])?
    .index("by_component_and_action", vec!["component", "action"])?;

    Ok(define_schema(tables! {
        "success" => success,
        "warning" => warning,
        "error" => error,
    }))
}