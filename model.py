

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

df=pd.read_csv('/content/final-dataset.csv')

df.head()

missing_values = df.isna().sum()

print("Missing Values:")
print(missing_values)

carcinogenic = df['label'].value_counts().get(1)
non_carcinogenic = df['label'].value_counts().get(0)

print("Number of Oncogenic Compounds:", carcinogenic)
print("Number of Non-Oncogenic Compounds:", non_carcinogenic)

plt.figure(figsize=(8, 6))
df['label'].value_counts().plot(kind='bar')
plt.title('Distribution of Oncogenic and Non-Oncogenic Compounds')
plt.xlabel('label')
plt.ylabel('Count')
plt.show()

from sklearn.utils import resample

carcinogenic_data = df[df['label'] == 1]
non_carcinogenic_data = df[df['label'] == 0]

carcinogenic_upsampled = resample(
    carcinogenic_data,
    replace=True,
    n_samples=len(non_carcinogenic_data),
    random_state=42
)

balanced_data = pd.concat([carcinogenic_upsampled, non_carcinogenic_data])

balanced_data = balanced_data.sample(frac=1, random_state=42)

print("Balanced Data:")
print(balanced_data['label'].value_counts())

X = balanced_data.drop('label', axis=1)
Y = balanced_data['label']
print(X)

print(Y)

pip install rdkit-pypi

from rdkit import Chem
from rdkit.Chem import Descriptors

# Function to generate molecular descriptors
def generate_descriptors(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:  # To handle invalid SMILES
        return None
    descriptors = {
        'MolecularWeight': Descriptors.MolWt(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'TPSA': Descriptors.TPSA(mol),  # Topological polar surface area
        'LogP': Descriptors.MolLogP(mol)  # LogP (lipophilicity)
    }
    return descriptors

# Apply the function to each row in the dataset
df['descriptors'] = df['SMILES'].apply(generate_descriptors)

# Drop rows where SMILES were invalid and descriptors are None
df = df.dropna(subset=['descriptors'])

# Convert the descriptors to separate columns
descriptors_df = pd.DataFrame(df['descriptors'].tolist())
df = pd.concat([df, descriptors_df], axis=1)
df = df.drop(columns=['descriptors'])

print(df.head())

print(df)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import RandomOverSampler
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import roc_auc_score

# Define X (features) and y (labels)
X = df[['MolecularWeight', 'NumHDonors', 'NumHAcceptors', 'TPSA', 'LogP']]
y = df['label']
X=X.dropna()
y=y.dropna()
ros = RandomOverSampler(random_state=42)
X_res, y_res = ros.fit_resample(X, y)

print(pd.Series(y_res).value_counts())


X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

rf_classifier.fit(X_train, y_train)

y_pred = rf_classifier.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

print(classification_report(y_test, y_pred))


y_probs = rf_classifier.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_probs)
print(f"roc_auc: {roc_auc}")

from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc

precision, recall, thresholds = precision_recall_curve(y_test, y_probs)
pr_auc = auc(recall, precision)

plt.figure(figsize=(8, 6))
plt.plot(recall, precision, label='Precision-Recall curve (AUC = %0.2f)' % pr_auc)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc='lower left')
plt.show()

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import RandomOverSampler
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt

from sklearn.metrics import roc_curve

# Calculate ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_probs)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc='lower right')
plt.show()

# prompt: genereate a correlation matrix for random forest

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Assuming X and y are already defined as in your previous code
# ... (Your existing code to define X and y) ...


# Assuming X and y are already defined from your previous code
X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train, y_train)

# Feature importances from the trained RandomForestClassifier
importances = rf_classifier.feature_importances_

# Create a DataFrame for better visualization
feature_importances = pd.DataFrame({'feature': X_train.columns, 'importance': importances})
feature_importances = feature_importances.sort_values(by='importance', ascending=False)

# Calculate the correlation matrix
correlation_matrix = X_train.corr()


# Plot the correlation matrix as a heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Features')
plt.show()

from sklearn.metrics import confusion_matrix
import seaborn as sns

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=['Predicted 0', 'Predicted 1'],
            yticklabels=['Actual 0', 'Actual 1'])
plt.title("Confusion Matrix for Random Forest Classifier")
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.show()

