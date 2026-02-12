use std::error::Error;
use std::fmt::{Display, Formatter};

pub type Result<T> = std::result::Result<T, SkypydbError>;

#[derive(Debug, Clone)]
pub struct SkypydbError {
    code: &'static str,
    message: String,
}

impl SkypydbError {
    pub fn new(code: &'static str, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
        }
    }

    pub fn code(&self) -> &'static str {
        self.code
    }

    pub fn message(&self) -> &str {
        &self.message
    }

    pub fn table_not_found(message: impl Into<String>) -> Self {
        Self::new("SKY101", message)
    }

    pub fn table_already_exists(message: impl Into<String>) -> Self {
        Self::new("SKY102", message)
    }

    pub fn database(message: impl Into<String>) -> Self {
        Self::new("SKY103", message)
    }

    pub fn invalid_search(message: impl Into<String>) -> Self {
        Self::new("SKY201", message)
    }

    pub fn security(message: impl Into<String>) -> Self {
        Self::new("SKY301", message)
    }

    pub fn validation(message: impl Into<String>) -> Self {
        Self::new("SKY302", message)
    }

    pub fn encryption(message: impl Into<String>) -> Self {
        Self::new("SKY303", message)
    }

    pub fn collection_not_found(message: impl Into<String>) -> Self {
        Self::new("SKY401", message)
    }

    pub fn collection_already_exists(message: impl Into<String>) -> Self {
        Self::new("SKY402", message)
    }

    pub fn embedding(message: impl Into<String>) -> Self {
        Self::new("SKY403", message)
    }

    pub fn vector_search(message: impl Into<String>) -> Self {
        Self::new("SKY404", message)
    }
}

impl Display for SkypydbError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl Error for SkypydbError {}

impl From<rusqlite::Error> for SkypydbError {
    fn from(value: rusqlite::Error) -> Self {
        Self::database(value.to_string())
    }
}

impl From<serde_json::Error> for SkypydbError {
    fn from(value: serde_json::Error) -> Self {
        Self::database(value.to_string())
    }
}

impl From<std::io::Error> for SkypydbError {
    fn from(value: std::io::Error) -> Self {
        Self::database(value.to_string())
    }
}

impl From<reqwest::Error> for SkypydbError {
    fn from(value: reqwest::Error) -> Self {
        Self::embedding(value.to_string())
    }
}
