#importing required packages/lib

import pandas as pd
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import sys
sys.path.append('/hushHushRecruiter/data/database/databaseConnection') 
from data.database.databaseConnection import engine





# Fetching data from the database instead of CSV
data = pd.read_sql("SELECT * FROM processed_data", engine)
data.columns
data.dtypes

 #checking for null/nan values
nan_values = data.isna().sum()
nan_values[nan_values > 0]


#cleaning badges data points and creating new feature as 'total_badges'
data['Bronze Badges'] = data['Bronze Badges'].str.replace(',', '').astype(float)
data['Bronze Badges'] = data['Bronze Badges'].fillna(0)
bronze = data['Bronze Badges']
golden = data['Gold Badges']
silver = data['Silver Badges'].str.replace(',', '').astype(float)
data['total_badges'] = golden + silver + bronze


#converting 'reputation' and 'reached' columns to numeric
data['reputation'] = data['Reputation'].str.replace(',', '').astype(float)
def clean_reached(value):
    if 'k' in value:
        return float(value.replace('k', '')) * 1000
    elif 'm' in value:
        return float(value.replace('m', '')) * 1000000
    else:
        return float(value)
data['reached'] = data['Reached'].apply(clean_reached)
data['membership_period'] = data['Membership Period']

#creating new feature as 'total_skills'
skill_columns = ['Python Developer','C Developer', 'C++ Developer', 'Java Developer', 'C# Developer','JavaScript Developer', 'SQL Developer', 'R Developer', 'Data Engineer','Data Scientist', 'Artificial Intelligence Specialist','Machine Learning Expert']
data['total_skills'] = data[skill_columns].sum(axis=1)

#creating new feature as 'skills_ratio'
data['skills_ratio'] = data['total_skills'] / data['membership_period']

max_skills_ratio = data[data['skills_ratio'] != float('inf')]['skills_ratio'].max()
data['skills_ratio'].replace(float('inf'), max_skills_ratio, inplace=True)


#droping unecessary columns
data = data.drop(['Membership Period', 'Job Title', 'Reputation',
       'Reached', 'Answers', 'Questions', 'Gold Badges', 'Silver Badges',
       'Bronze Badges', 'Number of Tags', 'User Tags', 'Python Developer',
       'C Developer', 'C++ Developer', 'Java Developer', 'C# Developer',
       'JavaScript Developer', 'SQL Developer', 'R Developer', 'Data Engineer',
       'Data Scientist', 'Artificial Intelligence Specialist',
       'Machine Learning Expert'],axis=1)
#checking for null/nan values
nan_values = data.isnull().sum()
nan_values[nan_values > 0]

data.columns

#standardizing the data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
columns_to_scale = ['total_badges', 'reputation', 'reached']
df = data[columns_to_scale]
scaled_data = scaler.fit_transform(df)

data[columns_to_scale] = scaled_data

#creating new feature as 'badge_to_reputation_ratio'
data['badge_to_reputation_ratio'] = data['total_badges'] / data['reputation']

#creating new feature as 'badge_per_membership_period'
data['badge_per_membership_period'] = data['total_badges']/data['membership_period']

data

#creating a subset of data to perform clustering algorithm
columns_to_cluster = ['total_badges', 'reputation', 'reached']
cluster_dataset = data[columns_to_cluster]
cluster_dataset

#finding the ideak cluster value k using elbow method
sse = []
k_rng = range(1,15)
for k in k_rng:
    K_means = KMeans(n_clusters=k)
    K_means.fit_predict(cluster_dataset)
    sse.append(K_means.inertia_)
plt.xlabel('K')
plt.ylabel('Sum of squared error')
plt.plot(k_rng,sse)

#the plot displays k ==5 (need to generalise this step)
K_means = KMeans(n_clusters = 5)
K_means
data_p = K_means.fit_predict(cluster_dataset)
data_p
data['cluster'] = data_p
data

data.cluster.unique()

#checking the number of records under each cluster
cluster_counts = data['cluster'].value_counts()
cluster_counts

clusters_above_threshold = cluster_counts[cluster_counts > 100].index
clusters_above_threshold

#seleting the best cluster based on high mean values for 'reputation' and 'total_badges' features
cluster_scores = {}
for cluster in clusters_above_threshold:
    cluster_data = data[data['cluster'] == cluster]
    combined_score = cluster_data['reputation'].mean() + cluster_data['total_badges'].mean()
    cluster_scores[cluster] = combined_score
cluster_scores

best_cluster = max(cluster_scores, key=cluster_scores.get)

best_cluster, cluster_scores[best_cluster]


best_cluster_data = data[data.cluster == best_cluster]
best_cluster_data

#clustering the best_cluster_data again based on different membership period
membership_data = best_cluster_data['membership_period'].values.reshape(-1, 1)
membership_data


sse = []
k_rng = range(1,10)
for k in k_rng:
    K_means_new_cluster = KMeans(n_clusters=k)
    K_means_new_cluster.fit_predict(membership_data)
    sse.append(K_means_new_cluster.inertia_)
plt.xlabel('K')
plt.ylabel('Sum of squared error')
plt.plot(k_rng,sse)

#the plot displays k ==3 (need to generalise this step, by def a function that takes a data farme performs sse plot and gets the ideal cluster value)
K_means_new_cluster = KMeans(n_clusters=3)
membership_clusters = K_means_new_cluster.fit_predict(membership_data)
membership_clusters

best_cluster_data['membership_clusters'] = membership_clusters

best_cluster_statistics_data = best_cluster_data.drop(['Name', 'sequential_id'],axis=1)
best_cluster_statistics = best_cluster_statistics_data.groupby('membership_clusters').mean()

best_cluster_statistics.membership_period

cluster_means = {}
for index, value in enumerate(best_cluster_statistics.membership_period):
    cluster_means[index] = value
    
#sorting the clusters based on these mean values
sorted_clusters = sorted(cluster_means, key=cluster_means.get)

#assigning labels in ascending order
label_mapping = {cluster: i for i, cluster in enumerate(sorted_clusters)}
label_mapping

#labeling the clusters
best_cluster_data['membership_clusters_ordered'] = best_cluster_data['membership_clusters'].map(label_mapping)

best_cluster_data

new_label_mapping = {
    0: "New member",
    1: "Mid-Tenure Members",
    2: "Veteran Members"}

#replacing the numeric labels with the desired string labels
best_cluster_data['membership_clusters_ordered'] = best_cluster_data['membership_clusters_ordered'].map(new_label_mapping)
best_cluster_data

#exporting top 10 records from each label
def get_best_cluster_users(df, column_name, count=10):
    
    top_records = df.groupby(column_name).apply(
        lambda x: x.nlargest(count, ['reputation', 'total_badges'])
    ).reset_index(drop=True)
    
    return top_records[['sequential_id', 'Name','membership_clusters_ordered']]

#need to save this to the database
best_cluster_users = get_best_cluster_users(best_cluster_data, 'membership_clusters_ordered', 10)