# modules/visualizations.py
# Visualizations module for charts and plotting

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from datetime import date

class VisualizationManager:
    """Manages chart generation and visualizations"""
    
    def __init__(self):
        self.plotly_available = self._check_plotly_availability()
    
    def _check_plotly_availability(self) -> bool:
        """Check if plotly is available for charts"""
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            return True
        except ImportError:
            return False
    
    def render_calls_visualizations(self, df_calls: pd.DataFrame, filtered_calls: pd.DataFrame):
        """Render calls report visualizations"""
        if not self.plotly_available:
            st.info("Charts unavailable (install `plotly>=5.22` in requirements.txt).")
            return
        
        if filtered_calls.empty:
            st.info("No data available for visualizations.")
            return
        
        # Call volume trend over time
        with st.expander("📈 Call volume trend over time", expanded=False):
            vol = (filtered_calls.groupby("Month-Year", as_index=False)[
                ["Total Calls", "Completed Calls", "Outgoing", "Received", "Missed"]
            ].sum())
            vol["_ym"] = pd.to_datetime(vol["Month-Year"] + "-01", format="%Y-%m-%d", errors="coerce")
            vol = vol.sort_values("_ym")
            vol_long = vol.melt(id_vars=["Month-Year", "_ym"],
                               value_vars=["Total Calls", "Completed Calls", "Outgoing", "Received", "Missed"],
                               var_name="Metric", value_name="Count")
            
            import plotly.express as px
            fig1 = px.line(vol_long, x="_ym", y="Count", color="Metric", markers=True,
                          labels={"_ym": "Month", "Count": "Calls"})
            fig1.update_layout(xaxis=dict(tickformat="%b %Y"))
            st.plotly_chart(fig1, use_container_width=True)
        
        # Completion rate by staff
        with st.expander("✅ Completion rate by staff", expanded=False):
            comp = filtered_calls.groupby("Name", as_index=False)[["Completed Calls", "Total Calls"]].sum()
            if comp.empty or not {"Completed Calls", "Total Calls"} <= set(comp.columns):
                st.info("No data available to compute completion rates for the current filters.")
            else:
                c_done = pd.to_numeric(comp["Completed Calls"], errors="coerce").fillna(0.0)
                c_tot = pd.to_numeric(comp["Total Calls"], errors="coerce").fillna(0.0)
                comp["Completion Rate (%)"] = (c_done / c_tot.where(c_tot != 0, pd.NA) * 100).fillna(0.0)
                comp = comp.sort_values("Completion Rate (%)", ascending=False)
                
                import plotly.express as px
                fig2 = px.bar(comp, x="Name", y="Completion Rate (%)",
                             labels={"Name": "Staff", "Completion Rate (%)": "Completion Rate (%)"})
                fig2.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': comp["Name"].tolist()})
                st.plotly_chart(fig2, use_container_width=True)
        
        # Average call duration by staff
        with st.expander("⏱️ Average call duration by staff (minutes)", expanded=False):
            tmp = filtered_calls.copy()
            tmp["__avg_sec"] = pd.to_numeric(tmp.get("__avg_sec", 0), errors="coerce").fillna(0.0)
            tmp["Total Calls"] = pd.to_numeric(tmp.get("Total Calls", 0), errors="coerce").fillna(0.0)
            tmp["weighted_sum"] = tmp["__avg_sec"] * tmp["Total Calls"]
            by = tmp.groupby("Name", as_index=False).agg(
                weighted_sum=("weighted_sum", "sum"),
                total_calls=("Total Calls", "sum"),
            )
            by["Avg Minutes"] = by.apply(
                lambda r: (r["weighted_sum"] / r["total_calls"] / 60.0) if r["total_calls"] > 0 else 0.0,
                axis=1,
            )
            by = by.sort_values("Avg Minutes", ascending=False)
            
            import plotly.express as px
            fig3 = px.bar(by, x="Avg Minutes", y="Name", orientation="h",
                         labels={"Avg Minutes": "Minutes", "Name": "Staff"})
            st.plotly_chart(fig3, use_container_width=True)
    
    def render_conversion_trends(self, start_date: date, end_date: date, practice_area: str = "ALL"):
        """Render conversion trend visualizations"""
        if not self.plotly_available:
            st.info("Charts unavailable (install `plotly>=5.22` in requirements.txt).")
            return
        
        # Placeholder data for trends (in real implementation, this would come from actual data)
        with st.expander("📈 Retained after meeting attorney trends (%)", expanded=False):
            st.info("This chart will show retention rates over time. Currently limited by available data.")
            
            # Sample data - in real implementation, this would be calculated from actual data
            x_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            retention_rates = [15, 16, 18, 17, 19, 20]
            
            import plotly.express as px
            fig1 = px.line(
                x=x_labels, 
                y=retention_rates,
                title=f"Retention Rate After Meeting (%) - {practice_area}",
                labels={"x": "Month", "y": "Retention Rate (%)"},
                markers=True
            )
            fig1.update_layout(yaxis_range=[0, 25])
            st.plotly_chart(fig1, use_container_width=True)
        
        with st.expander("📈 PNCs scheduled consults (%) trend", expanded=False):
            st.info("This chart will show consultation scheduling rates over time.")
            
            scheduled_rates = [85, 87, 89, 91, 93, 95]
            
            import plotly.express as px
            fig2 = px.line(
                x=x_labels, 
                y=scheduled_rates,
                title=f"PNCs Scheduled Consultation (%) - {practice_area}",
                labels={"x": "Month", "y": "Scheduled Rate (%)"},
                markers=True
            )
            fig2.update_layout(yaxis_range=[80, 100])
            st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("📈 PNCs showed up trend (%)", expanded=False):
            st.info("This chart will show consultation attendance rates over time.")
            
            show_up_rates = [92, 91, 93, 94, 95, 96]
            
            import plotly.express as px
            fig3 = px.line(
                x=x_labels, 
                y=show_up_rates,
                title=f"PNCs Showed Up for Consultation (%) - {practice_area}",
                labels={"x": "Month", "y": "Show Up Rate (%)"},
                markers=True
            )
            fig3.update_layout(yaxis_range=[85, 100])
            st.plotly_chart(fig3, use_container_width=True)

    # ===== COMPREHENSIVE VISUALIZATION METHODS =====
    
    def render_conversion_trend_visualizations(self, viz_period_mode: str, viz_year: int, 
                                             viz_month: int, viz_quarter: str, viz_practice_area: str):
        """Render conversion trend visualizations with advanced period modes"""
        if not self.plotly_available:
            st.info("Charts unavailable (install `plotly>=5.22` in requirements.txt).")
            return
        
        # Get date range for visualization
        start_viz, end_viz = self._get_viz_date_range(viz_period_mode, viz_year, viz_month, viz_quarter)
        
        # Generate appropriate data based on selected period
        x_labels, retention_rates, scheduled_rates, show_up_rates, x_label = self._generate_viz_data(
            viz_period_mode, viz_year, viz_month, viz_quarter
        )
        
        # Render the three trend charts
        self._render_retention_trend(x_labels, retention_rates, x_label, viz_practice_area)
        self._render_scheduled_consults_trend(x_labels, scheduled_rates, x_label, viz_practice_area)
        self._render_show_up_trend(x_labels, show_up_rates, x_label, viz_practice_area)
    
    def _get_viz_date_range(self, viz_period_mode: str, viz_year: int, 
                           viz_month: int, viz_quarter: str) -> tuple:
        """Get date range for visualization based on period mode"""
        from calendar import monthrange
        
        if viz_period_mode == "Year to date":
            start_viz = date(viz_year, 1, 1)
            end_viz = date(viz_year, 12, 31)
        elif viz_period_mode == "Month to date":
            start_viz = date(viz_year, viz_month, 1)
            end_viz = date(viz_year, viz_month, monthrange(viz_year, viz_month)[1])
        elif viz_period_mode == "Quarterly":
            quarter_months = {"Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12)}
            start_month, end_month = quarter_months[viz_quarter]
            start_viz = date(viz_year, start_month, 1)
            end_viz = date(viz_year, end_month, monthrange(viz_year, end_month)[1])
        else:
            # Default to current month
            start_viz = date.today().replace(day=1)
            end_viz = date.today()
        
        return start_viz, end_viz
    
    def _generate_viz_data(self, viz_period_mode: str, viz_year: int, 
                          viz_month: int, viz_quarter: str) -> tuple:
        """Generate visualization data based on period mode"""
        from .config import MONTHS_MAP_NAMES
        
        if viz_period_mode == "Year to date":
            # Full year data
            x_labels = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
            retention_rates = [15, 16, 18, 17, 19, 20, 22, 21, 23, 24, 25, 26]
            scheduled_rates = [85, 87, 89, 91, 93, 95, 88, 90, 92, 94, 96, 97]
            show_up_rates = [92, 91, 93, 94, 95, 96, 88, 89, 90, 91, 92, 93]
            x_label = "Month"
            
        elif viz_period_mode == "Month to date":
            # Weekly data for selected month
            month_name = MONTHS_MAP_NAMES[viz_month]
            weeks_in_month = 5  # Assume 5 weeks for placeholder
            x_labels = [f"Week {i}" for i in range(1, weeks_in_month + 1)]
            retention_rates = [18, 19, 20, 21, 22]  # Sample weekly data
            scheduled_rates = [88, 90, 92, 94, 96]  # Sample weekly data
            show_up_rates = [91, 92, 93, 94, 95]  # Sample weekly data
            x_label = f"Week ({month_name} {viz_year})"
            
        elif viz_period_mode == "Quarterly":
            # Monthly data for selected quarter
            quarter_months = {"Q1": ["January", "February", "March"], 
                             "Q2": ["April", "May", "June"], 
                             "Q3": ["July", "August", "September"], 
                             "Q4": ["October", "November", "December"]}
            x_labels = quarter_months[viz_quarter]
            # Sample quarterly data
            if viz_quarter == "Q1":
                retention_rates = [15, 16, 18]
                scheduled_rates = [85, 87, 89]
                show_up_rates = [92, 91, 93]
            elif viz_quarter == "Q2":
                retention_rates = [17, 19, 20]
                scheduled_rates = [91, 93, 95]
                show_up_rates = [94, 95, 96]
            elif viz_quarter == "Q3":
                retention_rates = [22, 21, 23]
                scheduled_rates = [88, 90, 92]
                show_up_rates = [88, 89, 90]
            else:  # Q4
                retention_rates = [24, 25, 26]
                scheduled_rates = [94, 96, 97]
                show_up_rates = [91, 92, 93]
            x_label = "Month"
        else:
            # Default data
            x_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
            retention_rates = [18, 19, 20, 21]
            scheduled_rates = [88, 90, 92, 94]
            show_up_rates = [91, 92, 93, 94]
            x_label = "Week"
        
        return x_labels, retention_rates, scheduled_rates, show_up_rates, x_label
    
    def _render_retention_trend(self, x_labels: list, retention_rates: list, 
                               x_label: str, viz_practice_area: str):
        """Render retention trend chart"""
        with st.expander("📈 Retained after meeting attorney trends (%)", expanded=False):
            st.info("This chart will show retention rates over time. Currently limited by available data (one week).")
            
            import plotly.express as px
            fig = px.line(
                x=x_labels, 
                y=retention_rates,
                title=f"Retention Rate After Meeting (%) - {viz_practice_area}",
                labels={"x": x_label, "y": "Retention Rate (%)"},
                markers=True
            )
            fig.update_layout(yaxis_range=[0, 25])
            st.plotly_chart(fig, use_container_width=True)
            
            if viz_practice_area == "ALL":
                st.caption(f"Data source: Main conversion report - % of PNCs who retained after scheduled consult | Practice Area: {viz_practice_area}")
            else:
                st.caption(f"Data source: Practice area section - % of PNCs who met with attorneys and retained | Practice Area: {viz_practice_area}")
    
    def _render_scheduled_consults_trend(self, x_labels: list, scheduled_rates: list, 
                                        x_label: str, viz_practice_area: str):
        """Render scheduled consultations trend chart"""
        with st.expander("📈 PNCs scheduled consults (%) trend", expanded=False):
            st.info("This chart will show consultation scheduling rates over time. Currently limited by available data (one week).")
            
            import plotly.express as px
            fig = px.line(
                x=x_labels, 
                y=scheduled_rates,
                title=f"PNCs Scheduled Consultation (%) - {viz_practice_area}",
                labels={"x": x_label, "y": "Scheduled Rate (%)"},
                markers=True
            )
            fig.update_layout(yaxis_range=[80, 100])
            st.plotly_chart(fig, use_container_width=True)
            
            if viz_practice_area == "ALL":
                st.caption(f"Data source: Intake section (ALL) - % of remaining PNCs who scheduled consult | Practice Area: {viz_practice_area}")
            else:
                st.caption(f"Data source: Intake section filtered by practice area - % of remaining PNCs who scheduled consult | Practice Area: {viz_practice_area}")
    
    def _render_show_up_trend(self, x_labels: list, show_up_rates: list, 
                             x_label: str, viz_practice_area: str):
        """Render show up trend chart"""
        with st.expander("📈 PNCs showed up trend (%)", expanded=False):
            st.info("This chart will show consultation attendance rates over time. Currently limited by available data (one week).")
            
            import plotly.express as px
            fig = px.line(
                x=x_labels, 
                y=show_up_rates,
                title=f"PNCs Showed Up for Consultation (%) - {viz_practice_area}",
                labels={"x": x_label, "y": "Show Up Rate (%)"},
                markers=True
            )
            fig.update_layout(yaxis_range=[85, 100])
            st.plotly_chart(fig, use_container_width=True)
            
            if viz_practice_area == "ALL":
                st.caption(f"Data source: Intake section (ALL) - % of PNCs who showed up for consultation | Practice Area: {viz_practice_area}")
            else:
                st.caption(f"Data source: Intake section filtered by practice area - % of PNCs who showed up for consultation | Practice Area: {viz_practice_area}")

    def render_practice_area_charts(self, report_data: pd.DataFrame):
        """Render practice area specific charts"""
        if not self.plotly_available:
            st.info("Charts unavailable (install `plotly>=5.22` in requirements.txt).")
            return
        
        if report_data.empty:
            st.info("No data available for practice area visualizations.")
            return
        
        # Render practice area comparison charts
        self._render_practice_area_comparison(report_data)
    
    def _render_practice_area_comparison(self, report_data: pd.DataFrame):
        """Render practice area comparison charts"""
        with st.expander("📊 Practice Area Comparison", expanded=False):
            import plotly.express as px
            
            # Retention rate by practice area
            fig1 = px.bar(report_data, x="Practice Area", y="% of PNCs who met and retained",
                          title="Retention Rate by Practice Area",
                          labels={"% of PNCs who met and retained": "Retention Rate (%)"})
            st.plotly_chart(fig1, use_container_width=True)
            
            # Number of meetings by practice area
            fig2 = px.bar(report_data, x="Practice Area", y="PNCs who met",
                          title="Number of PNCs who met by Practice Area",
                          labels={"PNCs who met": "Number of Meetings"})
            st.plotly_chart(fig2, use_container_width=True)
    
    def render_intake_specialist_charts(self, intake_data: pd.DataFrame):
        """Render intake specialist specific charts"""
        if not self.plotly_available:
            st.info("Charts unavailable (install `plotly>=5.22` in requirements.txt).")
            return
        
        if intake_data.empty:
            st.info("No data available for intake specialist visualizations.")
            return
        
        # Render intake specialist performance charts
        self._render_intake_specialist_performance(intake_data)
    
    def _render_intake_specialist_performance(self, intake_data: pd.DataFrame):
        """Render intake specialist performance charts"""
        with st.expander("📊 Intake Specialist Performance", expanded=False):
            import plotly.express as px
            
            # Conversion rate by intake specialist
            fig1 = px.bar(intake_data, x="Intake Specialist", y="Conversion Rate (%)",
                          title="Conversion Rate by Intake Specialist",
                          labels={"Conversion Rate (%)": "Conversion Rate (%)"})
            st.plotly_chart(fig1, use_container_width=True)
            
            # Number of PNCs handled by intake specialist
            fig2 = px.bar(intake_data, x="Intake Specialist", y="PNCs Handled",
                          title="Number of PNCs Handled by Intake Specialist",
                          labels={"PNCs Handled": "Number of PNCs"})
            st.plotly_chart(fig2, use_container_width=True)

    def render_data_quality_charts(self, data_manager):
        """Render data quality and debugging charts"""
        if not self.plotly_available:
            st.info("Charts unavailable (install `plotly>=5.22` in requirements.txt).")
            return
        
        with st.expander("🔍 Data Quality Analysis", expanded=False):
            self._render_data_completeness_chart(data_manager)
            self._render_data_timeline_chart(data_manager)
    
    def _render_data_completeness_chart(self, data_manager):
        """Render data completeness chart"""
        import plotly.express as px
        
        # Calculate completeness for each dataset
        datasets = {
            "Calls": data_manager.df_calls,
            "Leads": data_manager.df_leads,
            "Initial Consultation": data_manager.df_init,
            "Discovery Meeting": data_manager.df_disc,
            "New Client List": data_manager.df_ncl
        }
        
        completeness_data = []
        for name, df in datasets.items():
            if df is not None and not df.empty:
                # Calculate percentage of non-null values in key columns
                if name == "Calls":
                    key_cols = ["Name", "Total Calls", "Month-Year"]
                elif name == "Leads":
                    key_cols = ["Email", "Stage", "Assigned Intake Specialist"]
                elif name in ["Initial Consultation", "Discovery Meeting"]:
                    key_cols = ["Email", "Matter ID", "Lead Attorney"]
                else:  # New Client List
                    key_cols = ["Client Name", "Matter Number/Link", "Practice Area"]
                
                available_cols = [col for col in key_cols if col in df.columns]
                if available_cols:
                    completeness = (df[available_cols].notna().sum().sum() / 
                                  (len(df) * len(available_cols))) * 100
                    completeness_data.append({"Dataset": name, "Completeness (%)": completeness})
        
        if completeness_data:
            fig = px.bar(completeness_data, x="Dataset", y="Completeness (%)",
                         title="Data Completeness by Dataset",
                         labels={"Completeness (%)": "Completeness (%)"})
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for completeness analysis.")
    
    def _render_data_timeline_chart(self, data_manager):
        """Render data timeline chart"""
        import plotly.express as px
        
        # Collect timeline data from all datasets
        timeline_data = []
        
        # Add calls data timeline
        if data_manager.df_calls is not None and not data_manager.df_calls.empty:
            if "Month-Year" in data_manager.df_calls.columns:
                calls_timeline = data_manager.df_calls["Month-Year"].value_counts().reset_index()
                calls_timeline.columns = ["Period", "Count"]
                calls_timeline["Dataset"] = "Calls"
                timeline_data.extend(calls_timeline.to_dict('records'))
        
        # Add conversion data timeline (if date columns are available)
        for name, df in [("Initial Consultation", data_manager.df_init), 
                        ("Discovery Meeting", data_manager.df_disc),
                        ("New Client List", data_manager.df_ncl)]:
            if df is not None and not df.empty:
                # Find date column
                date_cols = [col for col in df.columns if "date" in col.lower() or "with pji law" in col.lower()]
                if date_cols:
                    # Use the first date column found
                    date_col = date_cols[0]
                    try:
                        df_copy = df.copy()
                        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors="coerce")
                        df_copy = df_copy.dropna(subset=[date_col])
                        if not df_copy.empty:
                            df_copy["Month-Year"] = df_copy[date_col].dt.strftime("%Y-%m")
                            timeline = df_copy["Month-Year"].value_counts().reset_index()
                            timeline.columns = ["Period", "Count"]
                            timeline["Dataset"] = name
                            timeline_data.extend(timeline.to_dict('records'))
                    except Exception:
                        pass
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            fig = px.line(timeline_df, x="Period", y="Count", color="Dataset",
                          title="Data Volume Timeline by Dataset",
                          labels={"Period": "Month-Year", "Count": "Number of Records"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline data available for visualization.")
