import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="Credit Union Executive Compensation Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Credit Union Executive Compensation Dashboard")

# Load your data (add CEO change detection first)
@st.cache_data
def load_data():
    df = pd.read_excel(
        r"c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx",
        sheet_name="CEO_Comp",
        dtype={
            "name": str,
            "ein": str,
            "year": int,
            "total_comp": float,
            "ceo_name": str,
            "compensation": float
        })
    return df.sort_values(by=['name', 'year'])

df = load_data()

# Create figure
fig = go.Figure()

# Add a trace for each credit union
for credit_union in df['name'].unique():
    subset = df[df['name'] == credit_union]
    fig.add_trace(
        go.Scatter(
            x=subset['year'],
            y=subset['total_comp'],
            name=credit_union,
            visible=False,  # Start with all traces hidden
            hovertemplate= '<b>CEO Name:</b> %{customdata[2]}<br>' +
                            '<b>Total Compensation:</b> $%{y:,.0f}<br>' +
                            '<b>Compensation:</b> $%{customdata[0]:,.0f}<br>' + 
                            '<b>Other Compensation:</b> $%{customdata[1]:,.0f}<br>' +    
                        '<extra></extra>',                         
            customdata=subset[['compensation', 'other_comp', 'ceo_name']].values,
        )
    )

# Make first trace visible
fig.data[0].visible = True

# Create dropdown menu with shapes for CEO changes
buttons = []
for i, name in enumerate(df['name'].unique()):
    subset = df[df['name'] == name]
    ceo_change_years = subset[subset['ceo_change'] == True]['year'].tolist()
    ma_years = subset[subset['m_or_a'] == True]['year'].tolist()
    
    # Create shapes for vertical lines: green for CEO changes, brown for mergers/acquisitions
    shapes = []
    all_years = sorted(set(ceo_change_years + ma_years))  # Get unique years

    for year in all_years:
        if year in ceo_change_years and year in ma_years:
            # Add offset lines for overlaps
            shapes.append(dict(
                type="line", x0=year-0.03, x1=year-0.03,
                y0=0, y1=1, yref="paper",
                line=dict(color="green", width=3, dash="dash")
            ))
            shapes.append(dict(
                type="line", x0=year+0.03, x1=year+0.03,
                y0=0, y1=1, yref="paper", 
                line=dict(color="brown", width=3, dash="dash")
            ))
        else:
            # Add normal lines for non-overlaps
            if year in ceo_change_years:
                shapes.append(dict(
                    type="line", x0=year, x1=year,
                    y0=0, y1=1, yref="paper",
                    line=dict(color="green", width=3, dash="dash")
                ))
            if year in ma_years:
                shapes.append(dict(
                    type="line", x0=year, x1=year,
                    y0=0, y1=1, yref="paper",
                    line=dict(color="brown", width=3, dash="dash")
                ))
    
    # Set trace visibility
    visibility = [False] * len(fig.data)
    visibility[i] = True
    
    buttons.append(
        dict(
            label=name,
            method='update',
            args=[
                {'visible': visibility},
                {
                    'title': f"Executive Compensation: {name}",
                    'shapes': shapes
                }
            ]
        )
    )

# Create initial shapes for the first credit union
first_cu = df['name'].unique()[0]
first_subset = df[df['name'] == first_cu]
initial_shapes = []

# Add CEO change lines for first credit union
for year in first_subset[first_subset['ceo_change'] == True]['year'].tolist():
    initial_shapes.append(
        dict(
            type="line",
            x0=year, x1=year,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="green", width=3, dash="dash")
        )
    )

# Add M&A lines for first credit union
for year in first_subset[first_subset['m_or_a'] == True]['year'].tolist():
    initial_shapes.append(
        dict(
            type="line",
            x0=year, x1=year,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="brown", width=3, dash="dash")
        )
    )

