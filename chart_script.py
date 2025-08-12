import plotly.graph_objects as go

# Define component positions and data
components = [
    {"name": "Vahan Portal", "tech": "Gov Portal", "x": 1, "y": 6},
    {"name": "Web Scraper", "tech": "Selenium+BS", "x": 1, "y": 5}, 
    {"name": "Data Process", "tech": "Pandas+NumPy", "x": 1, "y": 4},
    {"name": "Data Storage", "tech": "CSV/DB", "x": 1, "y": 3},
    {"name": "Streamlit App", "tech": "Streamlit", "x": 1, "y": 2},
    {"name": "Deploy Opts", "tech": "Cloud", "x": 1, "y": 1},
    {"name": "End Users", "tech": "Web Browser", "x": 1, "y": 0}
]

# Colors from brand palette
colors = ['#1FB8CD', '#DB4545', '#2E8B57', '#5D878F', '#D2BA4C', '#B4413C', '#964325']

fig = go.Figure()

# Add invisible scatter points to set up the coordinate system
fig.add_trace(go.Scatter(
    x=[0.5, 1.5], 
    y=[-0.5, 6.5],
    mode='markers',
    marker=dict(size=0, color='white'),
    showlegend=False,
    hoverinfo='skip'
))

# Add rectangular shapes for each component
shapes = []
annotations = []

for i, comp in enumerate(components):
    # Add rectangle shape
    shapes.append(dict(
        type="rect",
        x0=comp["x"]-0.3, y0=comp["y"]-0.15,
        x1=comp["x"]+0.3, y1=comp["y"]+0.15,
        fillcolor=colors[i],
        line=dict(color="white", width=2),
        opacity=0.8
    ))
    
    # Add main label
    annotations.append(dict(
        x=comp["x"], y=comp["y"]+0.05,
        text=f"<b>{comp['name']}</b>",
        showarrow=False,
        font=dict(color="white", size=12),
        xanchor="center", yanchor="middle"
    ))
    
    # Add tech label
    annotations.append(dict(
        x=comp["x"], y=comp["y"]-0.05,
        text=comp["tech"],
        showarrow=False,
        font=dict(color="white", size=10),
        xanchor="center", yanchor="middle"
    ))

# Add arrows between components
for i in range(len(components)-1):
    current_y = components[i]["y"]
    next_y = components[i+1]["y"]
    
    shapes.append(dict(
        type="line",
        x0=1, y0=current_y-0.15,
        x1=1, y1=next_y+0.15,
        line=dict(color="#333333", width=3),
    ))
    
    # Add arrowhead
    annotations.append(dict(
        x=1, y=next_y+0.18,
        text="▼",
        showarrow=False,
        font=dict(color="#333333", size=14),
        xanchor="center", yanchor="middle"
    ))

fig.update_layout(
    title="Vahan Dashboard Architecture",
    shapes=shapes,
    annotations=annotations,
    xaxis=dict(
        range=[0.4, 1.6],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    yaxis=dict(
        range=[-0.5, 6.5],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    plot_bgcolor='white',
    showlegend=False
)

# Save the chart
fig.write_image("vahan_architecture_flow.png")