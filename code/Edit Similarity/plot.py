import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns  # Import seaborn for heatmap

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the JSON data
with open("all_changes.json", "r", encoding='utf-8') as f:
    all_changes = json.load(f)

# Preprocess the text data
def preprocess_changes(changes):
    added_text = ' '.join(' '.join(change['added']).strip() for change in changes if 'added' in change and ''.join(change['added']).strip())
    removed_text = ' '.join(' '.join(change['removed']).strip() for change in changes if 'removed' in change and ''.join(change['removed']).strip())
    return added_text + ' ' + removed_text

# Iterate over each interval
for interval, changes in all_changes.items():
    texts = {person: preprocess_changes(changes) for person, changes in changes.items()}

    # Convert the dictionary to a list of texts
    documents = list(texts.values())
    names = list(texts.keys())

    # Vectorize the text using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Calculate cosine similarity
    cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Create a DataFrame for better visualization
    cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=names, columns=names)
    print(cosine_sim_df)
    
    # Save the similarity matrix to a CSV file
    interval_str = f"{interval.replace(':', '').replace('T', '_')}"
    cosine_sim_df.to_csv(f"cosine_similarity_matrix_{interval_str}.csv", encoding='utf-8')
    
    # Plot heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(cosine_sim_df, annot=True, fmt=".2f", cmap="Reds", xticklabels=names, yticklabels=names)
    plt.title(f"Similarity Matrix of Politician Edits Between {interval[:10]} and {interval[21:31]}")
    plt.tight_layout()  # Adjust layout to ensure all labels are visible
    plt.show()

    # Create a NetworkX graph
    G = nx.Graph()

    # Add nodes
    for name in names:
        G.add_node(name)

    # Add edges with weights (similarities)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if cosine_sim_df.iloc[i, j] >= 0.15:  # Add only edges with positive similarity
                G.add_edge(names[i], names[j], weight=cosine_sim_df.iloc[i, j])

    # Draw the network
    pos = nx.spring_layout(G, seed=42)  # positions for all nodes

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # Draw edges with weights as labels
    edges = nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f'{d["weight"]:.2f}' for u, v, d in G.edges(data=True)})

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")

    plt.title(f"Similarity Network of Wikipedia Page Changes ({interval})")
    plt.axis("off")
    plt.show()

    # Export to GraphML
    nx.write_graphml(G, f"similarity_network_{interval_str}.graphml")

    # Optionally, export to GEXF (Gephi's native format)
    nx.write_gexf(G, f"similarity_network_{interval_str}.gexf")
