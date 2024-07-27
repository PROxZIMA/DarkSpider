import time

tstart = time.time()
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from keras.layers import Input, Dense
from keras.models import Model
import re
import contractions

import umap
import hdbscan

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # Remove url from the scraped data
    text = re.sub(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w]*', '', text)
    text = re.sub(r'www\.[^\s]+', '', text)
    # Removing tags from the scraped data
    text = re.sub(r'<[^>]*>', '', text)    
    # Remove non-alphabetic characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    # Expand contractions
    text = contractions.fix(text)
    # Remove stop words
    words = word_tokenize(text)
    filtered_words = [word for word in words if word not in stop_words]
    # Perform lemmatization
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    # Remove punctuation
    lemmatized_words = [word for word in lemmatized_words if word.isalpha()]
    # Return a long string
    return ' '.join(lemmatized_words[:100])

def vectorize_unigram(text):
    # Initialize CountVectorizer and TfidfVectorizer objects
    count_vectorizer = CountVectorizer()
    tfidf_vectorizer = TfidfVectorizer()
    # Create count matrix and TF-IDF matrix
    count_matrix = count_vectorizer.fit_transform(text)
    tfidf_matrix = tfidf_vectorizer.fit_transform(text)
    # Get feature names (unigrams) from CountVectorizer and TfidfVectorizer
    count_feature_names = count_vectorizer.get_feature_names_out()
    tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()
    # Convert count matrix and TF-IDF matrix to DataFrames
    count_df = pd.DataFrame(count_matrix.toarray(), columns=count_feature_names)
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_feature_names)
    tfidf_df = tfidf_df.round(3) * 1000
    tfidf_df = tfidf_df.astype(int)
    # Get top 3 most frequent unigrams from CountVectorizer
    top3_count = count_df.apply(lambda x: x.nlargest(3).index.tolist(), axis=1)
    # Create new columns in the TF-IDF DataFrame for the top 3 unigrams from CountVectorizer
    tfidf_df['Top Unigram 1'] = [t[0] for t in top3_count]
    tfidf_df['Top Unigram 2'] = [t[1] if len(t) > 1 else '' for t in top3_count]
    tfidf_df['Top Unigram 3'] = [t[2] if len(t) > 2 else '' for t in top3_count]

    return tfidf_df

def get_autoencoder (dims, act='relu'): 
    n_stacks = len (dims) - 1 
    x = Input(shape=(dims[0],), name='input')
    
    h = x
    for i in range(n_stacks - 1):
        h = Dense(dims[i+1], activation=act, name='encoder_%d' %i)(h)
        
    h = Dense(dims [-1], name='encoder_%d' %(n_stacks - 1)) (h) 
    for i in range(n_stacks-1, 0, -1):
        h = Dense(dims[i], activation=act, name='decoder_%d' %i) (h)
    
    h = Dense(dims[0], name='decoder_0')(h)

    model = Model(inputs=x, outputs=h)
    model.summary()
    return model

def learn_manifold(x_data, umap_min_dist=0.00, umap_metric='euclidean', umap_dim=10, umap_neighbors=40):
    md = float(umap_min_dist)
    return umap.UMAP(random_state=0,
                 metric = umap_metric,
                 n_components = umap_dim, 
                 n_neighbors = umap_neighbors, 
                 min_dist = md).fit_transform(x_data)


def vectorize_unigram_text(text):
    count_vectorizer = CountVectorizer()
    count_matrix = count_vectorizer.fit_transform([text])

    count_feature_names = count_vectorizer.get_feature_names_out()
    count_df = pd.DataFrame(count_matrix.toarray(), columns=count_feature_names)

    top3_count = count_df.apply(lambda x: x.nlargest(3).index.tolist(), axis=1)
    count_df['Top Unigram 1'] = [t[0] for t in top3_count]
    count_df['Top Unigram 2'] = [t[1] if len(t) > 1 else '' for t in top3_count]
    count_df['Top Unigram 3'] = [t[2] if len(t) > 2 else '' for t in top3_count]
    count_df.drop(columns=count_feature_names, inplace=True)

    return count_df['Top Unigram 1'], count_df['Top Unigram 2'], count_df['Top Unigram 3']



