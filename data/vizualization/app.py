import streamlit as st
import pandas as pd
import socket
import json


# Function to read data from a socket
def read_from_socket(host='localhost', port=9999, buffer_size=4096):
    data = b""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            part = s.recv(buffer_size)
            if not part:
                break
            data += part
    return data.decode('utf-8')


# Function to load and parse JSON data
def load_data(data):
    lines = data.split('\n')
    json_data = [json.loads(line) for line in lines if line]
    return pd.DataFrame(json_data)


# Main function to display the data
def main():
    st.title("Reddit Streaming Data Visualization")

    host = st.text_input("Socket Host", value='localhost')
    port = st.number_input("Socket Port", value=9999)
    
    if st.button('Load Data'):
        try:
            raw_data = read_from_socket(host, port)
            if raw_data:
                df = load_data(raw_data)
                st.write("Raw Data", df)

                # Visualization: Top words
                all_texts = ' '.join(df['text'].tolist())
                words = pd.Series(all_texts.split()).value_counts().head(10)
                
                st.subheader("Top 10 Words")
                st.bar_chart(words)

                # Visualization: Average Sentiment (if sentiment analysis is included in your data)
                if 'sentiment' in df.columns:
                    average_sentiment = df['sentiment'].mean()
                    st.subheader("Average Sentiment")
                    st.write(f"Average Sentiment Score: {average_sentiment}")

                # Visualization: Posts over time
                df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
                time_series = df.set_index('created_utc').resample('T').count()['id']
                
                st.subheader("Posts Over Time")
                st.line_chart(time_series)
        except ConnectionRefusedError:
            st.error("Connection refused. Please ensure the socket server is running and accessible.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
