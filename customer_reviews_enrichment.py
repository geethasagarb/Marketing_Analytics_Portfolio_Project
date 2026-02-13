#pip install pandas nltk pyodbc sqlalchemy

import pandas as pd
import pyodbc
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#Download the VADER lexicon for sentiment analysis if not already present
nltk.download('vader_lexicon')

# Define a function to fetch data froma a SQL database using a SQL Query
def fetch_data_from_sql():
    #Define the connection string with parameters for the database connection
    conn_str = (
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=LAPTOP-QTBIBV95\SQLEXPRESS;'
        'Database=PortfolioProject_MarketingAnalytics;'
        'Trusted_Connection=yes;'
    )
    #Establish a connection to the database
    conn = pyodbc.connect(conn_str)
    #Define the SQL query to fetch customer reviews data
    query = "SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM dbo.customer_reviews"
    #Execute the query and fetch the data into a DataFrame
    df = pd.read_sql_query(query, conn)

    #Close the database connection
    conn.close()
    #Return the fetched data as a DataFrame
    return df

#Fetch the customer reviews data from the SQL database
customer_reviews_df = fetch_data_from_sql()

#Initialize the VADER sentiment intensity analyzer for analyzing the sentiment of text data
sia = SentimentIntensityAnalyzer()

#Define a function to calculate sentiment scores using VADER
def calculate_sentiment(review):
    #Get the sentiment scores for the review text
    sentiment = sia.polarity_scores(review)
    #Return the compound sentiment score which is a normalized score between -1 (negative) and 1 (positive)
    return sentiment['compound']

#Define a function to categorize the sentiment using both the sentiment score and the review rating
def categorize_sentiment(score,rating):
    #use both the text sentiment score and the numerical rating to determine sentiment category
    if score > 0.05: #Positive sentiment score
        if rating >=4:
            return 'Positive' # High rating and positive sentiment
        elif rating ==3:
            return 'Mixed Positive' # Neutral rating but positive sentiment
        else:
            return 'Mixed Negative' # Low rating but positive sentiment
    elif score < -0.05: #Negative sentiment score
        if rating <=2:
            return 'Negative' # Low rating and negative sentiment
        elif rating ==3:
            return 'Mixed Negative' # Neutral rating but negative sentiment
        else:
            return 'Mixed Positive' # High rating but negative sentiment
    else: #Neutral sentiment score
        if rating >=4:
            return 'Positive' # High rating but neutral sentiment
        elif rating <= 2:
            return 'Negative' # Low rating but neutral sentiment
        else:
            return 'Neutral' # Neutral rating and neutral sentiment
        
#Define function to bucket sentiment scores into text ranges
def bucket_sentiment(score):
    if score >= 0.5:
        return '0.5 to 1.0' # Strongly Positive sentiment
    elif 0.0 <= score < 0.5:
        return '0.0 to 0.49' # Mildly Positive sentiment
    elif -0.5 <= score < 0.0:
        return '-0.49 to 0.0' # Mildly Negative sentiment
    else:
        return '-1.0 to -0.5' # Strongly Negative sentiment
    
#Apply sentiment analysis to calculate sentiment scores for each review
customer_reviews_df['SentimentScore'] = customer_reviews_df['ReviewText'].apply(calculate_sentiment)

#Apply sentiment categorization using both text and rating
customer_reviews_df['SentimentCategory'] = customer_reviews_df.apply(
    lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1)

#Apply sentiment bucketing to categorize scores into defined ranges
customer_reviews_df['SentimentBucket'] = customer_reviews_df['SentimentScore'].apply(bucket_sentiment)

#Display the first few rows of the DataFrame with sentiment scores, categories, and buckets
print(customer_reviews_df.head())

#Save the DataFrame with sentiment scores, categories, and buckets into a new CSV file
customer_reviews_df.to_csv('fact_customer_reviews_with_sentiment.csv', index=False)