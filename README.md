# Elmenus Sentiment Analysis

This project analyzes 454 restaurant reviews from the Elmenus app to classify sentiments (positive, negative, neutral) using a fine-tuned `asafaya/bert-mini-arabic` model (71% accuracy, 0.65 F1-score). It includes a Streamlit app for interactive visualization and real-time predictions.

## Project Overview
- **Data**: Scraped 454 reviews with text, ratings, and timestamps.
- **Preprocessing**: Normalized Arabic text with `camel-tools` and translated mixed-language reviews to Arabic using `deep-translator`.
- **Model**: Fine-tuned BERT-Mini-Arabic with class weights to address imbalance (255 negative, 121 positive, 78 neutral).
- **Streamlit App**: Features bar/pie charts, word clouds, confidence scores, rating/sentiment filters, CSV download, and real-time Arabic/English predictions.