# Update layout with dropdown
fig.update_layout(
    updatemenus=[{
        'buttons': buttons,
        'direction': 'down',
        'showactive': True,
        'x': 0.25,
        'y': 1.2,
        'pad': {'r': 10, 't': 10}
    }],
    title='Executive Compensation Over Time - Select Credit Union',
    xaxis_title='Year',
    yaxis_title='Total Compensation (USD)',
    height=600,
    shapes=initial_shapes  
)

# Add annotations to explain the vertical lines
fig.add_annotation(
    text="Green dashed lines = CEO Changes",
    x=0.02, y=0.98,
    xref="paper", yref="paper",
    showarrow=False,
    font=dict(color="green", size=12),
    bgcolor="rgba(255,255,255,0.8)"
)
fig.add_annotation(
    text="Brown dashed lines = Merger/Acquisition",
    x=0.02, y=0.93,
    xref="paper", yref="paper",
    showarrow=False,
    font=dict(color="brown", size=12),
    bgcolor="rgba(255,255,255,0.8)"
)

fig.update_xaxes(
    tickmode='linear',  
    dtick=1,        
    tick0=df['year'].min(),  
    tickformat='d')

# Display the main plot with dropdown
st.plotly_chart(fig, use_container_width=True)

# Alternative selection method using Streamlit selectbox
st.subheader("Alternative Credit Union Selection")
selected_cu = st.selectbox('Select Credit Union', df['name'].unique())

# Filter data for selected credit union
selected_subset = df[df['name'] == selected_cu]

# Create a separate figure for the selected credit union
fig_selected = go.Figure()

fig_selected.add_trace(
    go.Scatter(
        x=selected_subset['year'],
        y=selected_subset['total_comp'],
        name=selected_cu,
        hovertemplate= '<b>CEO Name:</b> %{customdata[2]}<br>' +
                        '<b>Total Compensation:</b> $%{y:,.0f}<br>' +
                        '<b>Compensation:</b> $%{customdata[0]:,.0f}<br>' + 
                        '<b>Other Compensation:</b> $%{customdata[1]:,.0f}<br>' +    
                    '<extra></extra>',                         
        customdata=selected_subset[['compensation', 'other_comp', 'ceo_name']].values,
    )
)

# Add vertical lines for CEO changes and M&A for selected credit union
shapes_selected = []
ceo_change_years = selected_subset[selected_subset['ceo_change'] == True]['year'].tolist()
ma_years = selected_subset[selected_subset['m_or_a'] == True]['year'].tolist()

all_years = sorted(set(ceo_change_years + ma_years))

for year in all_years:
    if year in ceo_change_years and year in ma_years:
        # Modify the shapes to offset overlapping years
        # CEO change line (slightly left)
        shapes_selected.append(dict(
            type="line", x0=year-0.1, x1=year-0.1,
            y0=0, y1=1, yref="paper",
            line=dict(color="green", width=3, dash="dash")
        ))
        # M&A line (slightly right)  
        shapes_selected.append(dict(
            type="line", x0=year+0.1, x1=year+0.1,
            y0=0, y1=1, yref="paper",
            line=dict(color="brown", width=3, dash="dash")
        ))
    else:
        if year in ceo_change_years:
            shapes_selected.append(dict(
                type="line", x0=year, x1=year,
                y0=0, y1=1, yref="paper",
                line=dict(color="green", width=3, dash="dash")
            ))
        if year in ma_years:
            shapes_selected.append(dict(
                type="line", x0=year, x1=year,
                y0=0, y1=1, yref="paper",
                line=dict(color="brown", width=3, dash="dash")
            ))

fig_selected.update_layout(
    title=f"Executive Compensation: {selected_cu}",
    xaxis_title='Year',
    yaxis_title='Total Compensation (USD)',
    height=600,
    shapes=shapes_selected
)

fig_selected.update_xaxes(
    tickmode='linear',  
    dtick=1,        
    tick0=selected_subset['year'].min(),  
    tickformat='d')

# Display the selected credit union plot
st.plotly_chart(fig_selected, use_container_width=True)
