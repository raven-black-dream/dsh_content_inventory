import pandas as pd
import plotly.express as px
import streamlit as st
from tqdm.auto import tqdm

tqdm.pandas()

@st.cache_data
def load_data():
    df = pd.read_csv('data/term_counts_reshaped.csv')
    if not 'priority' in df.columns.to_list():
        df['priority'] = 'Low'
    if not 'short_list' in df.columns.to_list():
        df['short_list'] = False
    return df

@st.cache_data
def get_terms():
    if 'data' in st.session_state:
        terms = st.session_state['data']['term'].unique()
    else:
        df = load_data()
        terms = df['term'].unique()
    return terms

if not "data" in st.session_state:
    st.session_state['data'] = load_data()
    st.session_state['terms'] = get_terms()
    st.session_state['filter'] = ''

with st.sidebar:
    st.subheader("Filter the Data")
    with st.form('filter_form'):
        filter = st.selectbox(label='Filter', options=st.session_state.terms)
        submit = st.form_submit_button("Submit")

        if submit:
            st.session_state['filter'] = filter

st.title("Term Count Tool")

st.subheader("Sorted List of Terms")

initial: pd.DataFrame = st.session_state['data'].groupby('term').agg({'count': 'sum'})
initial.sort_values(by='count', ascending=False, inplace=True)
initial['priority'] = 'Low'
initial['short_list'] = False
edited = st.data_editor(initial,
                        key="edited",
                        column_config={
                            'term': "Term",
                            'count': st.column_config.NumberColumn(
                                "Count",
                            ),
                            'priority': st.column_config.SelectboxColumn(
                                'Priority',
                                options=['Low', "Normal", "High"]
                            ),
                            'short_list': st.column_config.CheckboxColumn(
                                'Short List',
                            )
                        }, use_container_width=True
                        )

if st.session_state['edited']['edited_rows'] is not {}:
    for row, edits in st.session_state['edited']['edited_rows'].items():
        for column, value in edits.items():
            st.session_state['data'].loc[row, column] = value
    st.session_state['data'].to_csv('data/term_counts_reshaped.csv')

st.subheader("Filtered Term Distribution")

if st.session_state['filter'] is not None:
    col1, col2 = st.columns(2)
    filtered: pd.DataFrame = st.session_state['data'].copy()
    filtered = filtered[filtered['term'] == st.session_state['filter']]
    with col1:       
        st.dataframe(filtered.groupby('high_level').agg({'count': 'sum'}), use_container_width=True)
    with col2:
        temp = filtered[filtered['count'] != 0].copy()
        st.write(temp['url'].unique())



    
