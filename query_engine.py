import pandas as pd

# -------------------------
# QUERY PARSING
# -------------------------

def parse_query(text):
    q = text.lower().strip()

    # Inventory
    if q in ["what devices exist", "list devices"]:
        return ("list_devices", None)
    if q in ["what gateways exist", "list gateways"]:
        return ("list_gateways", None)
    if "how many devices" in q:
        return ("count_devices", None)
    if "how many gateways" in q:
        return ("count_gateways", None)

    # Device health
    if "faulty" in q:
        return ("faulty_devices", None)
    if "needs maintenance" in q:
        return ("maintenance_devices", None)
    if "most unreliable" in q:
        return ("worst_device", None)

    # Device-specific
    if "device id" in q:
        return ("device_id", q)
    if "sensor type" in q or "profile" in q:
        return ("sensor_type", q)
    if "last data" in q or "last received" in q:
        return ("last_seen", q)
    if "where is" in q or "location" in q:
        return ("device_location", q)
    if "how many messages" in q:
        return ("message_count", q)
    if "confidence" in q:
        return ("device_confidence", q)
    if "is" in q and "healthy" in q:
        return ("device_health", q)
    if "which gateway" in q:
        return ("device_gateway", q)

    # Gateway
    if "which devices use" in q:
        return ("gateway_devices", q)
    if "how many events" in q:
        return ("gateway_events", q)
    if "unstable gateway" in q:
        return ("unstable_gateways", None)

    return ("unknown", None)


# -------------------------
# QUERY HANDLER
# -------------------------

def handle_query(
    intent,
    arg,
    events,
    device_metrics,
    device_name_map,
    gateway_name_map,
):
    import pandas as pd

    df = pd.DataFrame(events)
    name_to_dev = {v.lower(): k for k, v in device_name_map.items()}
    name_to_gw = {v.lower(): k for k, v in gateway_name_map.items()}

    def find_device(q):
        for name, dev in name_to_dev.items():
            if name in q:
                return dev
        return None

    def find_gateway(q):
        for name, gid in name_to_gw.items():
            if name in q:
                return gid
        return None

    # Inventory
    if intent == "list_devices":
        return sorted(device_name_map.values())

    if intent == "list_gateways":
        return sorted(gateway_name_map.values())

    if intent == "count_devices":
        return f"There are {len(device_name_map)} devices."

    if intent == "count_gateways":
        return f"There are {len(gateway_name_map)} gateways."

    # Fleet health
    if intent == "faulty_devices":
        return [
            device_name_map[d]
            for d, m in device_metrics.items()
            if m["avg_confidence"] < 70
        ] or ["No faulty devices detected"]

    if intent == "maintenance_devices":
        return [
            device_name_map[d]
            for d, m in device_metrics.items()
            if m["battery_reporting_quality"] < 0.5
            or m["confidence_trend"] == "degrading"
        ]

    if intent == "worst_device":
        d = min(device_metrics, key=lambda x: device_metrics[x]["avg_confidence"])
        return device_name_map[d]

    # Device-specific
    dev = find_device(arg or "")

    if dev:
        name = device_name_map[dev]

        if intent == "device_id":
            return f"{name} device ID is {dev}"

        if intent == "sensor_type":
            profile = next(
                e["device"]["profile"]
                for e in events
                if e["device"]["devEui"] == dev
            )
            return f"{name} is a {profile} sensor"

        if intent == "last_seen":
            last = max(
                e["timestamp"]
                for e in events
                if e["device"]["devEui"] == dev
            )
            return f"Last data received at {last}"

        if intent == "device_location":
            locs = [
                e["rf"]["location"]
                for e in events
                if e["device"]["devEui"] == dev and e["rf"].get("location")
            ]
            return locs[-1] if locs else "No location data available"

        if intent == "message_count":
            count = sum(1 for e in events if e["device"]["devEui"] == dev)
            return f"{name} has sent {count} messages"

        if intent == "device_confidence":
            return f"{name} average confidence is {device_metrics[dev]['avg_confidence']}"

        if intent == "device_health":
            m = device_metrics[dev]
            return "Healthy" if m["avg_confidence"] >= 70 else "At risk"

        if intent == "device_gateway":
            gws = {
                gateway_name_map[e["rf"]["gatewayId"]]
                for e in events
                if e["device"]["devEui"] == dev and e["rf"].get("gatewayId")
            }
            return list(gws)

    # Gateway
    gw = find_gateway(arg or "")

    if gw:
        name = gateway_name_map[gw]

        if intent == "gateway_devices":
            return sorted({
                device_name_map[e["device"]["devEui"]]
                for e in events
                if e["rf"].get("gatewayId") == gw
            })

        if intent == "gateway_events":
            count = sum(1 for e in events if e["rf"].get("gatewayId") == gw)
            return f"{name} handled {count} events"

    if intent == "unstable_gateways":
        return [
            gateway_name_map[g]
            for g in gateway_name_map
            if any(
                e["rf"]["gatewayId"] == g and e["confidence"]["confidence_score"] < 70
                for e in events
            )
        ] or ["No unstable gateways"]

    return "Unsupported question."
