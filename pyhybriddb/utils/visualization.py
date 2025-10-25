"""
Data Visualization utilities for PyHybridDB
Generate charts and statistics for admin panel
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import json


class DataVisualizer:
    """Generate visualization data for charts"""
    
    @staticmethod
    def generate_bar_chart(data: List[Dict], x_field: str, y_field: str) -> Dict[str, Any]:
        """Generate bar chart data"""
        labels = []
        values = []
        
        for item in data:
            labels.append(str(item.get(x_field, '')))
            values.append(float(item.get(y_field, 0)))
        
        return {
            "type": "bar",
            "labels": labels,
            "datasets": [{
                "label": y_field,
                "data": values,
                "backgroundColor": "rgba(102, 126, 234, 0.6)",
                "borderColor": "rgba(102, 126, 234, 1)",
                "borderWidth": 1
            }]
        }
    
    @staticmethod
    def generate_line_chart(data: List[Dict], x_field: str, y_field: str) -> Dict[str, Any]:
        """Generate line chart data"""
        labels = []
        values = []
        
        for item in data:
            labels.append(str(item.get(x_field, '')))
            values.append(float(item.get(y_field, 0)))
        
        return {
            "type": "line",
            "labels": labels,
            "datasets": [{
                "label": y_field,
                "data": values,
                "fill": False,
                "borderColor": "rgba(102, 126, 234, 1)",
                "tension": 0.1
            }]
        }
    
    @staticmethod
    def generate_pie_chart(data: List[Dict], label_field: str, value_field: str) -> Dict[str, Any]:
        """Generate pie chart data"""
        labels = []
        values = []
        
        for item in data:
            labels.append(str(item.get(label_field, '')))
            values.append(float(item.get(value_field, 0)))
        
        colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(255, 198, 128, 0.8)',
            'rgba(250, 227, 97, 0.8)'
        ]
        
        return {
            "type": "pie",
            "labels": labels,
            "datasets": [{
                "data": values,
                "backgroundColor": colors[:len(values)]
            }]
        }
    
    @staticmethod
    def generate_statistics(data: List[Dict], numeric_fields: List[str]) -> Dict[str, Any]:
        """Generate statistical summary"""
        stats = {}
        
        for field in numeric_fields:
            values = [float(item.get(field, 0)) for item in data if item.get(field) is not None]
            
            if values:
                stats[field] = {
                    "count": len(values),
                    "sum": sum(values),
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "median": sorted(values)[len(values) // 2]
                }
        
        return stats
    
    @staticmethod
    def generate_distribution(data: List[Dict], field: str, bins: int = 10) -> Dict[str, Any]:
        """Generate distribution histogram"""
        values = [item.get(field) for item in data if item.get(field) is not None]
        
        if not values:
            return {"labels": [], "data": []}
        
        # Count occurrences
        counter = Counter(values)
        
        labels = list(counter.keys())
        counts = list(counter.values())
        
        return {
            "type": "bar",
            "labels": [str(l) for l in labels],
            "datasets": [{
                "label": f"Distribution of {field}",
                "data": counts,
                "backgroundColor": "rgba(102, 126, 234, 0.6)"
            }]
        }
    
    @staticmethod
    def generate_time_series(data: List[Dict], date_field: str, value_field: str) -> Dict[str, Any]:
        """Generate time series chart"""
        # Sort by date
        sorted_data = sorted(data, key=lambda x: x.get(date_field, ''))
        
        labels = [item.get(date_field, '') for item in sorted_data]
        values = [float(item.get(value_field, 0)) for item in sorted_data]
        
        return {
            "type": "line",
            "labels": labels,
            "datasets": [{
                "label": value_field,
                "data": values,
                "fill": True,
                "backgroundColor": "rgba(102, 126, 234, 0.2)",
                "borderColor": "rgba(102, 126, 234, 1)",
                "tension": 0.4
            }]
        }
    
    @staticmethod
    def generate_table_summary(data: List[Dict]) -> Dict[str, Any]:
        """Generate table summary statistics"""
        if not data:
            return {
                "total_records": 0,
                "fields": [],
                "sample": []
            }
        
        return {
            "total_records": len(data),
            "fields": list(data[0].keys()) if data else [],
            "sample": data[:5],  # First 5 records
            "field_types": {
                field: type(data[0].get(field)).__name__ 
                for field in data[0].keys()
            } if data else {}
        }
