use clap::Parser;

#[derive(Debug, Parser)]
#[command(name = "skypydb-dashboard", about = "Run Skypydb dashboard API server")]
struct Args {
    #[arg(long, default_value = "0.0.0.0")]
    host: String,
    #[arg(long, default_value_t = 8000)]
    port: u16,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    if let Err(error) = skypydb::server::run_dashboard_server(&args.host, args.port).await {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
