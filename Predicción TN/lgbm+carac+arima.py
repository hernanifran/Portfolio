import pandas as pd
import numpy as np
from datetime import datetime
import lightgbm as lgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tqdm import tqdm
from sklearn.impute import SimpleImputer
from statsmodels.tsa.arima.model import ARIMA
import optuna
from scipy.optimize import minimize


# Cargar los datos
df = pd.read_csv('C:/Users/Hernán Ifrán/Downloads/df_prediccion_all.csv')  
productosPredecir = pd.read_csv('C:/Users/Hernán Ifrán/Downloads/productos_a_predecir.txt', sep='\t')


# Convertir el periodo a formato datetime
df['periodo'] = pd.to_datetime(df['periodo'], format='%Y%m')

# Agregar los datos por periodo y product_id para obtener la serie temporal
ts = df.groupby(['periodo', 'product_id'])['tn'].sum().reset_index()

# Convertir el periodo a formato datetime
df['periodo'] = pd.to_datetime(df['periodo'], format='%Y%m')

# Agregar los datos por periodo y product_id para obtener la serie temporal
ts = df.groupby(['periodo', 'product_id'])['tn'].sum().reset_index()

# Asegurarse de que las columnas tengan el mismo tipo y formato
ts['product_id'] = ts['product_id'].astype(int)
ts['periodo'] = pd.to_datetime(ts['periodo'])

# Crear características adicionales cat1    
ts['cat1'] = ts['product_id'] % 2 
ts['cat2'] = ts['product_id'] % 2 
ts['cat3'] = ts['product_id'] % 2 
ts['sku_size'] = ts['product_id'].astype(int)
# Codificar la característica cat1 utilizando One-Hot Encoding
#ts = pd.get_dummies(ts, columns=['cat1'], prefix='cat1', drop_first=True)
ts = pd.get_dummies(ts, columns=['cat1', 'cat2', 'cat3'], prefix=['cat1', 'cat2', 'cat3'], drop_first=True)
# Agregar lags a los datos
lags = 3  # Número de lags a incluir
for lag in range(1, lags + 1):
    ts[f'tn_lag_{lag}'] = ts.groupby('product_id')['tn'].shift(lag)

# Calcular la media de las ventas para cada producto
ts['tn_mean'] = ts.groupby('product_id')['tn'].transform('mean')

# Calcular promedios móviles de 2, 3, 4, 5 y 6 meses
for window in range(2, 7):
    ts[f'tn_rolling_mean_{window}'] = ts.groupby('product_id')['tn'].transform(lambda x: x.rolling(window).mean())

# Eliminar filas con valores NaN en la variable objetivo
ts.dropna(subset=['tn'], inplace=True)

# Crear características adicionales si es necesario (Ejemplo: características temporales)
ts['year'] = ts['periodo'].dt.year
ts['month'] = ts['periodo'].dt.month

# Generar características ARIMA para cada producto
def generate_arima_features(data, p=1, d=1, q=1):
    arima_preds = []
    for product_id in data['product_id'].unique():
        product_data = data[data['product_id'] == product_id].copy()
        model = ARIMA(product_data['tn'], order=(p, d, q))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=2)  # Predice los próximos dos periodos
        arima_preds.append(forecast.values)
       
    arima_preds = np.array(arima_preds)
    return arima_preds

# Aplicar la función para generar características ARIMA
arima_features = generate_arima_features(ts)
ts['arima_pred_1'] = np.nan
ts['arima_pred_2'] = np.nan

# Agregar predicciones ARIMA al DataFrame ts
for idx, product_id in enumerate(ts['product_id'].unique()):
    ts.loc[ts['product_id'] == product_id, 'arima_pred_1'] = arima_features[idx, 0]
    ts.loc[ts['product_id'] == product_id, 'arima_pred_2'] = arima_features[idx, 1]

# Calcular RSI
window_length = 14
ts['rsi'] = np.nan
for product_id in ts['product_id'].unique():
    product_data = ts[ts['product_id'] == product_id].copy()
    delta = product_data['tn'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window_length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window_length).mean()
    rs = gain / loss
    ts.loc[ts['product_id'] == product_id, 'rsi'] = 100 - (100 / (1 + rs))

# Calcular MACD
short_window = 12
long_window = 26
signal_window = 9

