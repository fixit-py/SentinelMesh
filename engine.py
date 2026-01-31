import json
from collections import defaultdict

def load_events(path="enriched_events.jsonl"):
    events = []
    with open(path) as f:
        for line in f:
            events.append(json.loads(line))
    return events


def build_device_index(events):
    devices = defaultdict(list)
    for e in events:
        devices[e["device"]["devEui"]].append(e)
    return devices


def build_gateway_index(events):
    gateways = defaultdict(list)
    for e in events:
        gw = e["rf"]["gatewayId"]
        if gw:
            gateways[gw].append(e)
    return gateways

def sla_status(m):
    if m["avg_confidence"] < 70:
        return "FAIL"
    if m["data_completeness"] < 0.8:
        return "WARN"
    return "PASS"


def maintenance_risk(m):
    risk = 0
    if m["battery_reporting_quality"] < 0.5:
        risk += 30
    if m["confidence_trend"] == "degrading":
        risk += 25
    if m["rssi_std"] > 10:
        risk += 20
    if m["data_completeness"] < 0.75:
        risk += 15
    return risk

def generate_insights(device_metrics):
    insights = []

    for dev, m in device_metrics.items():
        if "unreliable_despite_good_rssi" in m["flags"]:
            insights.append(
                f"Device {dev} is unreliable despite stable RF conditions."
            )
        if m["battery_reporting_quality"] < 0.7:
            insights.append(
                f"Device {dev} has poor battery telemetry quality."
            )
        if m["confidence_trend"] == "degrading":
            insights.append(
                f"Device {dev} shows degrading confidence over time."
            )
        if m["data_completeness"] < 0.75:
            insights.append(
                f"Device {dev} frequently reports incomplete telemetry."
            )

    return insights

import statistics

def analyze_gateways(gateway_index):
    results = {}

    for gw, events in gateway_index.items():
        confidences = [e["confidence"]["confidence_score"] for e in events]
        rssi_vals = [e["rf"]["rssi"] for e in events if e["rf"]["rssi"] is not None]

        results[gw] = {
            "avg_confidence": round(sum(confidences) / len(confidences), 2),
            "rssi_std": round(statistics.pstdev(rssi_vals), 2) if len(rssi_vals) > 1 else 0,
            "event_count": len(events)
        }

    return results

def query_devices(device_metrics, q):
    if q == "low_confidence":
        return {d: m for d, m in device_metrics.items() if m["avg_confidence"] < 80}

    if q == "needs_maintenance":
        return {
            d: m for d, m in device_metrics.items()
            if m["battery_reporting_quality"] < 0.5
            or m["confidence_trend"] == "degrading"
        }

    if q == "incomplete_data":
        return {d: m for d, m in device_metrics.items() if m["data_completeness"] < 0.8}

    return {}
def system_summary(device_metrics, gateway_stats):
    return {
        "total_devices": len(device_metrics),
        "high_risk_devices": sum(
            1 for m in device_metrics.values()
            if maintenance_risk(m) >= 60
        ),
        "warn_devices": sum(
            1 for m in device_metrics.values()
            if sla_status(m) == "WARN"
        ),
        "unstable_gateways": [
            g for g, s in gateway_stats.items()
            if s["rssi_std"] > 12
        ]
    }
def system_summary(device_metrics, gateway_stats):
    return {
        "total_devices": len(device_metrics),
        "high_risk_devices": sum(
            1 for m in device_metrics.values()
            if maintenance_risk(m) >= 60
        ),
        "warn_devices": sum(
            1 for m in device_metrics.values()
            if sla_status(m) == "WARN"
        ),
        "unstable_gateways": [
            g for g, s in gateway_stats.items()
            if s["rssi_std"] > 12
        ]
    }
def explain_device(dev, m):
    reasons = []
    if m["battery_reporting_quality"] < 0.5:
        reasons.append("Battery telemetry missing")
    if m["confidence_trend"] == "degrading":
        reasons.append("Confidence decreasing over time")
    if m["rssi_std"] > 10:
        reasons.append("Unstable RF conditions")
    return reasons
