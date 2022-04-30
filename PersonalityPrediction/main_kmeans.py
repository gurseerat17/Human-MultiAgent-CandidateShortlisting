import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

personalities = ('extroversion', 'neurotic', 'agreeable', 'conscientious', 'open')
def kmeans_fit():
    data_raw = pd.read_csv('data-final.csv', sep='\t')
    data = data_raw.copy()
    pd.options.display.max_columns = 150

    data.drop(data.columns[50:107], axis=1, inplace=True)
    data.drop(data.columns[51:], axis=1, inplace=True)

    print('Number of participants: ', len(data))
    data.head()
    data.dropna(inplace=True)

    df = data.drop('country', axis=1)
    columns = list(df.columns)

    scaler = MinMaxScaler(feature_range=(0,1))
    df = scaler.fit_transform(df)
    df = pd.DataFrame(df, columns=columns)
    df_sample = df[:5000]


    kmeans = KMeans()


    # I use the unscaled data but without the country column
    df_model = data.drop('country', axis=1)

    # I define 5 clusters and fit my model
    kmeans = KMeans(n_clusters=5)
    k_fit = kmeans.fit(df_model)

    pd.options.display.max_columns = 10
    predictions = k_fit.labels_
    df_model['Clusters'] = predictions
    df_model.head()
    return k_fit

def prediction_result(k_fit, personality_values):

    my_data = pd.read_csv('personality-tests.csv', sep='\t')

    openness = personality_values[0] 
    neuroticism = personality_values[1]
    conscientiousness = personality_values[2]
    agreeableness = personality_values[3]
    extraversion = personality_values[4]

    col_list = list(my_data)
    ext = col_list[0:10]
    est = col_list[10:20]
    agr = col_list[20:30]
    csn = col_list[30:40]
    opn = col_list[40:50]


    for idx in range(10):
        my_data[ext[idx]]=extraversion
        my_data[est[idx]]=neuroticism
        my_data[agr[idx]]=agreeableness
        my_data[csn[idx]]=conscientiousness
        my_data[opn[idx]]=openness

    my_personality = k_fit.predict(my_data)
    print('My Personality Cluster: ', my_personality)

    my_sums = pd.DataFrame()
    my_sums['extroversion'] = my_data[ext].sum(axis=1)/10
    my_sums['neurotic'] = my_data[est].sum(axis=1)/10
    my_sums['agreeable'] = my_data[agr].sum(axis=1)/10
    my_sums['conscientious'] = my_data[csn].sum(axis=1)/10
    my_sums['open'] = my_data[opn].sum(axis=1)/10
    my_sums['cluster'] = my_personality
    # print('Sum of my question groups')
    # my_sums

    my_sum = my_sums.drop('cluster', axis=1)
    plt.bar(my_sum.columns, my_sum.iloc[0,:], color='green', alpha=0.2)
    plt.plot(my_sum.columns, my_sum.iloc[0,:], color='red')
    plt.title('Cluster 2')
    plt.xticks(rotation=45)
    plt.ylim(0,4);
    return my_personality

if __name__ == "__main__":
    kfit = kmeans_fit()
    prediction_result(kfit, (9,0,8,7,5))