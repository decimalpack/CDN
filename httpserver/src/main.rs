use futures::{self, FutureExt};
use lazy_static::lazy_static;
use pretty_env_logger;
use std::{collections::HashMap, io::Read};
use tokio::sync::RwLock;
use warp::{
    hyper::{body::Bytes, StatusCode},
    Filter,
};
const BUFFER_SIZE: usize = 1 << 13;
lazy_static! {
    static ref RAM_CACHE: RwLock<HashMap<String, Vec<u8>>> = RwLock::new(HashMap::new());
    static ref ORIGIN: RwLock<String> = RwLock::new(String::new());
}

#[tokio::main]
async fn main() {
    if std::env::var_os("RUST_LOG").is_none() {
        std::env::set_var("RUST_LOG", "server=info");
    }
    pretty_env_logger::init_timed();

    let mut args = std::env::args();

    let port = args
        .nth(2)
        .expect("Port must be provided")
        .parse::<u16>()
        .expect("port must be a number");
    let origin = args.nth(1).expect("Origin must be provided");
    ORIGIN.write().await.push_str(&origin);

    let ping = warp::post()
        .and(warp::path!("ping"))
        .and(warp::body::bytes())
        .map(|body: Bytes| String::from_utf8_lossy(&body).to_string())
        .and_then(ping);

    let beacon = warp::path!("grading" / "beacon").map(|| StatusCode::NO_CONTENT);
    let preload = warp::path!("preload")
        .and(warp::body::bytes())
        .map(|body: Bytes| String::from_utf8_lossy(&body).to_string())
        .and_then(preload);
    let root = warp::path::end().and_then(|| proxy(String::new()));
    let proxy = warp::path!(String).and_then(proxy);

    let routes = root
        .or(preload)
        .or(beacon)
        .or(ping)
        .or(proxy)
        .with(warp::log("server"));
    warp::serve(routes).run(([0, 0, 0, 0], port)).await;
}
async fn ping(ip_list: String) -> Result<impl warp::Reply, warp::Rejection> {
    let scamper = std::process::Command::new("scamper")
        .args(["-i", "-O", "json", "-c", "ping -c 1"])
        .args(ip_list.split_whitespace())
        .output();
    match scamper {
        Ok(output) => Ok(warp::reply::with_status(
            String::from_utf8_lossy(&output.stdout).to_string(),
            StatusCode::OK,
        )),
        Err(e) => Ok(warp::reply::with_status(
            e.to_string(),
            StatusCode::INTERNAL_SERVER_ERROR,
        )),
    }
}

async fn fetch_from_origin(path: &str) -> String {
    log::debug!("Fetching from origin: {}", path);
    let url = format!("{}/{}", ORIGIN.read().await, path);
    let mut response = reqwest::get(&url)
        .await
        .expect(format!("GET {} fail", path).as_str());
    while response.status().is_server_error() {
        log::info!("{} - status {}, retrying in 10s", path, response.status());
        tokio::time::sleep(std::time::Duration::from_secs(10)).await;
        response = reqwest::get(&url).await.expect(
            format!(
                "GET {} fail second time - status {}",
                path,
                response.status()
            )
            .as_str(),
        );
    }
    return response.text().await.unwrap();
}

async fn preload(body: String) -> Result<impl warp::Reply, warp::Rejection> {
    tokio::spawn(async move {
        for path in body.split(";").filter(|&x| x != "").map(|x| x.to_string()) {
            let compressed = fetch_from_origin(path.as_str()).then(compress).await;
            log::debug!("Cached {} in RAM w/Size = {}", path, compressed.len());
            RAM_CACHE.write().await.insert(path, compressed);
        }
        RAM_CACHE.write().await.shrink_to_fit();
        log::info!(
            "Preload finished; RAM usage {}",
            RAM_CACHE
                .read()
                .await
                .values()
                .map(|v| v.len())
                .sum::<usize>()
        );
    });
    Ok(StatusCode::NO_CONTENT)
}

async fn compress(content: String) -> Vec<u8> {
    brotli::CompressorReader::new(content.as_bytes(), BUFFER_SIZE, 11, 22)
        .bytes()
        .map(|x| x.unwrap())
        .collect()
}

async fn decompress(content: &Vec<u8>) -> String {
    let mut decompressed = String::new();
    brotli::Decompressor::new(&content[..], BUFFER_SIZE)
        .read_to_string(&mut decompressed)
        .expect("decompress failed");
    decompressed
}

async fn proxy(path: String) -> Result<impl warp::Reply, warp::Rejection> {
    // tokio::time::sleep(std::time::Duration::from_millis(1314)).await;
    if let Ok(ram_cache) = RAM_CACHE.try_read() {
        if let Some(compressed) = ram_cache.get(&path) {
            log::info!("RAM hit {}", path);
            return Ok(warp::reply::html(decompress(&compressed).await));
        }
    }
    if let Ok(compressed) = tokio::fs::read(format!("./disk/{}", path)).await {
        log::info!("DISK hit {}", path);
        Ok(warp::reply::html(decompress(&compressed).await))
    } else {
        let response = fetch_from_origin(path.as_str()).await;
        log::info!("Fetched from origin: {}", path);
        Ok(warp::reply::html(response))
    }
}
