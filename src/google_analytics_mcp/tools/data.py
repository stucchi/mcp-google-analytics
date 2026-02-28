"""Google Analytics 4 Data API tools."""

from __future__ import annotations

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    GetMetadataRequest,
    Metric,
    RunRealtimeReportRequest,
    RunReportRequest,
)

from google_analytics_mcp.auth import get_credentials
from google_analytics_mcp.helpers import run_sync


def _client() -> BetaAnalyticsDataClient:
    return BetaAnalyticsDataClient(credentials=get_credentials())


def _format_report(response) -> dict:
    """Format a report response into a readable dict."""
    headers = [h.name for h in response.dimension_headers] + [
        h.name for h in response.metric_headers
    ]
    rows = []
    for row in response.rows:
        values = [v.value for v in row.dimension_values] + [
            v.value for v in row.metric_values
        ]
        rows.append(dict(zip(headers, values)))

    return {
        "row_count": response.row_count,
        "headers": headers,
        "rows": rows,
    }


async def run_report(
    property_id: str,
    dimensions: list[str],
    metrics: list[str],
    start_date: str = "28daysAgo",
    end_date: str = "today",
    dimension_filter_name: str | None = None,
    dimension_filter_value: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Run a GA4 report with flexible dimensions, metrics, and date ranges.

    Args:
        property_id: The property ID (e.g. "123456789").
        dimensions: List of dimension names (e.g. ["country", "city"]).
        metrics: List of metric names (e.g. ["activeUsers", "sessions"]).
        start_date: Start date ("YYYY-MM-DD", "NdaysAgo", "yesterday", "today").
        end_date: End date (same format as start_date).
        dimension_filter_name: Optional dimension name to filter on.
        dimension_filter_value: Value to match for the filter (exact match).
        limit: Max rows to return (default 100).
        offset: Row offset for pagination (default 0).
    """
    client = _client()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
        offset=offset,
    )

    if dimension_filter_name and dimension_filter_value:
        request.dimension_filter = FilterExpression(
            filter=Filter(
                field_name=dimension_filter_name,
                string_filter=Filter.StringFilter(
                    value=dimension_filter_value,
                    match_type=Filter.StringFilter.MatchType.EXACT,
                ),
            )
        )

    response = await run_sync(client.run_report, request=request)
    return _format_report(response)


async def run_realtime_report(
    property_id: str,
    dimensions: list[str] | None = None,
    metrics: list[str] | None = None,
) -> dict:
    """Run a real-time report (active users, live events).

    Args:
        property_id: The property ID.
        dimensions: Optional list of real-time dimensions (e.g. ["country", "unifiedScreenName"]).
        metrics: Optional list of real-time metrics (e.g. ["activeUsers", "eventCount"]).
            Defaults to ["activeUsers"] if not provided.
    """
    client = _client()

    if metrics is None:
        metrics = ["activeUsers"]

    request = RunRealtimeReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in (dimensions or [])],
        metrics=[Metric(name=m) for m in metrics],
    )

    response = await run_sync(client.run_realtime_report, request=request)
    return _format_report(response)


async def get_metadata(property_id: str) -> dict:
    """List all available dimensions and metrics for a GA4 property.

    Args:
        property_id: The property ID.
    """
    client = _client()

    response = await run_sync(
        client.get_metadata,
        request=GetMetadataRequest(name=f"properties/{property_id}/metadata"),
    )

    dims = [
        {"api_name": d.api_name, "ui_name": d.ui_name, "description": d.description, "category": d.category}
        for d in response.dimensions
    ]
    mets = [
        {"api_name": m.api_name, "ui_name": m.ui_name, "description": m.description, "category": m.category}
        for m in response.metrics
    ]

    return {
        "dimensions_count": len(dims),
        "metrics_count": len(mets),
        "dimensions": dims,
        "metrics": mets,
    }