# Process whole documents
start = time.time()
data_read = pd.read_csv("dataset_3.csv") # --TODO: Add path to your dataset here
data_read.rename(columns={'url': 'URL'}, inplace=True)
end = time.time()
print("Data loaded", end - start)

start = time.time()
data_read.dropna(inplace=True, axis=0)
data_read.drop_duplicates(inplace=True)
data_read.reset_index(drop=True, inplace=True)
end = time.time()
print("Data cleaned", end - start)

start = time.time()
data_read['preprocessed'] = data_read['scrape_data'].apply(preprocess_text)
end = time.time()
print("Data preprocessed", end - start)

start = time.time()
data_vect = vectorize_unigram(data_read['preprocessed'])
data_vect.insert(0, 'URL', data_read['URL'])
# data2.to_csv('vectorized.csv', index=False)
end = time.time()
print("Data vectorized", end - start)

## Clusterizing

# autoencoding
start = time.time()
X = data_vect.copy()
X_scaled = X.iloc[:,1:-3]
X_scaled = X_scaled.values
end = time.time()
print('Data ready for encoding', end - start)

start = time.time()
encoded_dimensions = 10
shape = [len(X_scaled[0]), 512,1024, 2048, encoded_dimensions]
autoencoder = get_autoencoder(shape) 

encoded_layer = f'encoder_{(len(shape) - 2)}'
hidden_encoder_layer = autoencoder.get_layer(name=encoded_layer).output
encoder = Model(inputs=autoencoder.input, outputs=hidden_encoder_layer)

autoencoder.compile(loss='mse', optimizer='adam')
end = time.time()
print('Encoder ready for training', end - start)

start = time.time()
if X_scaled.shape[0] > 5000:
    autoencoder.fit(
        X_scaled[:5000].astype('float32'),
        X_scaled[:5000],
        batch_size=64,
        epochs=5,
        verbose=1,
    )
else:
    autoencoder.fit(
        X_scaled.astype('float32'),
        X_scaled,
        batch_size=64,
        epochs=5,
        verbose=1,
    )

batch_size = 1024
X_encoded = []
num_samples = X_scaled.shape[0]

for i in range(0, num_samples, batch_size):
    batch = X_scaled[i:i+batch_size]
    encoded_batch = encoder.predict(batch)
    X_encoded.append(encoded_batch)

X_encoded = np.concatenate(X_encoded, axis=0)
end = time.time()
print('Data encoded', end - start)

# Manifold learning
start = time.time()
X_reduced = learn_manifold(X_encoded, umap_neighbors=30, umap_dim=int(encoded_dimensions/2))
end = time.time()
print('Data ready for clustering', end - start)

# Hierarchical Density Based Spartial Clustering of Applications with Noise 
start = time.time()
labels = hdbscan.HDBSCAN(
    min_samples=100,
    min_cluster_size=25
).fit_predict(X_reduced)
end = time.time()
print('Data clustered', end - start)

# Labelling
start = time.time()
data_clust = pd.DataFrame(columns=['URL', 'Cluster'], data=np.column_stack((X['URL'], labels)))

data_top = data_vect[['URL', 'Top Unigram 1', 'Top Unigram 2', 'Top Unigram 3']]
data_clust = pd.merge(data_clust, data_top, on='URL', how='left')
data_clust = pd.merge(data_clust, data_read, on='URL', how='left')

data_clust['label_1'] = 'micellaneous'
data_clust['label_2'] = 'micellaneous'
data_clust['label_3'] = 'micellaneous'

for i in data_clust.Cluster.unique():
    text = ' '.join(data_clust[data_clust['Cluster']==i]['preprocessed'].values)
    
    if i != -1:
        a, b, c = vectorize_unigram_text(text)
        data_clust.loc[data_clust['Cluster']==i, 'label_1'] = a.iloc[0]
        data_clust.loc[data_clust['Cluster']==i, 'label_2'] = b.iloc[0]
        data_clust.loc[data_clust['Cluster']==i, 'label_3'] = c.iloc[0]

data_clust.drop(columns=['Cluster','preprocessed'], axis=1, inplace=True)
data_clust.to_csv('clusterized.csv', index=False)
end = time.time()
print('Data labeled', end - start)

tend = time.time()
print("\n\nTOTAL TIME: ", tend - tstart)
