import streamlit as st
import pandas as pd
import plotly.express as px
from transformers import pipeline
from camel_tools.utils.normalize import normalize_alef_maksura_ar, normalize_teh_marbuta_ar
from deep_translator import GoogleTranslator
import re
import io
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.pyplot as plt

# Read dataset
df = pd.read_csv(r'C:\Users\noura\OneDrive\Desktop\university\arabic sentiment analysis project\notebooks\elmenus_reviews_predicted.csv')

st.set_page_config(page_title="Elmenus Reviews Sentiment Analysis", layout="wide")

st.title("Elmenus Reviews Analysis")

# Preprocess input text
def preprocess_arabic(text):
    text = normalize_alef_maksura_ar(text)
    text = normalize_teh_marbuta_ar(text)
    text = re.sub(r'[^\w\s]', '', text)
    return text

# Load fine-tuned model
@st.cache_resource
def load_model():
    return pipeline(
        'text-classification',
        model=r'C:\Users\noura\OneDrive\Desktop\university\arabic sentiment analysis project\notebooks\fine_tuned_bert_mini_arabic',
        tokenizer=r'C:\Users\noura\OneDrive\Desktop\university\arabic sentiment analysis project\notebooks\fine_tuned_bert_mini_arabic'
    )

classifier = load_model()

# Initialize translator
@st.cache_resource
def load_translator():
    return GoogleTranslator(source='auto', target='ar')

translator = load_translator()

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select a page", ["Overview", "Predict Sentiment"])

# Overview page
if page == "Overview":
    st.header("Sentiment Distribution of 454 Elmenus Reviews")
    
# Filter reviews
    st.header("Reviews Data")
    rating_filter = st.selectbox("Filter by Rating", options=["All"] + sorted(df['rating'].unique().tolist()))
    sentiment_filter = st.selectbox("Filter by Sentiment", options=["All", "negative", "neutral", "positive"])
    
    filtered_df = df
    if rating_filter != "All":
        filtered_df = filtered_df[filtered_df['rating'] == int(rating_filter)]
    if sentiment_filter != "All":
        filtered_df = filtered_df[filtered_df['predicted_sentiment'] == sentiment_filter]
    
    st.dataframe(filtered_df[['text_translated', 'rating', 'predicted_sentiment']], use_container_width=True)

    # Download button
    st.subheader("Download Dataset")
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Reviews as CSV",
        data=csv,
        file_name="elmenus_reviews_filtered.csv",
        mime="text/csv"
    ) 
    
    # word cloud
    st.subheader("Word Cloud for Review Sentiments")
    sentiment_choice = st.selectbox("Select Sentiment for Word Cloud", ["positive", "neutral", "negative"])
    text = " ".join(df[df['predicted_sentiment'] == sentiment_choice]['text_translated'].dropna())
    if text:
        reshaped_text=arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        wordcloud = WordCloud(font_path=r"C:\Windows\Fonts\arial.ttf", width=800, height=400, background_color='white').generate(bidi_text)

        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.write("No text available for this sentiment.")
        
        # Bar chart
        sentiment_counts = df['predicted_sentiment'].value_counts()
        fig_bar = px.bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            labels={'x': 'Sentiment', 'y': 'Number of Reviews'},
            title='Sentiment Distribution (Bar)',
            color=sentiment_counts.index,
            color_discrete_map={'negative': '#FF6B6B', 'neutral': '#FFD93D', 'positive': '#6BCB77'}
        )

    

# Predict Sentiment page
elif page == "Predict Sentiment":
    st.header("Predict Sentiment for New Text")
    
    # Text input
    input_type = st.radio("Select input language:", ("Arabic", "English"))
    user_input = st.text_area(f"Enter {input_type} text for sentiment prediction:", height=150)
    
    if user_input:
        # Process input based on language
        if input_type == "English":
            processed_input = translator.translate(user_input)
            st.write(f"Translated to Arabic: {processed_input}")
        else:
            processed_input = user_input
        
        # Preprocess and predict
        processed_input = preprocess_arabic(processed_input)
        prediction = classifier(processed_input)[0]
        sentiment = prediction['label'].replace('LABEL_0', 'negative').replace('LABEL_1', 'neutral').replace('LABEL_2', 'positive')
        confidence = prediction['score']
        
        # Display result
        st.subheader("Prediction Result")
        st.write(f"**Sentiment**: {sentiment.capitalize()}")
        st.write(f"**Confidence**: {confidence:.2%}")
        
        # Color-coded result
        color = {'negative': '#FF6B6B', 'neutral': '#FFD93D', 'positive': '#6BCB77'}
        st.markdown(f"<h3 style='color: {color[sentiment]};'>The input text is predicted as {sentiment}.</h3>", unsafe_allow_html=True)


