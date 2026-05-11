use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use serde::Deserialize;

const DEFAULT_BASE_URL: &str = "http://localhost:8010/api/fs";
const DEFAULT_CACHE_TTL: f64 = 30.0;

#[derive(Deserialize)]
struct EvaluateResponse {
    data: Option<HashMap<String, serde_json::Value>>,
}

fn now_secs() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

fn fetch_flags(
    api_key: &str,
    environment: &str,
    base_url: &str,
) -> Result<HashMap<String, serde_json::Value>, String> {
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(5))
        .build()
        .map_err(|e| format!("Failed to build HTTP client: {e}"))?;

    let response = client
        .get(format!("{base_url}/evaluate"))
        .header("X-Api-Key", api_key)
        .query(&[("environment", environment)])
        .send()
        .map_err(|e| format!("CONNECTION_ERROR:{e}"))?;

    match response.status().as_u16() {
        401 => return Err("INVALID_API_KEY:Invalid or inactive API key.".into()),
        404 => return Err(format!("ENV_NOT_FOUND:Environment '{environment}' not found for this project.")),
        200 => {}
        code => return Err(format!("CONNECTION_ERROR:Unexpected response from FlagSwitch: {code}")),
    }

    let payload: EvaluateResponse = response
        .json()
        .map_err(|e| format!("CONNECTION_ERROR:Failed to parse response: {e}"))?;

    Ok(payload.data.unwrap_or_default())
}

#[pyclass]
pub struct FlagSwitchCore {
    api_key: String,
    environment: String,
    base_url: String,
    cache_ttl: f64,
    cache: HashMap<String, serde_json::Value>,
    cache_ts: f64,
}

#[pymethods]
impl FlagSwitchCore {
    #[new]
    #[pyo3(signature = (api_key, environment, base_url=None, cache_ttl=None))]
    fn new(
        api_key: String,
        environment: String,
        base_url: Option<String>,
        cache_ttl: Option<f64>,
    ) -> Self {
        FlagSwitchCore {
            api_key,
            environment,
            base_url: base_url.unwrap_or_else(|| DEFAULT_BASE_URL.to_string()),
            cache_ttl: cache_ttl.unwrap_or(DEFAULT_CACHE_TTL),
            cache: HashMap::new(),
            cache_ts: 0.0,
        }
    }

    fn is_cache_valid(&self) -> bool {
        !self.cache.is_empty() && (now_secs() - self.cache_ts) < self.cache_ttl
    }

    fn refresh(&mut self) -> PyResult<()> {
        match fetch_flags(&self.api_key, &self.environment, &self.base_url) {
            Ok(flags) => {
                self.cache = flags;
                self.cache_ts = now_secs();
                Ok(())
            }
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn get_flags(&mut self) -> PyResult<HashMap<String, bool>> {
        if !self.is_cache_valid() {
            self.refresh()?;
        }
        let result = self
            .cache
            .iter()
            .map(|(k, v)| (k.clone(), v.as_bool().unwrap_or(false)))
            .collect();
        Ok(result)
    }

    fn is_enabled(&mut self, key: &str, default: bool) -> PyResult<bool> {
        if !self.is_cache_valid() {
            self.refresh()?;
        }
        Ok(self
            .cache
            .get(key)
            .and_then(|v| v.as_bool())
            .unwrap_or(default))
    }

    fn invalidate_cache(&mut self) {
        self.cache.clear();
        self.cache_ts = 0.0;
    }
}

#[pymodule]
fn flagswitch_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FlagSwitchCore>()?;
    Ok(())
}
