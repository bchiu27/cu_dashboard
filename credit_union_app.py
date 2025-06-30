import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="Credit Union Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Credit Union Dashboard")

# Load data from Excel file
@st.cache_data
def load_data():
    df = pd.read_excel(
        "credit_union_data.xlsx",
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
# region
# Create figure
# fig = go.Figure()

# # Add a trace for each credit union
# for credit_union in df['name'].unique():
#     subset = df[df['name'] == credit_union]
#     fig.add_trace(
#         go.Scatter(
#             x=subset['year'],
#             y=subset['total_comp'],
#             name=credit_union,
#             visible=False,  # Start with all traces hidden
#             hovertemplate= '<b>CEO Name:</b> %{customdata[2]}<br>' +
#                             '<b>Total Compensation:</b> $%{y:,.0f}<br>' +
#                             '<b>Compensation:</b> $%{customdata[0]:,.0f}<br>' + 
#                             '<b>Other Compensation:</b> $%{customdata[1]:,.0f}<br>' +    
#                         '<extra></extra>',                         
#             customdata=subset[['compensation', 'other_comp', 'ceo_name']].values,
#         )
#     )

# # Make first trace visible
# fig.data[0].visible = True

# # Create dropdown menu with shapes for CEO changes
# buttons = []
# for i, name in enumerate(df['name'].unique()):
#     subset = df[df['name'] == name]
#     ceo_change_years = subset[subset['ceo_change'] == True]['year'].tolist()
#     ma_years = subset[subset['m_or_a'] == True]['year'].tolist()
#
#     # Create shapes for vertical lines: green for CEO changes, brown for mergers/acquisitions
#     shapes = []
#     all_years = sorted(set(ceo_change_years + ma_years))  # Get unique years

#     for year in all_years:
#         if year in ceo_change_years and year in ma_years:
#             # Add offset lines for overlaps
#             shapes.append(dict(
#                 type="line", x0=year-0.03, x1=year-0.03,
#                 y0=0, y1=1, yref="paper",
#                 line=dict(color="green", width=3, dash="dash")
#             ))
#             shapes.append(dict(
#                 type="line", x0=year+0.03, x1=year+0.03,
#                 y0=0, y1=1, yref="paper", 
#                 line=dict(color="brown", width=3, dash="dash")
#             ))
#         else:
#             # Add normal lines for non-overlaps
#             if year in ceo_change_years:
#                 shapes.append(dict(
#                     type="line", x0=year, x1=year,
#                     y0=0, y1=1, yref="paper",
#                     line=dict(color="green", width=3, dash="dash")
#                 ))
#             if year in ma_years:
#                 shapes.append(dict(
#                     type="line", x0=year, x1=year,
#                     y0=0, y1=1, yref="paper",
#                     line=dict(color="brown", width=3, dash="dash")
#                 ))
    
#     # Set trace visibility
#     visibility = [False] * len(fig.data)
#     visibility[i] = True
    
#     buttons.append(
#         dict(
#             label=name,
#             method='update',
#             args=[
#                 {'visible': visibility},
#                 {
#                     'title': f"Executive Compensation: {name}",
#                     'shapes': shapes
#                 }
#             ]
#         )
#     )

# # Create initial shapes for the first credit union
# first_cu = df['name'].unique()[0]
# first_subset = df[df['name'] == first_cu]
# initial_shapes = []

# # Add CEO change lines for first credit union
# for year in first_subset[first_subset['ceo_change'] == True]['year'].tolist():
#     initial_shapes.append(
#         dict(
#             type="line",
#             x0=year, x1=year,
#             y0=0, y1=1,
#             yref="paper",
#             line=dict(color="green", width=3, dash="dash")
#         )
#     )

# # Add M&A lines for first credit union
# for year in first_subset[first_subset['m_or_a'] == True]['year'].tolist():
#     initial_shapes.append(
#         dict(
#             type="line",
#             x0=year, x1=year,
#             y0=0, y1=1,
#             yref="paper",
#             line=dict(color="brown", width=3, dash="dash")
#         )
#     )

# # Update layout with dropdown
# fig.update_layout(
#     updatemenus=[{
#         'buttons': buttons,
#         'direction': 'down',
#         'showactive': True,
#         'x': 0.25,
#         'y': 1.2,
#         'pad': {'r': 10, 't': 10}
#     }],
#     title='Executive Compensation Over Time',
#     xaxis_title='Year',
#     yaxis_title='Total Compensation (USD)',
#     height=600,
#     shapes=initial_shapes  
# )

# # Add annotations to explain the vertical lines
# fig.add_annotation(
#     text="Green dashed lines = CEO Changes",
#     x=0.02, y=0.98,
#     xref="paper", yref="paper",
#     showarrow=False,
#     font=dict(color="green", size=12),
#     bgcolor="rgba(255,255,255,0.8)"
# )
# fig.add_annotation(
#     text="Brown dashed lines = Merger/Acquisition",
#     x=0.02, y=0.93,
#     xref="paper", yref="paper",
#     showarrow=False,
#     font=dict(color="brown", size=12),
#     bgcolor="rgba(255,255,255,0.8)"
# )

# fig.update_xaxes(
#     tickmode='linear',  
#     dtick=1,        
#     tick0=df['year'].min(),  
#     tickformat='d')

# # Display the main plot with dropdown
# st.plotly_chart(fig, use_container_width=True)
#endregion

# Streamlit dropdown
st.subheader("Executive Compensation Section")
selected_cu = st.selectbox('Select Credit Union', df['name'].unique())

# Filter data for selected credit union
selected_subset = df[df['name'] == selected_cu]
shapes_selected = []
ceo_change_years = selected_subset[selected_subset['ceo_change'] == True]['year'].tolist()
ma_years = selected_subset[selected_subset['m_or_a'] == True]['year'].tolist()

all_years = sorted(set(ceo_change_years + ma_years))

# Add vertical lines for the CEO name change years and Merger and Acquisition years

def add_financial_vertical_lines(fig, selected_cu_name):
    ceo_subset = selected_subset[selected_subset['name'] == selected_cu_name] if not selected_subset.empty else pd.DataFrame()
    if not ceo_subset.empty:
        ceo_change_years = ceo_subset[ceo_subset['ceo_change'] == True]['year'].tolist()
        ma_years = ceo_subset[ceo_subset['m_or_a'] == True]['year'].tolist()
        all_years = sorted(set(ceo_change_years + ma_years))
        
        for year in all_years:
            if year in ceo_change_years and year in ma_years:
                # CEO change line (slightly left)
                fig.add_vline(x=year-0.1, line_color="green", line_width=3, line_dash="dash")
                # M&A line (slightly right)  
                fig.add_vline(x=year+0.1, line_color="brown", line_width=3, line_dash="dash")
            else:
                if year in ceo_change_years:
                    fig.add_vline(x=year, line_color="green", line_width=3, line_dash="dash")
                if year in ma_years:
                    fig.add_vline(x=year, line_color="brown", line_width=3, line_dash="dash")
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
        
    return fig

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


# for year in all_years:
#     if year in ceo_change_years and year in ma_years:
#         # Modify the shapes to offset overlapping years
#         # CEO change line (slightly left)
#         shapes_selected.append(dict(
#             type="line", x0=year-0.1, x1=year-0.1,
#             y0=0, y1=1, yref="paper",
#             line=dict(color="green", width=3, dash="dash")
#         ))
#         # M&A line (slightly right)  
#         shapes_selected.append(dict(
#             type="line", x0=year+0.1, x1=year+0.1,
#             y0=0, y1=1, yref="paper",
#             line=dict(color="brown", width=3, dash="dash")
#         ))
#     else:
#         if year in ceo_change_years:
#             shapes_selected.append(dict(
#                 type="line", x0=year, x1=year,
#                 y0=0, y1=1, yref="paper",
#                 line=dict(color="green", width=3, dash="dash")
#             ))
#         if year in ma_years:
#             shapes_selected.append(dict(
#                 type="line", x0=year, x1=year,
#                 y0=0, y1=1, yref="paper",
#                 line=dict(color="brown", width=3, dash="dash")
#             ))
add_financial_vertical_lines(fig_selected, selected_cu)
fig_selected.update_layout(
    title=f"Total Executive Compensation: {selected_cu}",
    xaxis_title='Year',
    yaxis_title='Total Compensation (USD)',
    height=600,
    shapes=shapes_selected,
    hoverlabel=dict(
            bgcolor='white',
            font=dict(color='black', size=12),
            bordercolor='black'
    )
)

fig_selected.update_xaxes(
    tickmode='linear',  
    dtick=1,        
    tick0=selected_subset['year'].min(),  
    tickformat='d')

# Display the selected credit union plot
st.plotly_chart(fig_selected, use_container_width=True)

#load financial data
@st.cache_data
def load_financial_data():
    return pd.read_excel(
        "credit_union_data.xlsx",
        sheet_name="Combined_Financials_2",
        dtype={
            "name": str,
            "ein": str,
            "Year": int,
            "Total Revenue": float,
            "Total Expenses": float,
            "Net Income": float,
            "Total Assets": float,
            "Total Liabilities": float,
            "Investment Income": float,
            "Cash On Hand": float,
            "Total Loans & Leases": float,
            "Commercial and Industrial Loans": float
        })

df_financial = load_financial_data()

st.subheader("Financial Performance Section")

# Use the same selected credit union from the dropdown above
selected_cu_financial = selected_cu  

# Filter financial data for selected credit union
selected_financial_subset = df_financial[df_financial['name'] == selected_cu_financial]

# Define available financial variables
financial_variables = [
    'Total Revenue', 'Total Expenses', 'Net Income', 'Total Assets', 
    'Total Liabilities', 'Investment Income', 'Cash On Hand', 
    'Total Loans & Leases', 'Commercial and Industrial Loans'
]

# Create 2 by 2 layout using columns
col1, col2 = st.columns(2)

with col1:
    # Graph 1: Selectable Financial Variable
    selected_var1 = st.selectbox('Select Financial Variable (Graph 1):', financial_variables, index=0)
    data_subset1 = selected_financial_subset.dropna(subset=[selected_var1]).sort_values('Year')
    
    st.subheader(f"{selected_var1}")
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=data_subset1['Year'],
            y=data_subset1[selected_var1],
            name=selected_var1,
            line=dict(color='blue'),
            hovertemplate='<b>Year:</b> %{x}<br>' +
                         f'<b>{selected_var1}:</b> $%{{y:,.0f}}<br>' +
                         '<extra></extra>'
        )
    )
    fig1 = add_financial_vertical_lines(fig1, selected_cu_financial)
    fig1.update_layout(
        title=f"{selected_var1}: {selected_cu_financial}",
        xaxis_title='Year',
        yaxis_title=f'{selected_var1} (USD)',
        height=400,
        hoverlabel=dict(
            bgcolor='white',
            font=dict(color='black', size=12),
            bordercolor='black'
        )
    )
    fig1.update_xaxes(tickmode='linear', dtick=1, tickformat='d')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Graph 3: Selectable Financial Variable
    selected_var3 = st.selectbox('Select Financial Variable (Graph 3):', financial_variables, index=2)
    data_subset3 = selected_financial_subset.dropna(subset=[selected_var3]).sort_values('Year')
    
    st.subheader(f"{selected_var3}")
    fig3 = go.Figure()
    fig3.add_trace(
        go.Scatter(
            x=data_subset3['Year'],
            y=data_subset3[selected_var3],
            name=selected_var3,
            line=dict(color='green'),
            hovertemplate='<b>Year:</b> %{x}<br>' +
                         f'<b>{selected_var3}:</b> $%{{y:,.0f}}<br>' +
                         '<extra></extra>'
        )
    )
    fig3 = add_financial_vertical_lines(fig3, selected_cu_financial)
    fig3.update_layout(
        title=f"{selected_var3}: {selected_cu_financial}",
        xaxis_title='Year',
        yaxis_title=f'{selected_var3} (USD)',
        height=400,
       hoverlabel=dict(
            bgcolor='white',
            font=dict(color='black', size=12),
            bordercolor='black'
    )
    )
    fig3.update_xaxes(tickmode='linear', dtick=1, tickformat='d')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    # Graph 2: Selectable Financial Variable
    selected_var2 = st.selectbox('Select Financial Variable (Graph 2):', financial_variables, index=3)
    data_subset2 = selected_financial_subset.dropna(subset=[selected_var2]).sort_values('Year')
    
    st.subheader(f"{selected_var2}")
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=data_subset2['Year'],
            y=data_subset2[selected_var2],
            name=selected_var2,
            line=dict(color='red'),
            hovertemplate='<b>Year:</b> %{x}<br>' +
                         f'<b>{selected_var2}:</b> $%{{y:,.0f}}<br>' +
                         '<extra></extra>'
        )
    )
    fig2 = add_financial_vertical_lines(fig2, selected_cu_financial)
    fig2.update_layout(
        title=f"{selected_var2}: {selected_cu_financial}",
        xaxis_title='Year',
        yaxis_title=f'{selected_var2} (USD)',
        height=400,
        hoverlabel=dict(
            bgcolor='white',
            font=dict(color='black', size=12),
            bordercolor='black'
        )
    )
    fig2.update_xaxes(tickmode='linear', dtick=1, tickformat='d')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Graph 4: Selectable Financial Variable
    selected_var4 = st.selectbox('Select Financial Variable (Graph 4):', financial_variables, index=5)
    data_subset4 = selected_financial_subset.dropna(subset=[selected_var4]).sort_values('Year')
    
    st.subheader(f"{selected_var4}")
    fig4 = go.Figure()
    fig4.add_trace(
        go.Scatter(
            x=data_subset4['Year'],
            y=data_subset4[selected_var4],
            name=selected_var4,
            line=dict(color='purple'),
            hovertemplate='<b>Year:</b> %{x}<br>' +
                         f'<b>{selected_var4}:</b> $%{{y:,.0f}}<br>' +
                         '<extra></extra>'
        )
    )
    fig4 = add_financial_vertical_lines(fig4, selected_cu_financial)
    fig4.update_layout(
        title=f"{selected_var4}: {selected_cu_financial}",
        xaxis_title='Year',
        yaxis_title=f'{selected_var4} (USD)',
        height=400,
        hoverlabel=dict(
            bgcolor='white',
            font=dict(color='black', size=12),
            bordercolor='black'
        )
    )
    fig4.update_xaxes(tickmode='linear', dtick=1, tickformat='d')
    st.plotly_chart(fig4, use_container_width=True)

