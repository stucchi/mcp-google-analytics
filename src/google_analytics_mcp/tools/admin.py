"""Google Analytics 4 Admin API tools."""

from __future__ import annotations

from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import (
    CreateCustomDimensionRequest,
    CreateCustomMetricRequest,
    CreateDataStreamRequest,
    CreateGoogleAdsLinkRequest,
    CreateKeyEventRequest,
    CreateMeasurementProtocolSecretRequest,
    CreatePropertyRequest,
    CustomDimension,
    CustomMetric,
    DataStream,
    GoogleAdsLink,
    KeyEvent,
    ListMeasurementProtocolSecretsRequest,
    MeasurementProtocolSecret,
    Property,
)

from google_analytics_mcp.auth import get_credentials
from google_analytics_mcp.helpers import proto_to_dict, run_sync


def _client() -> AnalyticsAdminServiceClient:
    return AnalyticsAdminServiceClient(credentials=get_credentials())


# ── Accounts ────────────────────────────────────────────────────────


async def list_accounts() -> list[dict]:
    """List all Google Analytics accounts accessible by the authenticated user."""
    client = _client()
    pages = await run_sync(client.list_accounts)
    return [proto_to_dict(a) for a in pages]


# ── Properties ──────────────────────────────────────────────────────


async def list_properties(account_id: str) -> list[dict]:
    """List GA4 properties for a given account.

    Args:
        account_id: The account ID (e.g. "123456789").
    """
    client = _client()
    pages = await run_sync(
        client.list_properties, filter=f"parent:accounts/{account_id}"
    )
    return [proto_to_dict(p) for p in pages]


async def create_property(
    account_id: str,
    display_name: str,
    time_zone: str = "Europe/Rome",
    currency_code: str = "EUR",
) -> dict:
    """Create a new GA4 property.

    Args:
        account_id: Parent account ID.
        display_name: Human-readable name for the property.
        time_zone: Reporting timezone (IANA, e.g. "Europe/Rome").
        currency_code: Currency code (e.g. "EUR", "USD").
    """
    client = _client()
    prop = Property(
        parent=f"accounts/{account_id}",
        display_name=display_name,
        time_zone=time_zone,
        currency_code=currency_code,
    )
    result = await run_sync(client.create_property, request=CreatePropertyRequest(property=prop))
    return proto_to_dict(result)


async def get_property(property_id: str) -> dict:
    """Get details of a GA4 property.

    Args:
        property_id: The property ID (e.g. "123456789").
    """
    client = _client()
    result = await run_sync(client.get_property, name=f"properties/{property_id}")
    return proto_to_dict(result)


async def delete_property(property_id: str) -> dict:
    """Soft-delete a GA4 property (can be restored within 35 days).

    Args:
        property_id: The property ID to delete.
    """
    client = _client()
    result = await run_sync(client.delete_property, name=f"properties/{property_id}")
    return proto_to_dict(result)


# ── Data Streams ────────────────────────────────────────────────────


async def list_data_streams(property_id: str) -> list[dict]:
    """List all data streams for a GA4 property.

    Args:
        property_id: The property ID.
    """
    client = _client()
    pages = await run_sync(client.list_data_streams, parent=f"properties/{property_id}")
    return [proto_to_dict(s) for s in pages]


async def create_web_data_stream(
    property_id: str,
    default_uri: str,
    display_name: str = "",
) -> dict:
    """Create a web data stream and get the Measurement ID (G-XXXXX).

    Args:
        property_id: The property ID.
        default_uri: Website URL (e.g. "https://example.com").
        display_name: Optional human-readable name for this stream.
    """
    client = _client()
    stream = DataStream(
        type_=DataStream.DataStreamType.WEB_DATA_STREAM,
        display_name=display_name or default_uri,
        web_stream_data=DataStream.WebStreamData(default_uri=default_uri),
    )
    result = await run_sync(
        client.create_data_stream,
        request=CreateDataStreamRequest(
            parent=f"properties/{property_id}",
            data_stream=stream,
        ),
    )
    return proto_to_dict(result)


async def delete_data_stream(property_id: str, stream_id: str) -> str:
    """Delete a data stream.

    Args:
        property_id: The property ID.
        stream_id: The data stream ID.
    """
    client = _client()
    await run_sync(
        client.delete_data_stream,
        name=f"properties/{property_id}/dataStreams/{stream_id}",
    )
    return f"Data stream {stream_id} deleted."


async def get_tracking_snippet(measurement_id: str) -> str:
    """Generate the gtag.js tracking snippet for a given Measurement ID.

    Args:
        measurement_id: The Measurement ID (e.g. "G-XXXXXXXXXX").
    """
    return f"""<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{measurement_id}');
</script>
<!-- End Google Analytics 4 -->"""


# ── Key Events (Conversions) ───────────────────────────────────────


async def list_key_events(property_id: str) -> list[dict]:
    """List key events (conversions) for a property.

    Args:
        property_id: The property ID.
    """
    client = _client()
    pages = await run_sync(client.list_key_events, parent=f"properties/{property_id}")
    return [proto_to_dict(e) for e in pages]


