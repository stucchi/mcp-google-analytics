# Google Analytics 4 MCP Server

MCP server for Google Analytics 4 — create properties, configure data streams, manage conversions, and run reports via the Admin & Data APIs.

## Setup (one-time, ~3 minutes)

1. **Google Cloud Console** → [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Create a service account (any name)
   - Click it → Keys → Add Key → JSON → Download

2. **Enable APIs** in your GCP project:
   - [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
   - [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)

3. **GA4 Admin** → Property Access Management → Add the service account email (from the JSON) as **Editor**

4. **Configure credentials** (pick one):
   - **Option A** (recommended): Copy the JSON content into the `GA_CREDENTIALS` env var in your MCP config
   - **Option B**: Save the file to `~/.google-analytics-mcp/credentials.json`

Done. No browser flow, no consent screen, no tokens to refresh.

## Installation

### Claude Code

```bash
claude mcp add google-analytics -e GA_CREDENTIALS='{"type":"service_account",...}' -- uvx google-analytics-mcp
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-analytics": {
      "command": "uvx",
      "args": ["google-analytics-mcp"],
      "env": {
        "GA_CREDENTIALS": "{\"type\":\"service_account\",\"project_id\":\"...\", ...}"
      }
    }
  }
}
```

### From source

```bash
git clone https://github.com/stucchi/mcp-google-analytics.git
cd google-analytics-mcp
uv run google-analytics-mcp
```

## Getting Started

1. **Check auth**: Call `check_auth_status` to verify the service account is configured
2. **List accounts**: Call `list_accounts` to see your GA4 accounts
3. **Setup a property**: Use `create_property` → `create_web_data_stream` → `get_tracking_snippet`
4. **Query data**: Use `run_report` with dimensions and metrics

## Tools (23)

### Auth

| Tool | Description |
|------|-------------|
| `check_auth_status` | Verify service account is configured and valid |

### Admin API

| Tool | Description |
|------|-------------|
| `list_accounts` | List accessible GA4 accounts |
| `list_properties` | List properties for an account |
| `create_property` | Create a GA4 property |
| `get_property` | Get property details |
| `delete_property` | Soft-delete a property |
| `list_data_streams` | List data streams |
| `create_web_data_stream` | Create web stream → get Measurement ID |
| `delete_data_stream` | Delete a data stream |
| `get_tracking_snippet` | Generate gtag.js HTML snippet |
| `list_key_events` | List conversion events |
| `create_key_event` | Mark event as conversion |
| `delete_key_event` | Remove conversion |
| `list_custom_dimensions` | List custom dimensions |
| `create_custom_dimension` | Create custom dimension |
| `list_custom_metrics` | List custom metrics |
| `create_custom_metric` | Create custom metric |
| `list_google_ads_links` | List Google Ads links |
| `create_google_ads_link` | Link Google Ads account |
| `get_measurement_protocol_secret` | Get/create Measurement Protocol secret |

### Data API

| Tool | Description |
|------|-------------|
| `run_report` | Run report with dimensions, metrics, dates, filters |
| `run_realtime_report` | Real-time active users and events |
| `get_metadata` | List available dimensions and metrics |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GA_CREDENTIALS` | — | Service Account JSON key content (copy-paste the entire JSON) |
| `GA_CREDENTIALS_PATH` | `~/.google-analytics-mcp/credentials.json` | Alternative: path to the JSON key file |

`GA_CREDENTIALS` takes priority over `GA_CREDENTIALS_PATH`.

## Example Usage

```
You: "Set up Google Analytics for my website https://mcpadvisor.stucchi.consulting"

Assistant calls: list_accounts → create_property → create_web_data_stream → get_tracking_snippet

Result: Property created with Measurement ID G-XXXXXXXXXX and ready-to-paste HTML snippet.
```

```
You: "Show me the top 10 countries by sessions in the last 7 days"

Assistant calls: run_report(property_id="...", dimensions=["country"], metrics=["sessions"], start_date="7daysAgo", limit=10)
```

## License

MIT