import pickle
filename = 'oncogenic_model.pkl'
pickle.dump(rf_classifier, open(filename, 'wb'))

print(f"Model saved to {filename}")

!pip install pytesseract

import pytesseract
from PIL import Image

# Load your image
image = Image.open('/content/image.png')

# Perform OCR
text = pytesseract.image_to_string(image)
text_lines = text.split('\n')
single_elements = [item.strip() for sublist in text_lines for item in sublist.split(',')]

# Remove any empty strings or unwanted characters
single_elements = [item.lower() for item in single_elements if item]
single_elements.remove(single_elements[0])
print(single_elements)

from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc

precision, recall, thresholds = precision_recall_curve(y_test, y_probs)
pr_auc = auc(recall, precision)

plt.figure(figsize=(8, 6))
plt.plot(recall, precision, label='Precision-Recall curve (AUC = %0.2f)' % pr_auc)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc='lower left')
plt.show()

from sklearn.tree import DecisionTreeClassifier

dt_classifier = DecisionTreeClassifier(random_state=42)

dt_classifier.fit(X_train, y_train)

y_pred = dt_classifier.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

print(classification_report(y_test, y_pred))

from sklearn.ensemble import BaggingClassifier
from sklearn.metrics import roc_auc_score

bagging_classifier = BaggingClassifier(estimator=RandomForestClassifier(random_state=42),
                                      n_estimators=100,
                                       random_state=42)


bagging_classifier.fit(X_train, y_train)

y_pred = bagging_classifier.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")
print(classification_report(y_test, y_pred))

y_probs = bagging_classifier.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_probs)
print(f"ROC-AUC score {roc_auc}")

from sklearn.metrics import confusion_matrix
import seaborn as sns

# Generate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Create a heatmap for the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Non-Carcinogenic', 'Carcinogenic'],
            yticklabels=['Non-Carcinogenic', 'Carcinogenic'])
plt.title('Confusion Matrix for Bagging Classifier')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()

!pip install pubchempy

import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Descriptors
import pandas as pd

def get_smiles_from_name(chemical_name):
    try:
        compound = pcp.get_compounds(chemical_name, 'name')
        if compound:
            return compound[0].canonical_smiles
        else:
            raise ValueError(f"No SMILES found for: {chemical_name}")
    except Exception as e:
        print(f"Error retrieving SMILES for {chemical_name}: {e}")
        return None

def compute_descriptors(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    descriptors = {
        'MolecularWeight': Descriptors.MolWt(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'TPSA': Descriptors.TPSA(mol),
        'LogP': Descriptors.MolLogP(mol)
    }
    return pd.DataFrame([descriptors])

new_chemical_names = ['Kaolin', 'Bentonite', 'Glycerin','Cetostearyl Alcohol', 'Iso Propyl Myristate',
'Glycerol Monostearate', 'Cetyl Alcohol']

new_data_smiles = [get_smiles_from_name(name) for name in new_chemical_names]

new_data_smiles = [smiles for smiles in new_data_smiles if smiles is not None]

new_data_features = pd.concat([compute_descriptors(smiles) for smiles in new_data_smiles], ignore_index=True)

new_predictions = rf_classifier.predict(new_data_features)

for name, pred in zip(new_chemical_names, new_predictions):
    print(f"Chemical: {name}, Predicted Oncogenicity: {'Oncogenic' if pred == 1 else 'Non-oncogenic'}")

svm_classifier = SVC(kernel='linear', probability=True, random_state=42)

svm_classifier.fit(X_train, y_train)

y_pred = svm_classifier.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

# Evaluate the model
print(classification_report(y_test, y_pred))

y_probs = svm_classifier.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_probs)

print(f"ROC AUC Score: {roc_auc}")

from xgboost import XGBClassifier

# Create an XGBoost classifier
xgb_classifier = XGBClassifier(random_state=42)

# Train the XGBoost classifier
xgb_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = xgb_classifier.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

# Evaluate the model
print(classification_report(y_test, y_pred))

y_probs = xgb_classifier.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_probs)

print(f"ROC AUC Score: {roc_auc}")

# Generate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Create a heatmap for the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Non-Carcinogenic', 'Carcinogenic'],
            yticklabels=['Non-Carcinogenic', 'Carcinogenic'])
plt.title('Confusion Matrix for XGBoost Classifier')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()