async def create_key_event(property_id: str, event_name: str) -> dict:
    """Mark an event as a key event (conversion).

    Args:
        property_id: The property ID.
        event_name: GA4 event name (e.g. "purchase", "sign_up").
    """
    client = _client()
    key_event = KeyEvent(event_name=event_name)
    result = await run_sync(
        client.create_key_event,
        request=CreateKeyEventRequest(
            key_event=key_event,
            parent=f"properties/{property_id}",
        ),
    )
    return proto_to_dict(result)


async def delete_key_event(property_id: str, key_event_id: str) -> str:
    """Remove an event from key events (conversions).

    Args:
        property_id: The property ID.
        key_event_id: The key event resource ID.
    """
    client = _client()
    await run_sync(
        client.delete_key_event,
        name=f"properties/{property_id}/keyEvents/{key_event_id}",
    )
    return f"Key event {key_event_id} deleted."


# ── Custom Dimensions ──────────────────────────────────────────────


async def list_custom_dimensions(property_id: str) -> list[dict]:
    """List custom dimensions for a property.

    Args:
        property_id: The property ID.
    """
    client = _client()
    pages = await run_sync(client.list_custom_dimensions, parent=f"properties/{property_id}")
    return [proto_to_dict(d) for d in pages]


async def create_custom_dimension(
    property_id: str,
    parameter_name: str,
    display_name: str,
    scope: str = "EVENT",
    description: str = "",
) -> dict:
    """Create a custom dimension.

    Args:
        property_id: The property ID.
        parameter_name: Event parameter name (e.g. "user_type").
        display_name: Human-readable name shown in reports.
        scope: "EVENT" or "USER".
        description: Optional description.
    """
    client = _client()
    dim = CustomDimension(
        parameter_name=parameter_name,
        display_name=display_name,
        scope=CustomDimension.DimensionScope[scope],
        description=description,
    )
    result = await run_sync(
        client.create_custom_dimension,
        request=CreateCustomDimensionRequest(
            parent=f"properties/{property_id}",
            custom_dimension=dim,
        ),
    )
    return proto_to_dict(result)


# ── Custom Metrics ─────────────────────────────────────────────────


async def list_custom_metrics(property_id: str) -> list[dict]:
    """List custom metrics for a property.

    Args:
        property_id: The property ID.
    """
    client = _client()
    pages = await run_sync(client.list_custom_metrics, parent=f"properties/{property_id}")
    return [proto_to_dict(m) for m in pages]


async def create_custom_metric(
    property_id: str,
    parameter_name: str,
    display_name: str,
    scope: str = "EVENT",
    measurement_unit: str = "STANDARD",
    description: str = "",
) -> dict:
    """Create a custom metric.

    Args:
        property_id: The property ID.
        parameter_name: Event parameter name.
        display_name: Human-readable name.
        scope: "EVENT" only for metrics.
        measurement_unit: "STANDARD", "CURRENCY", "FEET", "METERS", "KILOMETERS", "MILES", "MILLISECONDS", "SECONDS", "MINUTES", "HOURS".
        description: Optional description.
    """
    client = _client()
    metric = CustomMetric(
        parameter_name=parameter_name,
        display_name=display_name,
        scope=CustomMetric.MetricScope[scope],
        measurement_unit=CustomMetric.MeasurementUnit[measurement_unit],
        description=description,
    )
    result = await run_sync(
        client.create_custom_metric,
        request=CreateCustomMetricRequest(
            parent=f"properties/{property_id}",
            custom_metric=metric,
        ),
    )
    return proto_to_dict(result)


# ── Google Ads Links ───────────────────────────────────────────────


async def list_google_ads_links(property_id: str) -> list[dict]:
    """List Google Ads links for a property.

    Args:
        property_id: The property ID.
    """
    client = _client()
    pages = await run_sync(client.list_google_ads_links, parent=f"properties/{property_id}")
    return [proto_to_dict(link) for link in pages]


async def create_google_ads_link(property_id: str, customer_id: str) -> dict:
    """Link a Google Ads account to a GA4 property.

    Args:
        property_id: The property ID.
        customer_id: Google Ads customer ID (e.g. "123-456-7890").
    """
    client = _client()
    link = GoogleAdsLink(customer_id=customer_id)
    result = await run_sync(
        client.create_google_ads_link,
        request=CreateGoogleAdsLinkRequest(
            parent=f"properties/{property_id}",
            google_ads_link=link,
        ),
    )
    return proto_to_dict(result)


# ── Measurement Protocol Secret ────────────────────────────────────


async def get_measurement_protocol_secret(
    property_id: str,
    stream_id: str,
    display_name: str = "MCP Server",
) -> dict:
    """Get or create a Measurement Protocol API secret for server-side events.

    Args:
        property_id: The property ID.
        stream_id: The data stream ID.
        display_name: Name for the secret if a new one is created.
    """
    client = _client()
    parent = f"properties/{property_id}/dataStreams/{stream_id}"

    # Try to find existing
    pages = await run_sync(
        client.list_measurement_protocol_secrets,
        request=ListMeasurementProtocolSecretsRequest(parent=parent),
    )
    secrets = [proto_to_dict(s) for s in pages]
    if secrets:
        return secrets[0]

    # Create new
    secret = MeasurementProtocolSecret(display_name=display_name)
    result = await run_sync(
        client.create_measurement_protocol_secret,
        request=CreateMeasurementProtocolSecretRequest(
            parent=parent,
            measurement_protocol_secret=secret,
        ),
    )
    return proto_to_dict(result)
