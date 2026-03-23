import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="SSS Dashboard", layout="wide")

# ---------------------------
# UPDATED CSS
# ---------------------------
st.markdown("""
<style>

/* Title */
.title {
    background: linear-gradient(90deg, #ff7e5f, #feb47b);  /* 🔥 orange gradient */
    padding: 18px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: white;
    border-radius: 12px;
    margin-bottom: 20px;
}

/* Section */
.section {
    background: linear-gradient(90deg, #667eea, #764ba2);
    padding: 10px;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    margin-top: 25px;
}

/* Cards */
.card {
    padding: 25px;
    border-radius: 14px;
    color: white;
    text-align: center;
    font-weight: bold;
}

/* Card colors */
.card1 { background: linear-gradient(135deg, #36d1dc, #5b86e5); }
.card2 { background: linear-gradient(135deg, #ff9a9e, #fad0c4); }
.card3 { background: linear-gradient(135deg, #a1ffce, #faffd1); color:#333; }
.card4 { background: linear-gradient(135deg, #fbc2eb, #a6c1ee); }

</style>
""", unsafe_allow_html=True)

# ---------------------------
# TITLE
# ---------------------------
st.markdown('<div class="title">SSS DATA ANALYTICS (MARCH)</div>', unsafe_allow_html=True)

# ---------------------------
# LOAD DATA (AUTO REFRESH FIX)
# ---------------------------
file_path = r"C:\Users\sm2069\Desktop\SSS-Mar\data\SSS-Mar_26.csv"

@st.cache_data
def load_data(path, modified_time):
    return pd.read_csv(path)

df = load_data(file_path, os.path.getmtime(file_path))

# ---------------------------
# DATE CLEAN
# ---------------------------
df["Inserted_Date"] = pd.to_datetime(df["Inserted_At"], errors="coerce")

# ---------------------------
# FILTERS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

operator = col1.multiselect("Operator", df["Operator_Code"].dropna().unique())
service = col2.multiselect("Service", df["Service"].dropna().unique())
from_port = col3.multiselect("From Port", df["From_Port"].dropna().unique())
to_port = col4.multiselect("To Port", df["To_Port"].dropna().unique())

if not operator: operator = df["Operator_Code"].unique()
if not service: service = df["Service"].unique()
if not from_port: from_port = df["From_Port"].unique()
if not to_port: to_port = df["To_Port"].unique()

filtered_df = df[
    (df["Operator_Code"].isin(operator)) &
    (df["Service"].isin(service)) &
    (df["From_Port"].isin(from_port)) &
    (df["To_Port"].isin(to_port))
]

# ---------------------------
# KPI CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">TOTAL OPERATORS<br><h1>{filtered_df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">TOTAL PORTS<br><h1>{filtered_df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TOTAL TERMINALS<br><h1>{filtered_df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">TOTAL VESSELS<br><h1>{filtered_df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

# ---------------------------
# TOGGLE
# ---------------------------
view_type = st.radio(
    "View Mode",
    ["Top 5 Operators", "All Operators"],
    horizontal=True
)

# ---------------------------
# DATE WISE OPERATOR
# ---------------------------
st.markdown('<div class="section">DATE WISE OPERATOR DISTRIBUTION</div>', unsafe_allow_html=True)

# 👉 Convert date properly
filtered_df["Inserted_Date"] = pd.to_datetime(filtered_df["Inserted_Date"]).dt.date

# 👉 Aggregate total count per date
date_summary = (
    filtered_df.groupby("Inserted_Date")
    .size()
    .reset_index(name="Total_Count")
)

# 👉 Operator breakdown for hover
operator_details = (
    filtered_df.groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

# 👉 Create hover text
hover_text = (
    operator_details.groupby("Inserted_Date")
    .apply(lambda x: "<br>".join(
        x["Operator_Code"] + ": " + x["Count"].astype(str)
    ))
    .reset_index(name="Details")
)

date_summary = date_summary.merge(hover_text, on="Inserted_Date", how="left")

# ✅ CREATE FIG FIRST
fig = px.bar(
    date_summary,
    x="Inserted_Date",
    y="Total_Count",
    text="Total_Count"
)

# ✅ APPLY MULTI COLOR + HOVER AFTER FIG CREATED
fig.update_traces(
    textposition="outside",
    hovertemplate=
    "<b>Date:</b> %{x}<br>" +
    "<b>Total:</b> %{y}<br><br>" +
    "%{customdata}",
    customdata=date_summary["Details"],
    marker=dict(
        color=date_summary["Total_Count"],   # 🔥 multi-color
        colorscale="Turbo",
        showscale=False
    )
)

# ✅ Layout fix
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="black"),
    height=500,
    margin=dict(l=10, r=10, t=10, b=10),

    xaxis=dict(
        showgrid=False,
        showline=False,
        linewidth=2,
        linecolor="black"
    ),
    yaxis=dict(
        showgrid=False,
        gridcolor="lightgray",
        showline=False,
        linewidth=2,
        linecolor="black"
    )
)

st.plotly_chart(fig, use_container_width=True)
# ---------------------------
# TOP ROUTES
# ---------------------------
st.markdown('<div class="section">TOP ROUTES</div>', unsafe_allow_html=True)

route_df = (
    filtered_df.groupby(["From_Port", "To_Port"])
    .size()
    .reset_index(name="Count")
)

route_df["Route"] = route_df["From_Port"] + " → " + route_df["To_Port"]
route_df = route_df.sort_values(by="Count", ascending=False).head(10)

fig_route = px.bar(
    route_df,
    x="Count",
    y="Route",
    orientation="h",
    color="Route",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig_route.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="black"),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False, gridcolor="lightgray", showline=False, linecolor="black"),
    yaxis=dict(showgrid=False, showline=False, linecolor="black"),
    showlegend=False
)

st.plotly_chart(fig_route, use_container_width=True)

# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">SERVICE DISTRIBUTION (TOP 10)</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

top10 = service_df.head(10)
others = service_df["Count"][10:].sum()

if others > 0:
    top10.loc[len(top10)] = ["Others", others]

fig_service = px.bar(
    top10,
    x="Count",
    y="Service",
    orientation="h",
    text="Count",
    color="Service",
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig_service.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="black"),
    margin=dict(l=10, r=10, t=10, b=10),

    xaxis=dict(
        showgrid=False,
        gridcolor="lightgray",
        showline=False,
        linewidth=2,
        linecolor="black"
    ),
    yaxis=dict(
        showgrid=False,
        showline=False,
        linewidth=2,
        linecolor="black"
    ),
    showlegend=False
)

fig_service.update_traces(
    textposition="outside",
    marker=dict(line=dict(color="black", width=1))
)

st.plotly_chart(fig_service, use_container_width=True)