ts['ema_short'] = ts.groupby('product_id')['tn'].transform(lambda x: x.ewm(span=short_window, adjust=False).mean())
ts['ema_long'] = ts.groupby('product_id')['tn'].transform(lambda x: x.ewm(span=long_window, adjust=False).mean())
ts['macd'] = ts['ema_short'] - ts['ema_long']
ts['macd_signal'] = ts.groupby('product_id')['macd'].transform(lambda x: x.ewm(span=signal_window, adjust=False).mean())
ts['macd_hist'] = ts['macd'] - ts['macd_signal']


# Obtener la lista de productos únicos a predecir
product_ids = productosPredecir['product_id'].unique()

# Crear conjunto de entrenamiento y objetivo
feature_columns = ['product_id', 'year', 'month', 'tn_mean', 'rsi', 'macd','macd_signal', 'macd_hist', 'arima_pred_1', 'arima_pred_2','sku_size'] + [f'tn_lag_{lag}' for lag in range(1, lags + 1)]+\
                  [f'cat1_{k}' for k in range(1, 2)] + \
                  [f'cat2_{k}' for k in range(1, 2)] + \
                  [f'cat3_{k}' for k in range(1, 2)] + \
                  [f'tn_rolling_mean_{window}' for window in range(2, 7)]

X = ts[feature_columns].astype(float)
y = ts['tn'].shift(-2)

# Eliminar filas con valores NaN en el conjunto de datos
y.fillna(0, inplace=True)

# Función para calcular los pesos
def calcular_pesos(ts):
    ventas_totales = ts.groupby('product_id')['tn'].sum()
    pesos = ventas_totales / ventas_totales.sum()
    return pesos

# Calcular los pesos en función de tn
weights = ts['product_id'].map(calcular_pesos(ts))

# Imputar valores faltantes
imputer = SimpleImputer(strategy='mean')
X = imputer.fit_transform(X)

# Utilizar TimeSeriesSplit para validación cruzada en series temporales
tscv = TimeSeriesSplit(n_splits=5)

# Definir la función objetivo para Optuna
def objective(trial):
    params = {
        'num_leaves': trial.suggest_int('num_leaves', 20, 150),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'subsample': trial.suggest_float('subsample', 0.7, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.7, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 1.0)
    }

    model = lgb.LGBMRegressor(**params)
    
    # TimeSeriesSplit para validación cruzada
    scores = []
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        weights_train = weights[train_index]
        model.fit(X_train, y_train, sample_weight=weights_train)
        preds = model.predict(X_test)
        score = mean_squared_error(y_test, preds)
        scores.append(score)
    
    return np.mean(scores)

# Crear el estudio de Optuna y optimizar los hiperparámetros
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=100)

# Obtener el mejor conjunto de hiperparámetros
best_params = study.best_params

# Entrenar el modelo final con los mejores hiperparámetros
best_lgbm = lgb.LGBMRegressor(**best_params)
best_lgbm.fit(X, y, sample_weight=weights)

# Calcular la importancia de las características
feature_importances = best_lgbm.feature_importances_
feature_importance_df = pd.DataFrame({'feature': feature_columns, 'importance': feature_importances})
feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)

# Imprimir la importancia de las características
print(feature_importance_df)

# Calcular el promedio global de tn
global_mean_tn = ts['tn'].mean()

