from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
s="Mohit is very good boy"
score = analyzer.polarity_scores(s)
print (score)