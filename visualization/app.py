import streamlit as st
import pandas as pd
from datetime import datetime, timezone


def get_data(search_query, type_search):
    search_query = search_query.split()
    df = pd.read_csv('../data/out/proccessed.csv')
    df['top_words'] = df['top_words'].astype(str)
    filtered_df = df[df['type'] == 'post']
    if type_search == 1:
        return filtered_df
    condition = filtered_df['text'].str.contains('|'.join(search_query), case=False)
    filtered_df = filtered_df[condition]
    return filtered_df


# Set the title of the app
st.title('Mental Health App')

# Add a header
st.text('Mental health is crucial because it influences every aspect of our lives, \n'
        'from our relationships and work productivity to our overall happiness \n'
        'and quality of life.')

# Add a text input widget
name = st.text_input('Enter your name:')

# Add a button
if st.button('Submit'):
    st.write(f'Hello, {name}! Nice to meet you.')

# Add a slider
age = st.slider('Select your age', 0, 100, 25)

# Display the selected age
st.write(f'You selected: {age} years old')

gender = st.selectbox('Select your gender', ('Male', 'Female', 'Other'))

search_input = st.text_input(f'Please {name} enter keywords related to your mental unwellness:')

if st.button('Search'):
    st.text(f"Searching all information related to {search_input}....")
    if search_input == "":
        df_result = get_data(search_input, 1)
    else:
        search_input = search_input + ' ' + str(age) + ' ' + str(name)
        df_result = get_data(search_input, 2)
    for index, row in df_result.iterrows():
        st.write("Date: ", datetime.utcfromtimestamp(row['created_utc']).replace(tzinfo=timezone.utc).astimezone(
            tz=None).strftime('%d-%m-%Y %H:%M'))
        st.write(row['text'], unsafe_allow_html=True)
        if row['urls'] is not None:
            st.write(f"URL: https://www.reddit.com/r/mentalhealth/comments/{row['id']}")
        st.write("---------------------------------------------------")