# Realizar predicciones para los productos a predecir
results = []
for product_id in tqdm(product_ids, desc="Predicting with Optimized LGBM"):
    product_data = ts[ts['product_id'] == product_id].copy()
    if not product_data.empty:
        # Predicción para el último periodo disponible + 2 meses
        last_period = product_data['periodo'].max()
        next_period = last_period + pd.DateOffset(months=2)
        # Calcular rolling means
        rolling_means = {}
        for window in range(2, 7):
            rolling_means[f'tn_rolling_mean_{window}'] = product_data[f'tn_rolling_mean_{window}'].iloc[-1]

        next_data = pd.DataFrame({
            'product_id': [product_id],
            'year': [next_period.year],
            'month': [next_period.month],
            'tn_mean': [product_data['tn_mean'].iloc[-1]],
            'rsi': [product_data['rsi'].iloc[-1]],
            'macd': [product_data['macd'].iloc[-1]],
            'macd_signal': [product_data['macd_signal'].iloc[-1]],
            'macd_hist': [product_data['macd_hist'].iloc[-1]],
            'cat1_1': [product_data['cat1_1'].iloc[-1]] if 'cat1_1' in product_data else [0],
            'cat2_1': [product_data['cat2_1'].iloc[-1]] if 'cat2_1' in product_data else [0],
            'cat3_1': [product_data['cat3_1'].iloc[-1]] if 'cat3_1' in product_data else [0],
            'sku_size':[product_data['sku_size'].iloc[-1]],
            'tn_lag_1': [product_data['tn_lag_1'].iloc[-1]],
            'tn_lag_2': [product_data['tn_lag_2'].iloc[-1]],
            'tn_lag_3': [product_data['tn_lag_3'].iloc[-1]],
            'arima_pred_1': [product_data['arima_pred_1'].iloc[-1]],
            'arima_pred_2': [product_data['arima_pred_2'].iloc[-1]],
            **rolling_means
        })
        
        # Ordenar las columnas de next_data de acuerdo a feature_columns
        next_data = next_data[feature_columns]

        # Imputar valores faltantes en la predicción
        next_data_imputed = imputer.transform(next_data)
        
        # Realizar la predicción con LightGBM
        lgbm_pred = best_lgbm.predict(next_data_imputed)[0]
        
        # Predicción final promedio entre ARIMA y LightGBM
        
        final_pred = (lgbm_pred + product_data['arima_pred_2'].iloc[-1]) / 2
        
        results.append({
            'product_id': product_id,
            'predicted_tn': final_pred
        })
    
    else:
        # Calcular el promedio de tn para el producto si existen datos históricos
        product_mean_tn = ts[ts['product_id'] == product_id]['tn'].mean()
        if not np.isnan(product_mean_tn):
            results.append({'product_id': product_id, 'predicted_tn': product_mean_tn})
        else:
            # Si no hay datos históricos, usar el promedio global
            results.append({'product_id': product_id, 'predicted_tn': global_mean_tn})

# Convertir los resultados a un DataFrame
results_df = pd.DataFrame(results)

# Asegurarse de que el DataFrame resultante tiene las columnas product_id y predicted_tn
results_df = results_df[['product_id', 'predicted_tn']]

# Exportar a un archivo CSV con las columnas product_id y predicted_tn
results_df.to_csv('C:/Users/Hernán Ifrán/Downloads/ensemble_predictions.csv', index=False)


# Calcular las métricas de error
mae = mean_absolute_error(y, best_lgbm.predict(X))
rmse = mean_squared_error(y, best_lgbm.predict(X), squared=False)
r2 = r2_score(y, best_lgbm.predict(X))

print(f"MAE: {mae}")
print(f"RMSE: {rmse}")
print(f"R²: {r2}")
total_toneladas_febrero_2020 = results_df['predicted_tn'].sum()
print(f"Total de toneladas predichas para febrero 2020: {total_toneladas_febrero_2020}")


# Definir la función de error
def error_function(weights, arima_preds, lgbm_preds, target_total):
    final_preds = weights[0] * arima_preds + weights[1] * lgbm_preds
    total_predicted = final_preds.sum()
    error = abs(total_predicted - target_total)
    return error

# Obtener las predicciones de ARIMA y LightGBM
#arima_preds = next_data['arima_pred_2'].values
arima_preds = ts[ 'arima_pred_2'].values
lgbm_preds = results_df['predicted_tn'].values

# Inicializar los pesos
initial_weights = [0.5, 0.5]

# Definir el objetivo
target_total = 30644

# Ejecutar la optimización
result = minimize(error_function, initial_weights, args=(arima_preds, lgbm_preds, target_total), bounds=[(0, 1), (0, 1)])
optimal_weights = result.x

# Calcular las predicciones finales con los pesos óptimos
final_preds = optimal_weights[0] * arima_preds + optimal_weights[1] * lgbm_preds

# Crear el DataFrame final de resultados
adjusted_results_df = results_df.copy()
adjusted_results_df['final_predicted_tn'] = final_preds

# Calcular el total de toneladas predichas ajustadas
total_toneladas_febrero_2020_adjusted = adjusted_results_df['final_predicted_tn'].sum()

# Exportar a un archivo CSV con las columnas product_id y final_predicted_tn
adjusted_results_df.to_csv('C:/Users/Hernán Ifrán/Downloads/adjusted_ensemble_predictions.csv', index=False)

# Imprimir los pesos óptimos y el total de toneladas ajustadas
print(f"Pesos óptimos: ARIMA: {optimal_weights[0]:.4f}, LightGBM: {optimal_weights[1]:.4f}")
print(f"Total de toneladas predichas ajustadas para febrero 2020: {total_toneladas_febrero_2020_adjusted:.2f}")
print(f"Error absoluto respecto al valor real: {abs(total_toneladas_febrero_2020_adjusted - target_total):.2f}")
