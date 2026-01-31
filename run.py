from engine import *

events = load_events()
devices = build_device_index(events)
gateways = build_gateway_index(events)

device_metrics = {
    dev: evts[0]["device_metrics"]
    for dev, evts in devices.items()
}

print("\n=== AUTOMATED INSIGHTS ===")
for i in generate_insights(device_metrics):
    print("-", i)

print("\n=== SLA STATUS ===")
for dev, m in device_metrics.items():
    print(dev, sla_status(m))

print("\n=== MAINTENANCE PRIORITY ===")
ranked = sorted(
    device_metrics.items(),
    key=lambda x: maintenance_risk(x[1]),
    reverse=True
)
for dev, m in ranked[:5]:
    print(dev, "risk =", maintenance_risk(m))

print("\n=== GATEWAY HEALTH ===")
gw_stats = analyze_gateways(gateways)
for gw, s in gw_stats.items():
    print(gw, s)

print("\n=== SYSTEM SUMMARY ===")
print(system_summary(device_metrics, gw_stats))

print("\n=== QUERY: NEEDS MAINTENANCE ===")
for dev in query_devices(device_metrics, "needs_maintenance"):
    print(dev)
