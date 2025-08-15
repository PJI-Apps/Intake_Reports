# modules/visualizations.py
# Visualization Manager module for generating charts and graphs

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, datetime, timedelta
from calendar import monthrange
from typing import Optional, Dict, List, Tuple
import numpy as np

from .config import (
    MONTHS_MAP, MONTHS_MAP_NAMES, PRACTICE_AREAS, DISPLAY_NAME_OVERRIDES,
    INITIALS_TO_ATTORNEY, INTAKE_SPECIALISTS, INTAKE_INITIALS_TO_NAME
)

class VisualizationManager:
    """Manages all chart generation and visualization components"""
    
    def __init__(self):
        # Color schemes for consistent styling
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b',
            'dark': '#e377c2'
        }
        
        # Chart configuration
        self.chart_config = {
            'displayModeBar': False,
            'responsive': True
        }
    
    def render_conversion_trend_visualizations(self, data_manager, date_range: Tuple[date, date]):
        """Render conversion trend charts"""
        st.subheader("📈 Conversion Trends")
        
        # Get data for the date range
        viz_data = self._generate_viz_data(data_manager, date_range)
        
        if not viz_data['has_data']:
            st.info("No data available for the selected date range.")
            return
        
        # Create tabs for different chart types
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Monthly Trends", "👥 Attorney Performance", "🏢 Practice Areas", "📞 Call Analysis"])
        
        with tab1:
            self._render_monthly_trends(viz_data)
        
        with tab2:
            self._render_attorney_performance(viz_data)
        
        with tab3:
            self._render_practice_area_charts(viz_data)
        
        with tab4:
            self._render_call_analysis(viz_data)
    
    def render_calls_visualizations(self, data_manager):
        """Render call-specific visualizations"""
        st.subheader("📞 Call Volume Analysis")
        
        if not hasattr(data_manager, 'df_calls') or data_manager.df_calls.empty:
            st.info("No call data available.")
            return
        
        # Call volume over time
        self._render_call_volume_trend(data_manager.df_calls)
        
        # Call distribution by category
        self._render_call_category_distribution(data_manager.df_calls)
        
        # Call duration analysis
        self._render_call_duration_analysis(data_manager.df_calls)
    
    def render_conversion_trends(self, data_manager, start_date: date, end_date: date):
        """Render detailed conversion trend analysis"""
        st.subheader("🔄 Conversion Funnel Analysis")
        
        # Calculate conversion metrics
        conversion_data = self._calculate_conversion_metrics(data_manager, start_date, end_date)
        
        if not conversion_data:
            st.info("No conversion data available for the selected period.")
            return
        
        # Funnel chart
        self._render_conversion_funnel(conversion_data)
        
        # Conversion rates over time
        self._render_conversion_rates_trend(conversion_data)
    
    def render_practice_area_charts(self, data_manager, start_date: date, end_date: date):
        """Render practice area specific charts"""
        st.subheader("🏢 Practice Area Performance")
        
        practice_data = self._get_practice_area_data(data_manager, start_date, end_date)
        
        if not practice_data:
            st.info("No practice area data available.")
            return
        
        # Practice area comparison
        self._render_practice_area_comparison(practice_data)
        
        # Practice area trends
        self._render_practice_area_trends(practice_data)
    
    def render_intake_specialist_charts(self, data_manager, start_date: date, end_date: date):
        """Render intake specialist performance charts"""
        st.subheader("👤 Intake Specialist Performance")
        
        intake_data = self._get_intake_specialist_data(data_manager, start_date, end_date)
        
        if not intake_data:
            st.info("No intake specialist data available.")
            return
        
        # Intake specialist performance
        self._render_intake_specialist_performance(intake_data)
        
        # Intake specialist trends
        self._render_intake_specialist_trends(intake_data)
    
    # ===== PRIVATE HELPER METHODS =====
    
    def _generate_viz_data(self, data_manager, date_range: Tuple[date, date]) -> Dict:
        """Generate visualization data for the given date range"""
        start_date, end_date = date_range
        
        # Check if we have any data - safely check for attributes
        has_calls = hasattr(data_manager, 'df_calls') and not data_manager.df_calls.empty
        has_leads = hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty
        has_ic = hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty
        has_dm = hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty
        has_ncl = hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty
        
        has_data = any([has_calls, has_leads, has_ic, has_dm, has_ncl])
        
        if not has_data:
            return {'has_data': False}
        
        # Filter data by date range
        calls_data = self._filter_calls_by_date(data_manager.df_calls, start_date, end_date) if has_calls else pd.DataFrame()
        leads_data = self._filter_conversion_by_date(data_manager.df_leads, start_date, end_date) if has_leads else pd.DataFrame()
        ic_data = self._filter_conversion_by_date(data_manager.df_ic, start_date, end_date) if has_ic else pd.DataFrame()
        dm_data = self._filter_conversion_by_date(data_manager.df_dm, start_date, end_date) if has_dm else pd.DataFrame()
        ncl_data = self._filter_conversion_by_date(data_manager.df_ncl, start_date, end_date) if has_ncl else pd.DataFrame()
        
        return {
            'has_data': True,
            'calls': calls_data,
            'leads': leads_data,
            'ic': ic_data,
            'dm': dm_data,
            'ncl': ncl_data,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def _filter_calls_by_date(self, df_calls: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """Filter calls data by date range"""
        if df_calls.empty or 'Month-Year' not in df_calls.columns:
            return pd.DataFrame()
        
        # Convert Month-Year to date for filtering
        df_filtered = df_calls.copy()
        df_filtered['date'] = pd.to_datetime(df_filtered['Month-Year'] + '-01', format='%Y-%m-%d', errors='coerce')
        
        mask = (df_filtered['date'].dt.date >= start_date) & (df_filtered['date'].dt.date <= end_date)
        return df_filtered[mask].copy()
    
    def _filter_conversion_by_date(self, df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """Filter conversion data by date range"""
        if df.empty:
            return pd.DataFrame()
        
        # Find date column
        date_col = self._find_date_column(df)
        if not date_col:
            return df  # Return all data if no date column found
        
        # Convert to datetime and filter
        df_filtered = df.copy()
        df_filtered['date'] = pd.to_datetime(df_filtered[date_col], errors='coerce')
        
        mask = (df_filtered['date'].dt.date >= start_date) & (df_filtered['date'].dt.date <= end_date)
        return df_filtered[mask].copy()
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the most likely date column in a dataframe"""
        date_candidates = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['date', 'created', 'updated', 'time']):
                date_candidates.append(col)
        
        if date_candidates:
            return date_candidates[0]
        return None
    
    def _render_monthly_trends(self, viz_data: Dict):
        """Render monthly trend charts"""
        # Monthly call volume
        if not viz_data['calls'].empty:
            monthly_calls = viz_data['calls'].groupby('Month-Year')['Total Calls'].sum().reset_index()
            
            fig = px.line(monthly_calls, x='Month-Year', y='Total Calls', 
                         title='Monthly Call Volume',
                         labels={'Total Calls': 'Total Calls', 'Month-Year': 'Month'},
                         color_discrete_sequence=[self.colors['primary']])
            
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Total Calls",
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
        
        # Monthly conversion metrics
        conversion_metrics = self._calculate_monthly_conversion_metrics(viz_data)
        if conversion_metrics:
            fig = px.line(conversion_metrics, x='Month', y='Conversion Rate', 
                         title='Monthly Conversion Rate',
                         labels={'Conversion Rate': 'Conversion Rate (%)', 'Month': 'Month'},
                         color_discrete_sequence=[self.colors['success']])
            
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Conversion Rate (%)",
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_attorney_performance(self, viz_data: Dict):
        """Render attorney performance charts"""
        # Get attorney performance data
        attorney_data = self._get_attorney_performance_data(viz_data)
        
        if not attorney_data:
            st.info("No attorney performance data available.")
            return
        
        # Attorney conversion rates
        fig = px.bar(attorney_data, x='Attorney', y='Conversion Rate',
                    title='Attorney Conversion Rates',
                    labels={'Conversion Rate': 'Conversion Rate (%)', 'Attorney': 'Attorney'},
                    color='Conversion Rate',
                    color_continuous_scale='viridis')
        
        fig.update_layout(
            xaxis_title="Attorney",
            yaxis_title="Conversion Rate (%)",
            height=500,
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
        
        # Attorney workload
        if 'Total Cases' in attorney_data.columns:
            fig2 = px.bar(attorney_data, x='Attorney', y='Total Cases',
                         title='Attorney Case Load',
                         labels={'Total Cases': 'Total Cases', 'Attorney': 'Attorney'},
                         color='Total Cases',
                         color_continuous_scale='plasma')
            
            fig2.update_layout(
                xaxis_title="Attorney",
                yaxis_title="Total Cases",
                height=400,
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig2, use_container_width=True, config=self.chart_config)
    
    def _render_practice_area_charts(self, viz_data: Dict):
        """Render practice area charts"""
        practice_data = self._get_practice_area_metrics(viz_data)
        
        if not practice_data:
            st.info("No practice area data available.")
            return
        
        # Practice area distribution
        fig = px.pie(practice_data, values='Cases', names='Practice Area',
                    title='Case Distribution by Practice Area',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
        
        # Practice area performance
        if 'Conversion Rate' in practice_data.columns:
            fig2 = px.bar(practice_data, x='Practice Area', y='Conversion Rate',
                         title='Practice Area Conversion Rates',
                         labels={'Conversion Rate': 'Conversion Rate (%)', 'Practice Area': 'Practice Area'},
                         color='Conversion Rate',
                         color_continuous_scale='viridis')
            
            fig2.update_layout(
                xaxis_title="Practice Area",
                yaxis_title="Conversion Rate (%)",
                height=400,
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig2, use_container_width=True, config=self.chart_config)
    
    def _render_call_analysis(self, viz_data: Dict):
        """Render call analysis charts"""
        if viz_data['calls'].empty:
            st.info("No call data available for analysis.")
            return
        
        calls_df = viz_data['calls']
        
        # Call category distribution
        if 'Category' in calls_df.columns:
            category_counts = calls_df['Category'].value_counts()
            
            fig = px.pie(values=category_counts.values, names=category_counts.index,
                        title='Call Distribution by Category',
                        color_discrete_sequence=px.colors.qualitative.Pastel1)
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
        
        # Call status distribution
        status_columns = ['Completed Calls', 'Missed', 'Forwarded to Voicemail', 'Answered by Other']
        available_status = [col for col in status_columns if col in calls_df.columns]
        
        if available_status:
            status_data = calls_df[available_status].sum()
            
            fig2 = px.bar(x=status_data.index, y=status_data.values,
                         title='Call Status Distribution',
                         labels={'x': 'Call Status', 'y': 'Number of Calls'},
                         color=status_data.values,
                         color_continuous_scale='viridis')
            
            fig2.update_layout(
                xaxis_title="Call Status",
                yaxis_title="Number of Calls",
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True, config=self.chart_config)
    
    def _render_call_volume_trend(self, df_calls: pd.DataFrame):
        """Render call volume trend chart"""
        if df_calls.empty or 'Month-Year' not in df_calls.columns:
            st.info("No call volume data available.")
            return
        
        monthly_volume = df_calls.groupby('Month-Year')['Total Calls'].sum().reset_index()
        
        fig = px.line(monthly_volume, x='Month-Year', y='Total Calls',
                     title='Call Volume Trend Over Time',
                     labels={'Total Calls': 'Total Calls', 'Month-Year': 'Month'},
                     color_discrete_sequence=[self.colors['primary']])
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Calls",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_call_category_distribution(self, df_calls: pd.DataFrame):
        """Render call category distribution chart"""
        if df_calls.empty or 'Category' not in df_calls.columns:
            st.info("No call category data available.")
            return
        
        category_counts = df_calls['Category'].value_counts()
        
        fig = px.pie(values=category_counts.values, names=category_counts.index,
                    title='Call Distribution by Category',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_call_duration_analysis(self, df_calls: pd.DataFrame):
        """Render call duration analysis chart"""
        if df_calls.empty or 'Avg Call Time' not in df_calls.columns:
            st.info("No call duration data available.")
            return
        
        # Convert call time to numeric for analysis
        df_calls_copy = df_calls.copy()
        df_calls_copy['Avg Call Time Num'] = pd.to_numeric(df_calls_copy['Avg Call Time'], errors='coerce')
        
        # Remove outliers for better visualization
        Q1 = df_calls_copy['Avg Call Time Num'].quantile(0.25)
        Q3 = df_calls_copy['Avg Call Time Num'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        filtered_data = df_calls_copy[
            (df_calls_copy['Avg Call Time Num'] >= lower_bound) & 
            (df_calls_copy['Avg Call Time Num'] <= upper_bound)
        ]
        
        fig = px.histogram(filtered_data, x='Avg Call Time Num',
                          title='Distribution of Average Call Duration',
                          labels={'Avg Call Time Num': 'Average Call Time (minutes)', 'count': 'Number of Calls'},
                          nbins=20,
                          color_discrete_sequence=[self.colors['info']])
        
        fig.update_layout(
            xaxis_title="Average Call Time (minutes)",
            yaxis_title="Number of Calls",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _calculate_monthly_conversion_metrics(self, viz_data: Dict) -> Optional[pd.DataFrame]:
        """Calculate monthly conversion metrics"""
        # This would calculate conversion rates from leads to retained clients
        # For now, return a sample structure
        if viz_data['leads'].empty and viz_data['ncl'].empty:
            return None
        
        # Placeholder implementation
        months = ['2025-01', '2025-02', '2025-03']
        rates = [15.2, 18.7, 16.9]
        
        return pd.DataFrame({
            'Month': months,
            'Conversion Rate': rates
        })
    
    def _get_attorney_performance_data(self, viz_data: Dict) -> Optional[pd.DataFrame]:
        """Get attorney performance data"""
        # This would aggregate data by attorney
        # For now, return sample data
        attorneys = ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Wilson']
        conversion_rates = [22.5, 18.3, 25.1, 19.8]
        total_cases = [45, 38, 52, 41]
        
        return pd.DataFrame({
            'Attorney': attorneys,
            'Conversion Rate': conversion_rates,
            'Total Cases': total_cases
        })
    
    def _get_practice_area_metrics(self, viz_data: Dict) -> Optional[pd.DataFrame]:
        """Get practice area metrics"""
        # This would aggregate data by practice area
        # For now, return sample data
        practice_areas = ['Personal Injury', 'Medical Malpractice', 'Workers Comp', 'Other']
        cases = [120, 85, 65, 45]
        conversion_rates = [20.5, 18.2, 22.1, 15.8]
        
        return pd.DataFrame({
            'Practice Area': practice_areas,
            'Cases': cases,
            'Conversion Rate': conversion_rates
        })
    
    def _calculate_conversion_metrics(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Calculate conversion metrics for the given period"""
        # This would calculate actual conversion metrics from the data
        # For now, return sample data
        return {
            'leads': 150,
            'consultations': 45,
            'discovery_meetings': 28,
            'retained': 12,
            'conversion_rate': 8.0
        }
    
    def _get_practice_area_data(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Get practice area data for the given period"""
        # This would filter and aggregate practice area data
        # For now, return sample data
        return {
            'practice_areas': ['Personal Injury', 'Medical Malpractice', 'Workers Comp'],
            'cases': [45, 32, 28],
            'conversion_rates': [18.5, 22.1, 16.8]
        }
    
    def _get_intake_specialist_data(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Get intake specialist data for the given period"""
        # This would filter and aggregate intake specialist data
        # For now, return sample data
        return {
            'specialists': ['Rebecca', 'Jennifer', 'Everyone Else'],
            'cases': [65, 48, 32],
            'conversion_rates': [20.3, 18.7, 15.2]
        }
    
    def _render_conversion_funnel(self, conversion_data: Dict):
        """Render conversion funnel chart"""
        stages = ['Leads', 'Consultations', 'Discovery Meetings', 'Retained']
        values = [
            conversion_data.get('leads', 0),
            conversion_data.get('consultations', 0),
            conversion_data.get('discovery_meetings', 0),
            conversion_data.get('retained', 0)
        ]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(
            title="Conversion Funnel",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_conversion_rates_trend(self, conversion_data: Dict):
        """Render conversion rates trend chart"""
        # This would show conversion rates over time
        # For now, show a placeholder
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        rates = [8.2, 9.1, 7.8, 10.3, 8.9]
        
        fig = px.line(x=months, y=rates,
                     title='Conversion Rate Trend',
                     labels={'x': 'Month', 'y': 'Conversion Rate (%)'},
                     color_discrete_sequence=[self.colors['success']])
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Conversion Rate (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_practice_area_comparison(self, practice_data: Dict):
        """Render practice area comparison chart"""
        fig = px.bar(x=practice_data['practice_areas'], y=practice_data['cases'],
                    title='Cases by Practice Area',
                    labels={'x': 'Practice Area', 'y': 'Number of Cases'},
                    color=practice_data['cases'],
                    color_continuous_scale='viridis')
        
        fig.update_layout(
            xaxis_title="Practice Area",
            yaxis_title="Number of Cases",
            height=400,
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_practice_area_trends(self, practice_data: Dict):
        """Render practice area trends chart"""
        # This would show trends over time for each practice area
        # For now, show a placeholder
        st.info("Practice area trends over time would be displayed here.")
    
    def _render_intake_specialist_performance(self, intake_data: Dict):
        """Render intake specialist performance chart"""
        fig = px.bar(x=intake_data['specialists'], y=intake_data['conversion_rates'],
                    title='Intake Specialist Conversion Rates',
                    labels={'x': 'Intake Specialist', 'y': 'Conversion Rate (%)'},
                    color=intake_data['conversion_rates'],
                    color_continuous_scale='plasma')
        
        fig.update_layout(
            xaxis_title="Intake Specialist",
            yaxis_title="Conversion Rate (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True, config=self.chart_config)
    
    def _render_intake_specialist_trends(self, intake_data: Dict):
        """Render intake specialist trends chart"""
        # This would show trends over time for each intake specialist
        # For now, show a placeholder
        st.info("Intake specialist trends over time would be displayed here.")
