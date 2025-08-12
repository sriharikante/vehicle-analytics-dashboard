import plotly.graph_objects as go
import plotly.io as pio

# Data for time series chart
months = ["Jan-23", "Feb-23", "Mar-23", "Apr-23", "May-23", "Jun-23", 
          "Jul-23", "Aug-23", "Sep-23", "Oct-23", "Nov-23", "Dec-23"]
data_2w = [850000, 920000, 1050000, 980000, 890000, 750000, 680000, 720000, 860000, 950000, 1100000, 1200000]
data_3w = [45000, 48000, 52000, 49000, 44000, 38000, 35000, 37000, 42000, 48000, 55000, 58000]
data_4w = [120000, 135000, 145000, 140000, 125000, 110000, 105000, 115000, 130000, 140000, 155000, 165000]

# Convert to abbreviated format (k for thousands)
data_2w_abbrev = [val/1000 for val in data_2w]
data_3w_abbrev = [val/1000 for val in data_3w]
data_4w_abbrev = [val/1000 for val in data_4w]

# Create figure
fig = go.Figure()

# Add traces using the specified brand colors
colors = ['#1FB8CD', '#DB4545', '#2E8B57']

fig.add_trace(go.Scatter(
    x=months,
    y=data_2w_abbrev,
    mode='lines+markers',
    name='2W',
    line=dict(color=colors[0], width=3),
    marker=dict(size=6),
    cliponaxis=False,
    hovertemplate='<b>%{fullData.name}</b><br>Month: %{x}<br>Registrations: %{y}k<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=months,
    y=data_3w_abbrev,
    mode='lines+markers',
    name='3W',
    line=dict(color=colors[1], width=3),
    marker=dict(size=6),
    cliponaxis=False,
    hovertemplate='<b>%{fullData.name}</b><br>Month: %{x}<br>Registrations: %{y}k<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=months,
    y=data_4w_abbrev,
    mode='lines+markers',
    name='4W',
    line=dict(color=colors[2], width=3),
    marker=dict(size=6),
    cliponaxis=False,
    hovertemplate='<b>%{fullData.name}</b><br>Month: %{x}<br>Registrations: %{y}k<extra></extra>'
))

# Update layout
fig.update_layout(
    title='Vehicle Registrations by Category',
    xaxis_title='Month',
    yaxis_title='Registrations (k)',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='center',
        x=0.5
    )
)

# Save the chart
fig.write_image('vahan_dashboard_preview.png')