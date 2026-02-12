#[tokio::main]
async fn main() {
    if let Err(error) = skypydb::cli::run().await {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
