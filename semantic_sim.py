import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import pandas as pd
from pathlib import Path

FAIL_THRESHOLD = 0.6

error_report = []

def calculate_similarity(text1: str, text2: str, embedding_model) -> float:
    """Calculate semantic similarity between two texts using FAISS."""
    # Convert dictionaries to strings for embedding comparison
    if isinstance(text1, dict):
        text1 = json.dumps(text1, sort_keys=True)
    if isinstance(text2, dict):
        text2 = json.dumps(text2, sort_keys=True)
        
    embedding1 = embedding_model.encode([text1])[0]
    embedding2 = embedding_model.encode([text2])[0]
    
    embedding1 = embedding1.reshape(1, -1)
    embedding2 = embedding2.reshape(1, -1)
    faiss.normalize_L2(embedding1)
    faiss.normalize_L2(embedding2)
    
    return float(np.dot(embedding1, embedding2.T)[0][0])

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')



def process_csv(file_path, num_of_outputs_to_test):
    try:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        df = pd.read_csv(file_path)
        
        # Verify required columns exist
        required_columns = ['human'] + [f'predicted_{i}' for i in range(num_of_outputs_to_test)]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Process each row
        for index, row in df.iterrows():
            print(f"\nRow {index + 1}:")
            print(f"Human: {row['human']}")
            print("Predictions:")
            for i in range(num_of_outputs_to_test):
                print(f"  {i}: {row[f'predicted_{i}']}")
                similarity = calculate_similarity(row['human'], row[f'predicted_{i}'], embedding_model)
                print(f"Similarity score: {similarity:.4f}")
                if similarity<FAIL_THRESHOLD:
                    error_report.append(f"Row number:{i}\nOriginal Text:{row['full']}\nHuman: {row['human']}\nMachine pass:{i}\nContent:{row[f'predicted_{i}']}")
            print("-" * 50)
                
    except pd.errors.EmptyDataError:
        print("The CSV file is empty")
    except Exception as e:
        print(f"An error occurred: {e}")


process_csv("my_output.csv", 5)

if error_report:
    print("ERROR REPORT:")
    for error in error_report:
        print(error)



# Example Files - Super Simple test to see if Semantic Similarity pipeline is actualy working

# text1 = """
# The sun was setting on the horizon, painting the sky in brilliant hues of orange and pink. 
# Birds were returning to their nests, creating a symphony of chirping sounds.
# The cool evening breeze rustled through the trees.
# """

# text2 = """
# As dusk approached, the sky was filled with orange and pink colors.
# The birds were flying back home, filling the air with their songs.
# A gentle wind moved through the leaves of the trees.
# """

# similarity = calculate_similarity(text1, text2, embedding_model)
# print(f"Similarity score: {similarity:.4f}")