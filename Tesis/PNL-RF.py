import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import re
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
#nltk.download('stopwords')
#nltk.download('punkt')

# Leer el archivo CSV
df = pd.read_csv('C:/Users/Hernán Ifrán/Downloads/resultados.csv', encoding='latin-1')  
# Obtener las columnas de diagnósticos y códigos AIS
descripciones = df['Description'].tolist()
codigos_AIS = df['Codigo_AIS'].tolist()

descripciones = [str(desc) for desc in descripciones]

# Codificar los códigos AIS como etiquetas numéricas
label_encoder = LabelEncoder()
codigos_AIS_numericos = label_encoder.fit_transform(codigos_AIS)

# Función para separar diagnósticos en una descripción
def separar_diagnosticos(descripcion):
    pattern = r'\s*\+\s*|\s+(?<!\w)\.\s+|\n'
   # pattern = r'\s*\+\s*|\s+(?<!\w)\.\s+|\s*,\s*|\n'
    return re.split(pattern, descripcion.strip())

# Función para realizar stemming en una descripción
stemmer = SnowballStemmer('spanish')
def stem_descripcion(descripcion):
    words = nltk.word_tokenize(descripcion)
    words = [stemmer.stem(word) for word in words if word not in stopwords.words('spanish')]
    return ' '.join(words)

# Aplicar stemming a las descripciones
descripciones_stemmed = [stem_descripcion(desc) for desc in descripciones]

# División de los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(descripciones_stemmed, codigos_AIS_numericos, test_size=0.15, random_state=42)

# Creación del pipeline para el clasificador basado en texto
pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', RandomForestClassifier(class_weight='balanced', n_estimators=100, max_depth=None, min_samples_split=2))  
])

# Entrenamiento del modelo
pipeline.fit(X_train, y_train)
# Guardar el modelo
modelo_path = 'C:/Users/Hernán Ifrán/Downloads/modelo_entrenado.joblib'
joblib.dump(pipeline, modelo_path)
print(f"El modelo se ha guardado correctamente en: {modelo_path}")
# Evaluación del modelo
y_pred = pipeline.predict(X_test)
report = classification_report(y_test, y_pred, zero_division=1)
print(report)

# Ejemplo de predicción para diagnósticos nuevos
archivo_diagnosticos = 'C:/Users/Hernán Ifrán/Downloads/pruebadiagnosticos.txt'
with open(archivo_diagnosticos, 'r',encoding='latin-1') as file:
    texto_diagnosticos = file.read()

diagnosticos = separar_diagnosticos(texto_diagnosticos)
for diagnostico in diagnosticos:
    diagnostico_stemmed = stem_descripcion(diagnostico.strip())
    predicciones = pipeline.predict([diagnostico_stemmed])
    clases_predichas = label_encoder.inverse_transform(predicciones)
    print('Descripción:', diagnostico.strip())
    print('Códigos AIS predichos:', clases_predichas)
    print('---')

# Guardar el LabelEncoder en la carpeta Downloads
label_encoder_path = 'C:/Users/Hernán Ifrán/Downloads/label_encoder.joblib'
joblib.dump(label_encoder, label_encoder_path)
print(f"El LabelEncoder se ha guardado correctamente en: {label_encoder_path}")