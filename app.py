import streamlit as st
import pandas as pd
import altair as alt

from engine import (
    load_events,
    build_device_index,
    build_gateway_index,
    sla_status,
    maintenance_risk,
    analyze_gateways,
    generate_insights,
    system_summary,
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="IoT Trust & Reliability Engine",
    layout="wide"
)
# --------------------------------------------------
# HEADER / BRANDING
# --------------------------------------------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=80)

with col2:
    st.markdown(
        """
        <div style="padding-top: 10px;">
            <div style="font-size: 34px; font-weight: 700; color: #4C78A8;">
                SentinelMesh
            </div>
            <div style="font-size: 14px; color: #A0AEC0;">
                Trust & Reliability Engine for IoT Telemetry
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
events = load_events()
devices = build_device_index(events)
gateways = build_gateway_index(events)

device_metrics = {
    dev: evts[0]["device_metrics"]
    for dev, evts in devices.items()
}

# ----------------------------
# DEVICE NAME MAP
# ----------------------------
device_name_map = {}
for e in events:
    dev = e["device"]["devEui"]
    name = e["device"].get("name")
    if name:
        device_name_map[dev] = name

def device_label(dev):
    return device_name_map.get(dev, dev)

# ----------------------------
# GATEWAY NAME MAP
# ----------------------------
gateway_ids = sorted(set(
    e["rf"]["gatewayId"]
    for e in events
    if e["rf"].get("gatewayId")
))

gateway_name_map = {
    gid: f"Gateway-{i+1}"
    for i, gid in enumerate(gateway_ids)
}

def gateway_label(gid):
    return gateway_name_map.get(gid, gid)

# ----------------------------
# ANALYTICS
# ----------------------------
gateway_stats = analyze_gateways(gateways)
summary = system_summary(device_metrics, gateway_stats)

# ----------------------------
# EVENTS DATAFRAME
# ----------------------------
df_events = pd.DataFrame([
    {
        "timestamp": e["timestamp"],
        "device": device_label(e["device"]["devEui"]),
        "confidence": e["confidence"]["confidence_score"],
    }
    for e in events
])

df_events["timestamp"] = pd.to_datetime(
    df_events["timestamp"],
    format="mixed",
    utc=True,
    errors="coerce"
)
df_events = df_events.dropna(subset=["timestamp"])

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("IoT Trust & Reliability Engine")
st.markdown(
    "This system evaluates **how reliable IoT telemetry is**, not just what it reports."
)

st.divider()

# --------------------------------------------------
# SYSTEM SUMMARY
# --------------------------------------------------
with st.expander("System Summary", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Devices Analyzed", summary["total_devices"])
    c2.metric("High-Risk Devices", summary["high_risk_devices"])
    c3.metric("Devices with SLA Warnings", summary["warn_devices"])
    c4.metric("Unstable Gateways", len(summary["unstable_gateways"]))

# --------------------------------------------------
# AUTOMATED INSIGHTS (DEVICE NAMES)
# --------------------------------------------------
with st.expander("Automated Insights", expanded=False):
    st.markdown(
        "Automatically generated insights based on device behavior, "
        "data completeness, and RF conditions."
    )

    for dev, m in device_metrics.items():
        name = device_label(dev)

        if m["battery_reporting_quality"] < 0.7:
            st.markdown(f"- **{name}** has poor battery telemetry quality.")

        if m["confidence_trend"] == "degrading":
            st.markdown(f"- **{name}** shows degrading confidence over time.")

        if m["data_completeness"] < 0.75:
            st.markdown(f"- **{name}** frequently reports incomplete telemetry.")

# --------------------------------------------------
# FLEET CONFIDENCE BY DEVICE
# --------------------------------------------------
with st.expander("Fleet Confidence by Device", expanded=False):
    st.markdown(
        "Each point represents a device. Lower confidence indicates unreliable telemetry."
    )

    conf_df = pd.DataFrame([
        {
            "device": device_label(d),
            "avg_confidence": m["avg_confidence"]
        }
        for d, m in device_metrics.items()
    ])

    scatter = (
        alt.Chart(conf_df)
        .mark_circle(size=90)
        .encode(
            x=alt.X(
                "avg_confidence:Q",
                title="Average Confidence Score",
                scale=alt.Scale(domain=[0, 100])
            ),
            y=alt.Y(
                "device:N",
                sort="-x",
                title="Device"
            ),
            color=alt.condition(
                alt.datum.avg_confidence < 70,
                alt.value("#E45756"),
                alt.value("#4C78A8")
            ),
            tooltip=["device", "avg_confidence"]
        )
        .properties(height=400)
    )

    threshold = alt.Chart(
        pd.DataFrame({"x": [70]})
    ).mark_rule(color="#E45756").encode(x="x:Q")

    st.altair_chart(scatter + threshold, use_container_width=True)

# --------------------------------------------------
# CONFIDENCE OVER TIME
# --------------------------------------------------
with st.expander("Confidence Over Time (Per Device)", expanded=False):
    st.markdown(
        "Shows how trust evolves over time for a selected device."
    )

    selected = st.selectbox(
        "Select device",
        sorted(conf_df["device"])
    )

    ts = df_events[df_events["device"] == selected]

    line = (
        alt.Chart(ts)
        .mark_line(color="#4C78A8")
        .encode(
            x=alt.X("timestamp:T", title="Time"),
            y=alt.Y(
                "confidence:Q",
                title="Confidence Score",
                scale=alt.Scale(domain=[0, 100])
            )
        )
        .properties(height=300)
    )

    warn_line = alt.Chart(
        pd.DataFrame({"y": [70]})
    ).mark_rule(color="#E45756").encode(y="y:Q")

    st.altair_chart(line + warn_line, use_container_width=True)

# --------------------------------------------------
# GATEWAY RF STABILITY (GATEWAY NAMES)
# --------------------------------------------------
with st.expander("Gateway RF Stability", expanded=False):
    st.markdown(
        "RSSI variance per gateway. Higher variance indicates unstable RF conditions."
    )

    gw_df = (
        pd.DataFrame.from_dict(gateway_stats, orient="index")
        .reset_index()
        .rename(columns={"index": "gateway_id"})
    )

    gw_df["gateway"] = gw_df["gateway_id"].map(gateway_label)

    gw_chart = (
        alt.Chart(gw_df)
        .mark_bar()
        .encode(
            x=alt.X("gateway:N", title="Gateway"),
            y=alt.Y("rssi_std:Q", title="RSSI Variance"),
            color=alt.condition(
                alt.datum.rssi_std > 12,
                alt.value("#E45756"),
                alt.value("#4C78A8")
            ),
            tooltip=["gateway", "rssi_std", "avg_confidence", "event_count"]
        )
        .properties(height=300)
    )

    st.altair_chart(gw_chart, use_container_width=True)

# --------------------------------------------------
# MAINTENANCE PRIORITY
# --------------------------------------------------
with st.expander("Maintenance Priority", expanded=False):
    st.markdown(
        "Devices ranked by maintenance risk."
    )

    maint_df = pd.DataFrame([
        {
            "device": device_label(d),
            "risk": maintenance_risk(m)
        }
        for d, m in device_metrics.items()
        if maintenance_risk(m) > 0
    ]).sort_values("risk", ascending=False)

    risk_chart = (
        alt.Chart(maint_df)
        .mark_bar(color="#F2A541")
        .encode(
            x=alt.X("risk:Q", title="Maintenance Risk Score"),
            y=alt.Y("device:N", sort="-x", title="Device"),
            tooltip=["device", "risk"]
        )
        .properties(height=350)
    )

    st.altair_chart(risk_chart, use_container_width=True)

# --------------------------------------------------
# SLA STATUS
# --------------------------------------------------
with st.expander("SLA Status", expanded=False):
    sla_df = pd.DataFrame([
        {
            "device": device_label(d),
            "sla": sla_status(m),
            "confidence": m["avg_confidence"],
            "completeness": m["data_completeness"],
        }
        for d, m in device_metrics.items()
    ])

    st.dataframe(sla_df, use_container_width=True)
# --------------------------------------------------
# TRUST REPLAY (TIME FLOW)
# --------------------------------------------------
with st.expander("Trust Replay (Time Flow)", expanded=False):
    st.markdown(
        "Replay how **trust and reliability evolve over time**. "
        "Drag the slider to inspect the system state at any moment."
    )

    # Determine replay range
    min_time = df_events["timestamp"].min()
    max_time = df_events["timestamp"].max()

    replay_time = st.slider(
        "Replay Time",
        min_value=min_time.to_pydatetime(),
        max_value=max_time.to_pydatetime(),
        value=max_time.to_pydatetime(),
        format="YYYY-MM-DD HH:mm"
    )

    # Filter events up to replay time
    replay_df = df_events[df_events["timestamp"] <= pd.Timestamp(replay_time)]
    # ----------------------------
    # CONFIDENCE OVER TIME (ALL DEVICES)
    # ----------------------------
    st.markdown("### Fleet Confidence Over Time")

    fleet_chart = (
        alt.Chart(replay_df)
        .mark_line(opacity=0.5)
        .encode(
            x=alt.X("timestamp:T", title="Time"),
            y=alt.Y(
                "confidence:Q",
                title="Confidence Score",
                scale=alt.Scale(domain=[0, 100])
            ),
            color=alt.Color(
                "device:N",
                legend=None
            ),
            tooltip=["device", "confidence", "timestamp:T"]
        )
        .properties(height=300)
    )

    threshold = alt.Chart(
        pd.DataFrame({"y": [70]})
    ).mark_rule(color="#E45756").encode(y="y:Q")

    st.altair_chart(fleet_chart + threshold, use_container_width=True)

    # ----------------------------
    # DEVICE STATE AT REPLAY TIME
    # ----------------------------
    st.markdown("### Device State at Selected Time")

    latest_state = (
        replay_df.sort_values("timestamp")
        .groupby("device")
        .tail(1)
    )

    state_df = latest_state[["device", "confidence"]].copy()
    state_df["status"] = state_df["confidence"].apply(
        lambda x: "At Risk" if x < 70 else "Healthy"
    )

    st.dataframe(
        state_df.sort_values("confidence"),
        use_container_width=True
    )

    # ----------------------------
    # ACTIVE WARNINGS AT REPLAY TIME
    # ----------------------------
    st.markdown("### Active Warnings")

    warnings = state_df[state_df["confidence"] < 70]

    if len(warnings) == 0:
        st.success("No devices below confidence threshold at this time.")
    else:
        for _, row in warnings.iterrows():
            st.markdown(
                f"- **{row['device']}** confidence dropped to {row['confidence']}"
            )
# --------------------------------------------------
# GUIDED QUERY INTERFACE
# --------------------------------------------------
from query_engine import parse_query, handle_query

with st.expander("Interactive Query", expanded=True):
    st.markdown("### What exists in this system")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Devices**")
        for d in sorted(device_name_map.values()):
            st.markdown(f"- {d}")

    with c2:
        st.markdown("**Gateways**")
        for g in sorted(gateway_name_map.values()):
            st.markdown(f"- {g}")

    st.divider()

    st.markdown("### Supported questions")
    st.markdown(
        "- What devices are faulty?\n"
        "- Which gateway does **Door Sensor 08** use?\n"
        "- Which devices use **Gateway-1**?\n"
        "- Which gateways are unstable?"
    )

    st.divider()

    user_q = st.text_input("Ask a question")

    if user_q:
        intent, arg = parse_query(user_q)
        response = handle_query(
            intent,
            arg,
            events,
            device_metrics,
            device_name_map,
            gateway_name_map,
        )

        st.markdown("### Answer")

        if isinstance(response, list):
            for r in response:
                st.markdown(f"- {r}")
        elif isinstance(response, dict):
            st.json(response)
        else:
            st.markdown(response)
