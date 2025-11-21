"""
Streamlit Charts and Tables Demo
Demonstrates all chart types and custom styling capabilities
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Streamlit Charts Demo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Streamlit Charts & Tables Demo")
st.markdown("Демонстрация всех возможностей графиков и таблиц в Streamlit")

# Color scheme matching RightCareHome
COLORS = {
    "primary": "#1E2A44",
    "green": "#10B981",
    "red": "#EF4444",
    "blue": "#3B82F6",
    "purple": "#8B5CF6",
    "yellow": "#F59E0B"
}

# Sample data
care_homes_data = {
    "name": ["Sunshine Care", "Greenwood Manor", "Riverside Home", "Oakwood House", "Maple Gardens"],
    "weekly_cost": [850, 1200, 950, 1100, 1050],
    "cqc_rating": ["Good", "Outstanding", "Good", "Outstanding", "Good"],
    "distance_km": [2.5, 5.1, 3.8, 4.2, 6.0],
    "fsa_rating": ["green", "green", "yellow", "green", "green"]
}

df = pd.DataFrame(care_homes_data)

st.markdown("---")
st.header("📈 Plotly Charts (Рекомендуется)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Bar Chart - Weekly Costs")
    fig_bar = px.bar(
        df,
        x="name",
        y="weekly_cost",
        color="weekly_cost",
        color_continuous_scale=["#10B981", "#059669"],
        title="Weekly Costs by Care Home"
    )
    fig_bar.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter",
        title_font_size=16,
        title_font_color="#1E2A44"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Scatter Plot - Cost vs Distance")
    fig_scatter = px.scatter(
        df,
        x="distance_km",
        y="weekly_cost",
        size="weekly_cost",
        color="cqc_rating",
        color_discrete_map={
            "Outstanding": "#10B981",
            "Good": "#3B82F6",
            "Requires improvement": "#F59E0B",
            "Inadequate": "#EF4444"
        },
        title="Cost vs Distance Analysis"
    )
    fig_scatter.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.header("📊 Advanced Charts")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pie Chart - CQC Ratings Distribution")
    rating_counts = df["cqc_rating"].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=rating_counts.index,
        values=rating_counts.values,
        marker_colors=["#10B981", "#3B82F6", "#F59E0B", "#EF4444"],
        hole=0.3
    )])
    fig_pie.update_layout(
        title="CQC Ratings Distribution",
        font_family="Inter",
        title_font_color="#1E2A44"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Line Chart - Cost Trends")
    # Simulate trends
    months = pd.date_range("2024-01", periods=12, freq="M")
    trend_data = pd.DataFrame({
        "month": months,
        "average_cost": np.random.randint(900, 1200, 12),
        "median_cost": np.random.randint(850, 1100, 12)
    })
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=trend_data["month"],
        y=trend_data["average_cost"],
        name="Average Cost",
        line=dict(color="#10B981", width=3),
        mode="lines+markers"
    ))
    fig_line.add_trace(go.Scatter(
        x=trend_data["month"],
        y=trend_data["median_cost"],
        name="Median Cost",
        line=dict(color="#3B82F6", width=3),
        mode="lines+markers"
    ))
    fig_line.update_layout(
        title="Cost Trends Over Time",
        xaxis_title="Month",
        yaxis_title="Cost (£/week)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter"
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")
st.header("📋 Tables with Custom Styling")

st.subheader("Styled DataFrame (Built-in)")
st.dataframe(
    df.style.format({
        "weekly_cost": "£{:.0f}",
        "distance_km": "{:.1f} km"
    }).background_gradient(
        subset=["weekly_cost"],
        cmap="Greens"
    ).applymap(
        lambda x: f"color: {'#10B981' if x == 'green' else '#F59E0B' if x == 'yellow' else '#EF4444'}",
        subset=["fsa_rating"]
    ),
    use_container_width=True,
    height=300
)

st.subheader("Custom HTML Table (Premium Styling)")
st.markdown("""
<style>
.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}
.custom-table thead {
    background: linear-gradient(135deg, #1E2A44 0%, #2D3A5A 100%);
    color: white;
}
.custom-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
    font-size: 14px;
}
.custom-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #E5E7EB;
}
.custom-table tbody tr:hover {
    background-color: #F9FAFB;
}
.custom-table tbody tr:last-child td {
    border-bottom: none;
}
.rating-good { color: #10B981; font-weight: 600; }
.rating-outstanding { color: #10B981; font-weight: 700; }
.cost-high { color: #EF4444; font-weight: 600; }
.cost-medium { color: #F59E0B; font-weight: 600; }
.cost-low { color: #10B981; font-weight: 600; }
</style>

<table class="custom-table">
    <thead>
        <tr>
            <th>Care Home</th>
            <th>Weekly Cost</th>
            <th>CQC Rating</th>
            <th>Distance</th>
            <th>FSA Rating</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Sunshine Care</td>
            <td class="cost-low">£850</td>
            <td class="rating-good">Good</td>
            <td>2.5 km</td>
            <td style="color: #10B981;">✅ Green</td>
        </tr>
        <tr>
            <td>Greenwood Manor</td>
            <td class="cost-high">£1,200</td>
            <td class="rating-outstanding">Outstanding</td>
            <td>5.1 km</td>
            <td style="color: #10B981;">✅ Green</td>
        </tr>
        <tr>
            <td>Riverside Home</td>
            <td class="cost-medium">£950</td>
            <td class="rating-good">Good</td>
            <td>3.8 km</td>
            <td style="color: #F59E0B;">⚠️ Yellow</td>
        </tr>
        <tr>
            <td>Oakwood House</td>
            <td class="cost-high">£1,100</td>
            <td class="rating-outstanding">Outstanding</td>
            <td>4.2 km</td>
            <td style="color: #10B981;">✅ Green</td>
        </tr>
        <tr>
            <td>Maple Gardens</td>
            <td class="cost-medium">£1,050</td>
            <td class="rating-good">Good</td>
            <td>6.0 km</td>
            <td style="color: #10B981;">✅ Green</td>
        </tr>
    </tbody>
</table>
""", unsafe_allow_html=True)

st.markdown("---")
st.header("🎨 Color Schemes")

st.subheader("RightCareHome Color Palette")
col1, col2, col3, col4, col5, col6 = st.columns(6)

colors_display = [
    ("Primary", "#1E2A44"),
    ("Green", "#10B981"),
    ("Red", "#EF4444"),
    ("Blue", "#3B82F6"),
    ("Purple", "#8B5CF6"),
    ("Yellow", "#F59E0B")
]

for i, (name, color) in enumerate(colors_display):
    with [col1, col2, col3, col4, col5, col6][i]:
        st.markdown(f"""
        <div style="background: {color}; 
                    color: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    text-align: center;
                    font-weight: 600;">
            {name}<br>
            <small>{color}</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.header("📊 Chart Types Available in Streamlit")

chart_types = {
    "Plotly": [
        "Bar charts", "Line charts", "Scatter plots", "Pie charts",
        "3D charts", "Maps", "Heatmaps", "Candlestick charts"
    ],
    "Altair": [
        "Vega-Lite charts", "Interactive visualizations", "Layered charts"
    ],
    "Matplotlib": [
        "Custom plots", "Scientific visualizations", "Publication-quality charts"
    ],
    "Built-in": [
        "st.line_chart()", "st.bar_chart()", "st.area_chart()", "st.map()"
    ]
}

for chart_lib, types in chart_types.items():
    with st.expander(f"📈 {chart_lib}"):
        for chart_type in types:
            st.markdown(f"• {chart_type}")

st.markdown("---")
st.header("✅ Вывод")

st.success("""
**Streamlit отлично поддерживает:**

✅ **Графики и диаграммы:**
   - Plotly (интерактивные, профессиональные)
   - Altair (декларативные, красивые)
   - Matplotlib (научные графики)
   - Встроенные простые графики

✅ **Таблицы с кастомными цветами:**
   - Pandas Styler (градиенты, условное форматирование)
   - HTML таблицы (полный контроль)
   - Streamlit Dataframe (базовое форматирование)

✅ **Цветовые схемы:**
   - Полный контроль через CSS
   - Интеграция с вашей палитрой (#1E2A44, #10B981, #EF4444)
   - Условное форматирование по значениям
""")

