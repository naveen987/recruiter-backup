import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def get_best_cluster_users():
    # Load the dataset
    data_path = 'stack.csv'
    data = pd.read_csv(data_path)

    # Convert the 'Reputation' column to numeric format
    data['Reputation'] = data['Reputation'].str.replace(',', '').astype(int)

    # Extract the columns related to job profiles
    job_profile_columns = data.columns[11:-1]

    # Create a subset with relevant columns for clustering
    data_subset = data[['Membership Period', 'Reputation'] + list(job_profile_columns)]
    data_subset = data_subset.drop(columns=['Number of Tags', 'User Tags'])

    # Scale the data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_subset)

    # K-means clustering
    optimal_clusters = 4
    kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
    data['cluster_group'] = kmeans.fit_predict(data_scaled)

    # Identify the cluster with the highest average reputation
    best_cluster = data.groupby('cluster_group')['Reputation'].mean().idxmax()

    # Extract users from the best cluster and sort them by reputation in descending order
    best_cluster_users = data[data['cluster_group'] == best_cluster][['sequential_id', 'Name', 'Reputation']]
    best_cluster_users = best_cluster_users.sort_values(by='Reputation', ascending=False)
    
    return best_cluster_users
