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
    
    def _find_attorney_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the most likely attorney column in a dataframe"""
        attorney_candidates = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['attorney', 'lawyer', 'assigned', 'assigned to', 'handling']):
                attorney_candidates.append(col)
        
        if attorney_candidates:
            return attorney_candidates[0]
        return None
    
    def _find_practice_area_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the most likely practice area column in a dataframe"""
        practice_candidates = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['practice', 'area', 'type', 'category', 'case type']):
                practice_candidates.append(col)
        
        if practice_candidates:
            return practice_candidates[0]
        return None
    
    def _mask_by_range_dates(self, df: pd.DataFrame, date_col: str, start: date, end: date) -> pd.Series:
        """Create mask for date range filtering with robust date parsing"""
        if df is None or df.empty or date_col not in df.columns:
            return pd.Series([False] * (0 if df is None else len(df)))
        
        # Use robust date parsing with format specification to avoid warnings
        ts = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
        if ts.isna().any():
            y = ts.copy()
            for fmt in ("%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M", "%m/%d/%Y"):
                m = y.isna()
                if not m.any(): 
                    break
                try:
                    y.loc[m] = pd.to_datetime(df[date_col].loc[m], format=fmt, errors="coerce")
                except Exception:
                    pass
            ts = y
        
        # Handle NaT values properly
        valid_dates = ts.notna()
        in_range = pd.Series([False] * len(df), index=df.index)
        if valid_dates.any():
            in_range.loc[valid_dates] = (ts.loc[valid_dates].dt.date >= start) & (ts.loc[valid_dates].dt.date <= end)
        return in_range
    
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
        if conversion_metrics is not None and not conversion_metrics.empty:
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
        
        if attorney_data is None or attorney_data.empty:
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
        
        if practice_data is None or practice_data.empty:
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
        """Calculate monthly conversion metrics from actual data"""
        if viz_data['leads'].empty and viz_data['ncl'].empty:
            return None
        
        # Get date column names
        leads_date_col = self._find_date_column(viz_data['leads'])
        ncl_date_col = self._find_date_column(viz_data['ncl'])
        
        if not leads_date_col or not ncl_date_col:
            return None
        
        # Calculate monthly metrics
        monthly_data = []
        
        # Group by month and calculate conversion rates
        if not viz_data['leads'].empty:
            leads_df = viz_data['leads'].copy()
            leads_df['month'] = pd.to_datetime(leads_df[leads_date_col]).dt.to_period('M')
            monthly_leads = leads_df.groupby('month').size().reset_index(name='leads')
            monthly_data.append(monthly_leads)
        
        if not viz_data['ncl'].empty:
            ncl_df = viz_data['ncl'].copy()
            ncl_df['month'] = pd.to_datetime(ncl_df[ncl_date_col]).dt.to_period('M')
            monthly_ncl = ncl_df.groupby('month').size().reset_index(name='retained')
            monthly_data.append(monthly_ncl)
        
        if not monthly_data:
            return None
        
        # Merge all monthly data
        result = monthly_data[0]
        for data in monthly_data[1:]:
            result = result.merge(data, on='month', how='outer')
        
        result = result.fillna(0)
        
        # Calculate conversion rate
        if 'leads' in result.columns and 'retained' in result.columns:
            result['Conversion Rate'] = (result['retained'] / result['leads'] * 100).round(1)
        else:
            result['Conversion Rate'] = 0
        
        # Convert month to string format
        result['Month'] = result['month'].astype(str)
        
        final_result = result[['Month', 'Conversion Rate']].sort_values('Month')
        
        # Return None if no meaningful data
        if final_result.empty or final_result['Conversion Rate'].sum() == 0:
            return None
            
        return final_result
    
    def _get_attorney_performance_data(self, viz_data: Dict) -> Optional[pd.DataFrame]:
        """Get attorney performance data from actual data"""
        # Look for attorney columns in the data
        attorney_data = []
        
        # Check leads data for attorney information
        if not viz_data['leads'].empty:
            leads_df = viz_data['leads'].copy()
            attorney_col = self._find_attorney_column(leads_df)
            if attorney_col:
                leads_by_attorney = leads_df.groupby(attorney_col).size().reset_index(name='leads')
                attorney_data.append(('leads', leads_by_attorney, attorney_col))
        
        # Check new client list for attorney information
        if not viz_data['ncl'].empty:
            ncl_df = viz_data['ncl'].copy()
            attorney_col = self._find_attorney_column(ncl_df)
            if attorney_col:
                ncl_by_attorney = ncl_df.groupby(attorney_col).size().reset_index(name='retained')
                attorney_data.append(('retained', ncl_by_attorney, attorney_col))
        
        if not attorney_data:
            return None
        
        # Merge attorney data
        result = attorney_data[0][1]
        for _, data, col in attorney_data[1:]:
            result = result.merge(data, left_on=attorney_data[0][2], right_on=col, how='outer')
        
        result = result.fillna(0)
        
        # Calculate conversion rate
        if 'leads' in result.columns and 'retained' in result.columns:
            result['Conversion Rate'] = (result['retained'] / result['leads'] * 100).round(1)
        else:
            result['Conversion Rate'] = 0
        
        # Use the first attorney column name
        attorney_col_name = attorney_data[0][2]
        result['Attorney'] = result[attorney_col_name]
        
        # Calculate total cases
        result['Total Cases'] = result['leads'] + result['retained']
        
        final_result = result[['Attorney', 'Conversion Rate', 'Total Cases']].sort_values('Conversion Rate', ascending=False)
        
        # Return None if no meaningful data
        if final_result.empty or final_result['Total Cases'].sum() == 0:
            return None
            
        return final_result
    
    def _get_practice_area_metrics(self, viz_data: Dict) -> Optional[pd.DataFrame]:
        """Get practice area metrics from actual data"""
        # Look for practice area columns in the data
        practice_data = []
        
        # Check leads data for practice area information
        if not viz_data['leads'].empty:
            leads_df = viz_data['leads'].copy()
            practice_col = self._find_practice_area_column(leads_df)
            if practice_col:
                leads_by_practice = leads_df.groupby(practice_col).size().reset_index(name='leads')
                practice_data.append(('leads', leads_by_practice, practice_col))
        
        # Check new client list for practice area information
        if not viz_data['ncl'].empty:
            ncl_df = viz_data['ncl'].copy()
            practice_col = self._find_practice_area_column(ncl_df)
            if practice_col:
                ncl_by_practice = ncl_df.groupby(practice_col).size().reset_index(name='retained')
                practice_data.append(('retained', ncl_by_practice, practice_col))
        
        if not practice_data:
            return None
        
        # Merge practice area data
        result = practice_data[0][1]
        for _, data, col in practice_data[1:]:
            result = result.merge(data, left_on=practice_data[0][2], right_on=col, how='outer')
        
        result = result.fillna(0)
        
        # Calculate conversion rate
        if 'leads' in result.columns and 'retained' in result.columns:
            result['Conversion Rate'] = (result['retained'] / result['leads'] * 100).round(1)
        else:
            result['Conversion Rate'] = 0
        
        # Use the first practice area column name
        practice_col_name = practice_data[0][2]
        result['Practice Area'] = result[practice_col_name]
        
        # Calculate total cases
        result['Cases'] = result['leads'] + result['retained']
        
        final_result = result[['Practice Area', 'Cases', 'Conversion Rate']].sort_values('Cases', ascending=False)
        
        # Return None if no meaningful data
        if final_result.empty or final_result['Cases'].sum() == 0:
            return None
            
        return final_result
    
    def _calculate_conversion_metrics(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Calculate conversion metrics for the given period from actual data"""
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Get date columns
        leads_date_col = self._find_date_column(data_manager.df_leads)
        ic_date_col = self._find_date_column(data_manager.df_ic)
        dm_date_col = self._find_date_column(data_manager.df_dm)
        ncl_date_col = self._find_date_column(data_manager.df_ncl)
        
        # Filter data by date range
        leads_count = 0
        if leads_date_col and not data_manager.df_leads.empty:
            leads_mask = self._mask_by_range_dates(data_manager.df_leads, leads_date_col, start_date, end_date)
            leads_count = leads_mask.sum()
        
        consultations_count = 0
        if ic_date_col and not data_manager.df_ic.empty:
            ic_mask = self._mask_by_range_dates(data_manager.df_ic, ic_date_col, start_date, end_date)
            consultations_count = ic_mask.sum()
        
        discovery_count = 0
        if dm_date_col and not data_manager.df_dm.empty:
            dm_mask = self._mask_by_range_dates(data_manager.df_dm, dm_date_col, start_date, end_date)
            discovery_count = dm_mask.sum()
        
        retained_count = 0
        if ncl_date_col and not data_manager.df_ncl.empty:
            ncl_mask = self._mask_by_range_dates(data_manager.df_ncl, ncl_date_col, start_date, end_date)
            retained_count = ncl_mask.sum()
        
        # Calculate conversion rate
        conversion_rate = (retained_count / leads_count * 100) if leads_count > 0 else 0
        
        return {
            'leads': leads_count,
            'consultations': consultations_count,
            'discovery_meetings': discovery_count,
            'retained': retained_count,
            'conversion_rate': round(conversion_rate, 1)
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
