from PIL.Image import item
import pandas as pd
import numpy as np  
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)

def load_csv(csv):
    df = pd.read_csv(csv, index_col = 0)
    return df 

def prep_features(df):
    y = df['placement']
    item_cols = ['unit_5_item_3', 'unit_5_item_1',	
                            'unit_5_item_2', 'unit_6_item_3',
                            'unit_6_item_1', 'unit_6_item_2',
                            'unit_7_item_3', 'unit_7_item_1',	
                            'unit_7_item_2', 'unit_3_item_3',
                            'unit_3_item_1', 'unit_0_item_3',
                            'unit_1_item_3', 'unit_1_item_1',	
                            'unit_2_item_3', 'unit_2_item_1',	
                            'unit_2_item_2', 'unit_1_item_2',
                            'unit_4_item_3', 'unit_4_item_1',	
                            'unit_4_item_2', 'unit_0_item_1',	
                            'unit_3_item_2', 'unit_0_item_2',	
                            'unit_8_item_3', 'unit_8_item_1',	
                            'unit_8_item_2', 'unit_9_item_3',
                            'unit_9_item_1', 'unit_9_item_2',
                            'unit_10_item_3', 'unit_10_item_1',
                            'unit_10_item_2', 'unit_11_item_3',
                            'unit_11_item_1', 'unit_11_item_2',
                            'unit_12_item_3', 'unit_12_item_1',
                            'unit_12_item_2', 'unit_13_item_3', 
                            'unit_13_item_1', 'unit_13_item_2']
                            
    for item in item_cols:
        try:
            df = df.drop(item, axis='columns')
        except:
            continue
    trait_columns = [col for col in df.columns if col.startswith('trait_')]
    exclude_columns = ['placement', 'riotIdGameName', 'match_id'] + trait_columns

    feature_col = [col for col in df.columns if col not in exclude_columns]

    X = df[feature_col]

    X = pd.get_dummies(X, drop_first=True, dtype='int')

    print(f"\nNumber of features: {X.shape[1]}")
    print(f"Number of samples: {X.shape[0]}")

    return X, y

def train_rf_model(X_train, y_train, X_test, y_test):
    rf_model = RandomForestRegressor(
        n_estimators=100,      
        max_depth=10,          
        min_samples_split=5,   
        min_samples_leaf=2,    
        random_state=42,
        n_jobs=-1 
    )

    print("\n=== Training Random Forest ===")
    print(f"Training on {len(X_train)} samples...")

    rf_model.fit(X_train, y_train)
    y_train_pred = rf_model.predict(X_train)
    y_test_pred = rf_model.predict(X_test)

    print("\n=== Model Performance ===")
    print(f"Training MAE: {mean_absolute_error(y_train, y_train_pred):.3f}")
    print(f"Test MAE: {mean_absolute_error(y_test, y_test_pred):.3f}")
    print(f"\nTraining RMSE: {np.sqrt(mean_squared_error(y_train, y_train_pred)):.3f}")
    print(f"Test RMSE: {np.sqrt(mean_squared_error(y_test, y_test_pred)):.3f}")
    print(f"\nTraining R²: {r2_score(y_train, y_train_pred):.3f}")
    print(f"Test R²: {r2_score(y_test, y_test_pred):.3f}")

    return rf_model, y_test_pred

def cross_validate_model(X, y):
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    print("\n=== Cross-Validation (5-fold) ===")

    cv_scores = cross_val_score(
        rf_model, X, y, 
        cv=5, 
        scoring='neg_mean_absolute_error'
    )

    cv_mae = -cv_scores
    
    print(f"CV MAE scores: {cv_mae}")
    print(f"Mean CV MAE: {cv_mae.mean():.3f} (+/- {cv_mae.std():.3f})")
    
    return cv_mae

def analyze_feature_importance(model, feature_names, top_n=20):
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print(f"\n=== Top {top_n} Most Important Features ===")
    for i in range(min(top_n, len(feature_names))):
        print(f"{i+1}. {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
    
    plt.figure(figsize=(10, 6))
    top_indices = indices[:top_n]
    plt.barh(range(top_n), importances[top_indices])
    plt.yticks(range(top_n), [feature_names[i] for i in top_indices])
    plt.xlabel('Importance')
    plt.title(f'Top {top_n} Feature Importances')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('/Users/christiangrier/Documents/tft_game_research/test/figs/feature_importance.png', dpi=300, bbox_inches='tight')
    print(f"\nFeature importance plot saved to 'feature_importance.png'")

    return importances

def plot_predictions(y_true, y_pred):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].scatter(y_true, y_pred, alpha=0.6)
    axes[0].plot([1, 8], [1, 8], 'r--', lw=2)  
    axes[0].set_xlabel('Actual Placement')
    axes[0].set_ylabel('Predicted Placement')
    axes[0].set_title('Actual vs Predicted Placement')
    axes[0].grid(True, alpha=0.3)

    residuals = y_true - y_pred
    axes[1].scatter(y_pred, residuals, alpha=0.6)
    axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Predicted Placement')
    axes[1].set_ylabel('Residuals (Actual - Predicted)')
    axes[1].set_title('Residual Plot')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/christiangrier/Documents/tft_game_research/test/figs/prediction_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\nPrediction plots saved to 'prediction_analysis.png'")

def plot_placement_distribution(y_true, y_pred):
    plt.figure(figsize=(10, 6))

    y_pred_rounded = np.round(y_pred)
    
    x = np.arange(1, 9)
    width = 0.35
    
    actual_counts = [sum(y_true == i) for i in range(1, 9)]
    pred_counts = [sum(y_pred_rounded == i) for i in range(1, 9)]
    
    plt.bar(x - width/2, actual_counts, width, label='Actual', alpha=0.8)
    plt.bar(x + width/2, pred_counts, width, label='Predicted', alpha=0.8)
    
    plt.xlabel('Placement')
    plt.ylabel('Count')
    plt.title('Distribution of Actual vs Predicted Placements')
    plt.xticks(x)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('/Users/christiangrier/Documents/tft_game_research/test/figs/placement_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\nPlacement distribution plot saved to 'placement_distribution.png'")


def main():
    filepath = '/Users/christiangrier/Documents/tft_game_research/tft_data/cleaned_csv/NA1_5439283217_NA1_5439506130_2001.csv'
    csv = load_csv(filepath)
    X, y = prep_features(csv)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    model, y_pred = train_rf_model(X_train, y_train, X_test, y_test)
    cv_scores = cross_validate_model(X, y)
    importances = analyze_feature_importance(model, X.columns.tolist())
    plot_predictions(y_test, y_pred)
    plot_placement_distribution(y_test, y_pred)

if __name__ == '__main__':
    main()