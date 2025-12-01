# import pandas as pd
# from sklearn.tree import DecisionTreeClassifier
# import pickle
# import io
# import os

# def train_remedy_model():
#     """
#     This script is now upgraded to be more robust. It intelligently handles
#     different column names and converts text-based symptoms into a numerical
#     format using One-Hot Encoding before training.
#     """
    
#     dataset_filename = 'remedy_dataset.csv'

#     # --- 1. Load the Dataset from a CSV file ---
#     if not os.path.exists(dataset_filename):
#         print(f"'{dataset_filename}' not found. Creating a sample dataset for demonstration.")
#         csv_data = """Symptom_1,Symptom_2,Symptom_3,Remedy
# itching,skin_rash,nodal_skin_eruptions,Neem Bath
# shivering,chills,vomiting,Hydration and Rest
# fatigue,lethargy,headache,Rest and Hydration
# """
#         with open(dataset_filename, 'w') as f:
#             f.write(csv_data)
    
#     df = pd.read_csv(dataset_filename).dropna(axis=1) # Load data and drop any empty columns
#     print("--- Training on data loaded from 'remedy_dataset.csv' ---")
#     print(df.head())

#     # --- 2. Data Preparation (Upgraded with One-Hot Encoding) ---
    
#     # Define the column we want to predict. 
#     # **IMPORTANT**: This has been updated to match your new dataset.
#     target_column = 'Home Remedy' 

#     if target_column not in df.columns:
#         print(f"\nERROR: The target column '{target_column}' was not found in your CSV file.")
#         print(f"Please update the 'target_column' variable in this script to match your dataset.")
#         return

#     # Separate the features (symptoms) from the target (remedy)
#     X = df.drop(columns=[target_column])
#     y = df[target_column]

#     # --- THIS IS THE FIX: Convert all text symptoms into a numerical format ---
#     # `pd.get_dummies` performs one-hot encoding on our symptom columns.
#     X_encoded = pd.get_dummies(X)
#     print("\n--- Symptoms have been converted to a numerical format. ---")
    
#     # --- 3. Model Training ---
#     # We train the model on the new, numerically encoded data.
#     model = DecisionTreeClassifier(random_state=42)
#     model.fit(X_encoded, y)
#     print(f"\n--- Home Remedy Prediction Model has been trained successfully! ---")

#     # --- 4. Save the Model and the Encoded Columns ---
#     with open('remedy_model.pkl', 'wb') as f:
#         pickle.dump(model, f)
#     print("... Trained model saved to 'remedy_model.pkl'")

#     # Save the list of columns from the *encoded* data, which the model now expects.
#     model_columns = list(X_encoded.columns)
#     with open('remedy_columns.pkl', 'wb') as f:
#         pickle.dump(model_columns, f)
#     print("... Encoded model columns saved to 'remedy_columns.pkl'")


# # --- Run the new training process ---
# if __name__ == '__main__':
#     train_remedy_model()







































































import pandas as pd
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle

def train_final_model():
    """
    Train model using FreedomIntelligence/Disease_Database from Hugging Face.
    
    Uses:
    - 'common_symptom' as the symptom input text
    - 'disease' as the label
    - 'treatment' optionally stored but not used for classification
    """
    print("--- Starting the final model training process... ---")
    
    # --- 1. Load the dataset ---
    try:
        dataset = load_dataset("FreedomIntelligence/Disease_Database", "en", split="train")
        df = dataset.to_pandas()
        print("... Dataset downloaded and loaded successfully!")
        print("Columns available:", df.columns.tolist())    
        
    except Exception as e:
        print(f"ERROR: Could not download the dataset. Details: {e}")
        return
    
    # --- 2. Data preparation ---
    # Ensure these columns exist
    required_cols = ['common_symptom', 'disease', 'treatment']
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Expected column '{col}' not found in dataset. Available: {df.columns.tolist()}")
    
    # Select and drop missing
    df_clean = df[['common_symptom', 'disease', 'treatment']].dropna().reset_index(drop=True)
    
    # Rename for consistency
    df_clean = df_clean.rename(columns={
        'common_symptom': 'Symptoms',
        'disease': 'Disease',
        'treatment': 'Treatment'
    })
    
    print(f"... After cleaning, dataset has {len(df_clean)} records.")
    
    # Rename for consistency
   
    K = 100  # change this to 50, 200, etc. depending on your prototype
    top_diseases = df_clean['Disease'].value_counts().nlargest(K).index
    df_clean = df_clean[df_clean['Disease'].isin(top_diseases)].reset_index(drop=True)
    print(f"... Filtered dataset to Top-{K} diseases, now {len(df_clean)} records remain.")
    
    # --- 3. Feature / Label ---
    X = df_clean['Symptoms']
    y = df_clean['Disease']
    
    # --- 4. Vectorization ---
    vectorizer = TfidfVectorizer(max_features=1500, stop_words='english')
    X_vectorized = vectorizer.fit_transform(X)
    print("... Symptoms have been processed into a numerical format.")
    
    # --- 5. Model training ---
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vectorized, y)
    print("--- Final Disease Prediction Model has been trained successfully! ---")
    
    # --- 6. Save model, vectorizer, dataset lookup ---
    with open('final_disease_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("... Trained model saved to 'final_disease_model.pkl'")
    
    with open('final_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    print("... Symptom vectorizer saved to 'final_vectorizer.pkl'")
    
    df_clean.to_csv('final_remedy_dataset.csv', index=False)
    print("... Cleaned dataset saved to 'final_remedy_dataset.csv'")
    

if __name__ == '__main__':
    train_final_model()
