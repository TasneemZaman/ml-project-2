"""
Visualization Module
Creates visualizations for model results and predictions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)


class ModelVisualizer:
    """Creates visualizations for model analysis"""
    
    def __init__(self, results_dir):
        self.results_dir = results_dir
        
    def plot_model_comparison(self, results_df: pd.DataFrame, save_path: str = None):
        """Plot comparison of model performances"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Sort by test RMSE
        results_df = results_df.sort_values('test_rmse')
        
        # Plot 1: RMSE comparison
        axes[0].barh(results_df.index, results_df['test_rmse'], color='steelblue')
        axes[0].set_xlabel('Test RMSE ($)', fontsize=12)
        axes[0].set_title('Model Performance - RMSE', fontsize=14, fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)
        
        # Plot 2: R² comparison
        axes[1].barh(results_df.index, results_df['test_r2'], color='coral')
        axes[1].set_xlabel('Test R²', fontsize=12)
        axes[1].set_title('Model Performance - R²', fontsize=14, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_prediction_distribution(self, predictions_df: pd.DataFrame, 
                                    save_path: str = None):
        """Plot distribution of predictions across models"""
        fig = go.Figure()
        
        # Box plot
        fig.add_trace(go.Box(
            y=predictions_df['predicted_first_week_income'],
            name='Predictions',
            marker_color='lightblue',
            boxmean='sd'
        ))
        
        # Individual points
        fig.add_trace(go.Scatter(
            x=['Models'] * len(predictions_df),
            y=predictions_df['predicted_first_week_income'],
            mode='markers',
            name='Individual Models',
            marker=dict(size=10, color='red', symbol='diamond'),
            text=predictions_df['model_name'],
            hovertemplate='%{text}<br>$%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Distribution of First Week Income Predictions',
            yaxis_title='Predicted First Week Income ($)',
            showlegend=False,
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def plot_predictions_by_model(self, predictions_df: pd.DataFrame,
                                 save_path: str = None):
        """Plot predictions for each model"""
        predictions_df = predictions_df.sort_values('predicted_first_week_income', 
                                                     ascending=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=predictions_df['model_name'],
            x=predictions_df['predicted_first_week_income'],
            orientation='h',
            marker=dict(
                color=predictions_df['predicted_first_week_income'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Prediction ($)")
            ),
            text=[f"${v:,.0f}" for v in predictions_df['predicted_first_week_income']],
            textposition='auto',
            hovertemplate='%{y}<br>$%{x:,.0f}<extra></extra>'
        ))
        
        # Add mean line
        mean_pred = predictions_df['predicted_first_week_income'].mean()
        fig.add_vline(x=mean_pred, line_dash="dash", line_color="red",
                     annotation_text=f"Mean: ${mean_pred:,.0f}")
        
        fig.update_layout(
            title='First Week Income Predictions by Model',
            xaxis_title='Predicted First Week Income ($)',
            yaxis_title='Model',
            height=max(400, len(predictions_df) * 30),
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def plot_feature_importance(self, model, feature_names: list, 
                               top_n: int = 20, save_path: str = None):
        """Plot feature importance for tree-based models"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Create dataframe
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False).head(top_n)
            
            # Plot
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=importance_df['feature'],
                x=importance_df['importance'],
                orientation='h',
                marker_color='teal'
            ))
            
            fig.update_layout(
                title=f'Top {top_n} Most Important Features',
                xaxis_title='Importance',
                yaxis_title='Feature',
                height=max(400, top_n * 25)
            )
            
            if save_path:
                fig.write_html(save_path)
            
            fig.show()
        else:
            print("Model does not have feature_importances_ attribute")
    
    def plot_actual_vs_predicted(self, y_true, y_pred, model_name: str,
                                save_path: str = None):
        """Plot actual vs predicted values"""
        fig = go.Figure()
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=y_true,
            y=y_pred,
            mode='markers',
            name='Predictions',
            marker=dict(size=8, color='blue', opacity=0.6),
            hovertemplate='Actual: $%{x:,.0f}<br>Predicted: $%{y:,.0f}<extra></extra>'
        ))
        
        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Prediction',
            line=dict(color='red', dash='dash')
        ))
        
        # Calculate R²
        from sklearn.metrics import r2_score
        r2 = r2_score(y_true, y_pred)
        
        fig.update_layout(
            title=f'Actual vs Predicted - {model_name} (R² = {r2:.4f})',
            xaxis_title='Actual First Week Income ($)',
            yaxis_title='Predicted First Week Income ($)',
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def create_dashboard(self, results_df: pd.DataFrame, 
                        predictions_df: pd.DataFrame,
                        save_path: str = None):
        """Create interactive dashboard with all visualizations"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Model Performance (RMSE)', 
                          'Model Performance (R²)',
                          'Prediction Distribution',
                          'Individual Model Predictions'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'box'}, {'type': 'bar'}]]
        )
        
        # Sort results
        results_df = results_df.sort_values('test_rmse')
        
        # Plot 1: RMSE
        fig.add_trace(
            go.Bar(x=results_df['test_rmse'], y=results_df.index, 
                   orientation='h', marker_color='steelblue',
                   name='RMSE'),
            row=1, col=1
        )
        
        # Plot 2: R²
        fig.add_trace(
            go.Bar(x=results_df['test_r2'], y=results_df.index,
                   orientation='h', marker_color='coral',
                   name='R²'),
            row=1, col=2
        )
        
        # Plot 3: Box plot
        fig.add_trace(
            go.Box(y=predictions_df['predicted_first_week_income'],
                   marker_color='lightblue', name='Distribution'),
            row=2, col=1
        )
        
        # Plot 4: Predictions by model
        predictions_sorted = predictions_df.sort_values('predicted_first_week_income')
        fig.add_trace(
            go.Bar(y=predictions_sorted['model_name'],
                   x=predictions_sorted['predicted_first_week_income'],
                   orientation='h', marker_color='green',
                   name='Predictions'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Box Office Prediction Dashboard",
            showlegend=False,
            height=1000
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()


if __name__ == "__main__":
    from config import RESULTS_DIR
    
    # Load results
    results_df = pd.read_csv(RESULTS_DIR / "model_results.csv", index_col=0)
    predictions_df = pd.read_csv(RESULTS_DIR / "all_predictions.csv")
    
    # Create visualizer
    viz = ModelVisualizer(RESULTS_DIR)
    
    # Generate visualizations
    viz.plot_model_comparison(results_df, 
                             save_path=RESULTS_DIR / "model_comparison.png")
    
    viz.plot_predictions_by_model(predictions_df,
                                 save_path=RESULTS_DIR / "predictions_by_model.html")
    
    viz.plot_prediction_distribution(predictions_df,
                                    save_path=RESULTS_DIR / "prediction_distribution.html")
    
    viz.create_dashboard(results_df, predictions_df,
                        save_path=RESULTS_DIR / "dashboard.html")
    
    print("Visualizations created successfully!")
