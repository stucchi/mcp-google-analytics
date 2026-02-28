"""Google Analytics 4 MCP Server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from google_analytics_mcp.auth import check_credentials
from google_analytics_mcp.helpers import format_json, with_setup_guide
from google_analytics_mcp.tools import admin, data

mcp = FastMCP("google-analytics")


# ── Auth Tools ──────────────────────────────────────────────────────


@mcp.tool()
async def check_auth_status() -> str:
    """Check if the Google Analytics service account is configured and valid."""
    status = check_credentials()
    return format_json(status)


# ── Admin: Accounts ─────────────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_accounts() -> str:
    """List all Google Analytics accounts accessible by the authenticated user."""
    result = await admin.list_accounts()
    if not result:
        return "No accounts found. Make sure you have access to at least one Google Analytics account."
    return format_json(result)


# ── Admin: Properties ───────────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_properties(
    account_id: Annotated[str, "The GA account ID (e.g. '123456789')"],
) -> str:
    """List all GA4 properties for an account."""
    result = await admin.list_properties(account_id)
    if not result:
        return f"No properties found for account {account_id}."
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def create_property(
    account_id: Annotated[str, "Parent account ID"],
    display_name: Annotated[str, "Name for the property"],
    time_zone: Annotated[str, "Reporting timezone (IANA format)"] = "Europe/Rome",
    currency_code: Annotated[str, "Currency code"] = "EUR",
) -> str:
    """Create a new GA4 property."""
    result = await admin.create_property(account_id, display_name, time_zone, currency_code)
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def get_property(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """Get details of a GA4 property."""
    result = await admin.get_property(property_id)
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def delete_property(
    property_id: Annotated[str, "The property ID to delete"],
) -> str:
    """Soft-delete a GA4 property (can be restored within 35 days)."""
    result = await admin.delete_property(property_id)
    return format_json(result)


# ── Admin: Data Streams ─────────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_data_streams(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """List all data streams for a GA4 property."""
    result = await admin.list_data_streams(property_id)
    if not result:
        return f"No data streams found for property {property_id}."
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def create_web_data_stream(
    property_id: Annotated[str, "The property ID"],
    default_uri: Annotated[str, "Website URL (e.g. 'https://example.com')"],
    display_name: Annotated[str, "Optional name for this stream"] = "",
) -> str:
    """Create a web data stream and get the Measurement ID (G-XXXXX)."""
    result = await admin.create_web_data_stream(property_id, default_uri, display_name)
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def delete_data_stream(
    property_id: Annotated[str, "The property ID"],
    stream_id: Annotated[str, "The data stream ID"],
) -> str:
    """Delete a data stream."""
    return await admin.delete_data_stream(property_id, stream_id)


@mcp.tool()
async def get_tracking_snippet(
    measurement_id: Annotated[str, "Measurement ID (e.g. 'G-XXXXXXXXXX')"],
) -> str:
    """Generate the gtag.js HTML tracking snippet ready to paste into your website."""
    return await admin.get_tracking_snippet(measurement_id)


# ── Admin: Key Events (Conversions) ─────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_key_events(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """List key events (conversions) configured for a property."""
    result = await admin.list_key_events(property_id)
    if not result:
        return f"No key events found for property {property_id}."
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def create_key_event(
    property_id: Annotated[str, "The property ID"],
    event_name: Annotated[str, "GA4 event name (e.g. 'purchase', 'sign_up')"],
) -> str:
    """Mark an event as a key event (conversion)."""
    result = await admin.create_key_event(property_id, event_name)
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def delete_key_event(
    property_id: Annotated[str, "The property ID"],
    key_event_id: Annotated[str, "The key event resource ID"],
) -> str:
    """Remove an event from key events (conversions)."""
    return await admin.delete_key_event(property_id, key_event_id)


# ── Admin: Custom Dimensions ────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_custom_dimensions(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """List custom dimensions for a property."""
    result = await admin.list_custom_dimensions(property_id)
    if not result:
        return f"No custom dimensions found for property {property_id}."
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def create_custom_dimension(
    property_id: Annotated[str, "The property ID"],
    parameter_name: Annotated[str, "Event parameter name (e.g. 'user_type')"],
    display_name: Annotated[str, "Human-readable name for reports"],
    scope: Annotated[str, "'EVENT' or 'USER'"] = "EVENT",
    description: Annotated[str, "Optional description"] = "",
) -> str:
    """Create a custom dimension."""
    result = await admin.create_custom_dimension(
        property_id, parameter_name, display_name, scope, description
    )
    return format_json(result)


# ── Admin: Custom Metrics ───────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_custom_metrics(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """List custom metrics for a property."""
    result = await admin.list_custom_metrics(property_id)
    if not result:
        return f"No custom metrics found for property {property_id}."
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def create_custom_metric(
    property_id: Annotated[str, "The property ID"],
    parameter_name: Annotated[str, "Event parameter name"],
    display_name: Annotated[str, "Human-readable name"],
    scope: Annotated[str, "'EVENT'"] = "EVENT",
    measurement_unit: Annotated[str, "'STANDARD', 'CURRENCY', 'FEET', 'METERS', 'KILOMETERS', 'MILES', 'MILLISECONDS', 'SECONDS', 'MINUTES', 'HOURS'"] = "STANDARD",
    description: Annotated[str, "Optional description"] = "",
) -> str:
    """Create a custom metric."""
    result = await admin.create_custom_metric(
        property_id, parameter_name, display_name, scope, measurement_unit, description
    )
    return format_json(result)


# ── Admin: Google Ads Links ─────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def list_google_ads_links(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """List Google Ads links for a property."""
    result = await admin.list_google_ads_links(property_id)
    if not result:
        return f"No Google Ads links found for property {property_id}."
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def create_google_ads_link(
    property_id: Annotated[str, "The property ID"],
    customer_id: Annotated[str, "Google Ads customer ID (e.g. '123-456-7890')"],
) -> str:
    """Link a Google Ads account to a GA4 property."""
    result = await admin.create_google_ads_link(property_id, customer_id)
    return format_json(result)


# ── Admin: Measurement Protocol ─────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def get_measurement_protocol_secret(
    property_id: Annotated[str, "The property ID"],
    stream_id: Annotated[str, "The data stream ID"],
    display_name: Annotated[str, "Name for the secret if creating new"] = "MCP Server",
) -> str:
    """Get or create a Measurement Protocol API secret for server-side event tracking."""
    result = await admin.get_measurement_protocol_secret(property_id, stream_id, display_name)
    return format_json(result)


# ── Data: Reports ───────────────────────────────────────────────────


@mcp.tool()
@with_setup_guide
async def run_report(
    property_id: Annotated[str, "The property ID"],
    dimensions: Annotated[list[str], "List of dimension names (e.g. ['country', 'city'])"],
    metrics: Annotated[list[str], "List of metric names (e.g. ['activeUsers', 'sessions'])"],
    start_date: Annotated[str, "Start date ('YYYY-MM-DD', 'NdaysAgo', 'yesterday', 'today')"] = "28daysAgo",
    end_date: Annotated[str, "End date (same format)"] = "today",
    dimension_filter_name: Annotated[str | None, "Optional dimension to filter on"] = None,
    dimension_filter_value: Annotated[str | None, "Value for the dimension filter (exact match)"] = None,
    limit: Annotated[int, "Max rows (default 100)"] = 100,
    offset: Annotated[int, "Row offset for pagination"] = 0,
) -> str:
    """Run a GA4 report with dimensions, metrics, date range, and optional filters."""
    result = await data.run_report(
        property_id, dimensions, metrics, start_date, end_date,
        dimension_filter_name, dimension_filter_value, limit, offset,
    )
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def run_realtime_report(
    property_id: Annotated[str, "The property ID"],
    dimensions: Annotated[list[str] | None, "Optional real-time dimensions"] = None,
    metrics: Annotated[list[str] | None, "Optional real-time metrics (default: ['activeUsers'])"] = None,
) -> str:
    """Run a real-time report showing active users and live events."""
    result = await data.run_realtime_report(property_id, dimensions, metrics)
    return format_json(result)


@mcp.tool()
@with_setup_guide
async def get_metadata(
    property_id: Annotated[str, "The property ID"],
) -> str:
    """List all available dimensions and metrics for a GA4 property.

    Useful to discover which dimension/metric names you can use in run_report.
    """
    result = await data.get_metadata(property_id)
    return format_json(result)


# ── Entry Point ─────────────────────────────────────────────────────


def main() -> None:
    mcp.run(transport="stdio")
