import string
import emoji
from analysis import app
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import GetOldTweets3 as got
import matplotlib.pyplot as plt
from io import BytesIO
from nltk.corpus import stopwords
from collections import Counter
from flask import Flask,request,render_template,url_for,flash
from flask_bootstrap import Bootstrap
import os

def get_tweets_bytopic(n,topic,date1,date2):
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(topic).setSince(date1).setUntil(date2).setMaxTweets(n)
    tweets = got.manager.TweetManager.getTweets(tweetCriteria)

    #To convert objects into text of tweets
    tweets = [[tweets.text] for tweets in tweets]
    return tweets

@app.route('/',methods=['GET','POST'])
def analysis():
    if request.method == 'POST':        
        form = request.form
        topic = form['topic']
        n = int(form['no'])
        date1 = form['from']
        date2 = form['to']
        msg = str(get_tweets_bytopic(n,topic,date1,date2))

        #To get text without punctuation and stopwords
        np = [c for c in msg if c not in string.punctuation]
        no_punc = ''.join(np)
        tokenized_no_punc = word_tokenize(no_punc,'english')
        final_mess = [word for word in tokenized_no_punc if word.lower() not in stopwords.words('english')]

        emotion_list =[]

        #For getting clean text(removing \n, \t, and ',')
        with open('emotions.txt','r') as f:
            for line in f:
                clear_line = line.replace('\n','').replace(',','').replace("'",'').replace("\t",'').strip()
                word, emotion = clear_line.split(':')
                
                if word in final_mess:
                    emotion_list.append(emotion)

        #To count the number of times emotion comes in the string
        emotion_count = Counter(emotion_list)

        #Sentiment Analysis
        score = SentimentIntensityAnalyzer().polarity_scores(msg)
        if score['neg'] > score['pos']:
            result = 'Negative \U0001f620'
        elif score['neg'] < score['pos']:
            result = 'Positive \U0001f604'
        else:
            result = 'Neutral \U0001F636'
            
        #bar plot for the emotions we got.
        fig,ax = plt.subplots()
        ax.bar(emotion_count.keys(),emotion_count.values(),color='midnightblue')
        fig.autofmt_xdate()
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.title("Sentiment Analysis on " + topic,fontsize=13,fontweight='bold')
        plt.xlabel("Emotions",fontsize=13)
        plt.ylabel("Proportion",fontsize=13)
        
        plt.savefig('analysis/static/graph.png')
        img = os.path.join('analysis/static', 'graph.png')
        return render_template('index.html',result=result)
    return render_template('index.html')
