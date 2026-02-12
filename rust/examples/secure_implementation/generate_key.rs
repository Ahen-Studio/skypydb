// you can generate a secure encryption key and salt using the cli
// or generate a secure encryption key and salt using the this example code
use base64::engine::general_purpose::STANDARD as BASE64_STANDARD;
use base64::Engine;
use skypydb::{EncryptionManager, Result};

fn main() -> Result<()> {
    let key = EncryptionManager::generate_key();
    let salt = EncryptionManager::generate_salt(32)?;

    println!("ENCRYPTION_KEY={key}");
    println!("SALT_KEY={}", BASE64_STANDARD.encode(salt));

    Ok(())
}