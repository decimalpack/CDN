use std::{collections::HashMap, io::Read, thread::sleep};

use lazy_static::lazy_static;
use pretty_env_logger;
use tokio::sync::RwLock;
use warp::{
    hyper::{body::Bytes, StatusCode},
    Filter,
};
const BUFFER_SIZE: usize = 1 << 13;
const ORIGIN: &str = "http://cs5700cdnorigin.ccs.neu.edu:8080/";
lazy_static! {
    static ref RAM_CACHE: RwLock<HashMap<String, Vec<u8>>> = RwLock::new(HashMap::new());
}
#[tokio::main]
async fn main() {
    if std::env::var_os("RUST_LOG").is_none() {
        std::env::set_var("RUST_LOG", "server=debug");
    }
    pretty_env_logger::init_timed();
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
    warp::serve(routes).run(([0, 0, 0, 0], 25015)).await;
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

async fn fetch_from_origin(path: &str) -> Result<String, reqwest::Error> {
    dbg!(format!("Fetch: {}", &path));
    let response = reqwest::get(format!("{}{}", ORIGIN, path)).await?;
    return response.text().await;
}

async fn preload(body: String) -> Result<impl warp::Reply, warp::Rejection> {
    let mut ram_cache = RAM_CACHE.write().await;
    for path in body.split(";").into_iter() {
        let response = fetch_from_origin(&path).await.unwrap();
        ram_cache.insert(path.to_string(), compress(&response));
    }
    Ok(StatusCode::NO_CONTENT)
}

fn compress(content: &String) -> Vec<u8> {
    brotli::CompressorReader::new(content.as_bytes(), BUFFER_SIZE, 11, 24)
        .bytes()
        .map(|x| x.unwrap())
        .collect()
}

fn decompress(content: &Vec<u8>) -> String {
    let mut decompressed = String::new();
    brotli::Decompressor::new(&content[..], BUFFER_SIZE)
        .read_to_string(&mut decompressed)
        .expect("decompress failed");
    decompressed
}
async fn proxy(path: String) -> Result<impl warp::Reply, warp::Rejection> {
    sleep(std::time::Duration::from_secs(1));
    let ram_cache = RAM_CACHE.read().await;
    if ram_cache.contains_key(&path) {
        Ok(decompress(ram_cache.get(&path).unwrap()))
    } else {
        match tokio::fs::read(format!("./disk/{}", path)).await {
            Ok(content) => Ok(decompress(&content)),
            Err(_) => Ok(fetch_from_origin(&path).await.unwrap()),
        }
    }
}
