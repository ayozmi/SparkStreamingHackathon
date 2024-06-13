import socket
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql.functions import col, regexp_extract, udf
from pyspark.ml.feature import IDF, CountVectorizer, RegexTokenizer
from pyspark.ml.feature import StopWordsRemover
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv("../.env")
path_to_python = os.getenv("MY_PYTHON_PATH")
os.environ['PYSPARK_PYTHON'] = path_to_python
os.environ['PYSPARK_DRIVER_PYTHON'] = path_to_python

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the root folder by going up one level from the current directory
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

logging_dir = os.path.join(root_dir, "logs/dataProcessing")
if not os.path.exists(logging_dir):
    os.makedirs(logging_dir)
logging_file = os.path.join(logging_dir, "logs.log")
logging.basicConfig(filename=logging_file, level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_references(df):
    df = df.withColumn('user_refs', regexp_extract('text', r'/u/(\w+)', 1)) \
        .withColumn('post_refs', regexp_extract('text', r'/r/(\w+)', 1)) \
        .withColumn('urls', regexp_extract('text', r'(http[s]?://\S+)', 1))
    return df


# def get_top_words(indices, words):
#     top_indices = indices.indices[:10]
#     return [words[idx] for idx in top_indices]


def get_top_words(features, vocabulary, num_words=10):
    feature_tuples = [(i, features[i]) for i in range(len(features))]
    sorted_features = sorted(feature_tuples, key=lambda x: -x[1])
    top_indices = [idx for idx, _ in sorted_features[:num_words]]
    return [vocabulary[idx] for idx in top_indices]


def process_data(spark, host='localhost', port=9999):
    while True:
        try:
            # Initialize socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((host, port))
            print("Socket initialized!")
            print("Listening on port: " + str(port))
            s.listen(1)
            conn, addr = s.accept()
        except socket.error as ser:
            print(ser)
            sys.exit()

        # Read data
        raw_data = []
        while True:
            data = conn.recv(1024)
            if not data:
                break
            raw_data.append(data)
        # print("Raw: ", raw_data)
        message = b''.join(raw_data).decode('utf-8')
        # Split the message on the delimiter
        messages = message.split('\n')
        all_data = []
        for msg in messages:
            if not msg.strip():
                continue

            # Convert string to JSON
            try:
                json_data = json.loads(msg)
                all_data.append(json_data)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                continue

        # Create DataFrame from JSON data
        raw_df = spark.read.json(spark.sparkContext.parallelize([all_data]))
        # raw_df.show()
        raw_df.toPandas().to_csv('../data/out/raw.csv', index=False)
        # raw_df.show()
        df_ref = get_references(raw_df)
        # df_ref.show()

        # Tokenize the text column
        tokenizer = RegexTokenizer(inputCol="text", outputCol="words", pattern="[^a-zA-Z]")
        words_df = tokenizer.transform(df_ref)
        remover = StopWordsRemover(outputCol="filter_words")
        remover.setInputCol("words")
        words_df = remover.transform(words_df)
        # words_df.show()
        # exit()

        # Compute TF
        cv = CountVectorizer(inputCol="words", outputCol="rawFeatures")
        cv_model = cv.fit(words_df)
        featurized_df = cv_model.transform(words_df)
        # featurized_df.show()
        # exit()

        # Compute IDF
        idf = IDF(inputCol="rawFeatures", outputCol="features")
        idf_model = idf.fit(featurized_df)
        tfidf_df = idf_model.transform(featurized_df)
        # tfidf_df.show()
        # exit()
        vocabulary = cv_model.vocabulary
        get_top_words_udf = udf(lambda features: get_top_words(features.toArray(), vocabulary), ArrayType(StringType()))
        tfidf_top_words_df = tfidf_df.withColumn("top_words", get_top_words_udf(col("features")))

        tfidf_top_words_df.toPandas().to_csv('../data/out/proccessed.csv', index=False)

        # exit()
        # Close the connection after processing the data
        conn.close()
        print(f"Connection with {addr} closed")


if __name__ == '__main__':
    spark = SparkSession.builder.appName("MentalHealthDataProcessing").getOrCreate()
    process_data(spark)
