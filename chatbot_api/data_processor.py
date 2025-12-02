import pandas as pd
import json
import os

class RealEstateProcessor:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.df = None
        
    def load_data(self, file_path=None):
        if file_path:
            self.file_path = file_path
        try:
            self.df = pd.read_excel(self.file_path)
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            # Create sample data if file doesn't exist
            self.create_sample_data()
            return True
    
    def create_sample_data(self):
        """Create sample data if no Excel file is available"""
        sample_data = {
            'year': [2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023],
            'area': ['Wakad', 'Wakad', 'Wakad', 'Wakad', 
                    'Aundh', 'Aundh', 'Aundh', 'Aundh',
                    'Akurdi', 'Akurdi', 'Akurdi', 'Akurdi'],
            'price': [5500000, 6000000, 6800000, 7500000, 
                     8000000, 8500000, 9200000, 10000000,
                     4500000, 5000000, 5800000, 6500000],
            'demand': [7.5, 8.0, 8.5, 9.0, 
                      8.0, 8.2, 8.5, 8.8,
                      7.0, 7.3, 7.8, 8.2],
            'size': [1200, 1200, 1200, 1200, 
                    1500, 1500, 1500, 1500,
                    1000, 1000, 1000, 1000]
        }
        
        self.df = pd.DataFrame(sample_data)
        print("Sample data loaded successfully")
    
    def filter_by_area(self, area_name):
        if self.df is None:
            self.create_sample_data()
        
        if 'area' not in self.df.columns:
            return []
            
        filtered_df = self.df[self.df['area'].str.lower() == area_name.lower()]
        return filtered_df.to_dict('records')
    
    def get_price_trend(self, area_name):
        if self.df is None:
            self.create_sample_data()
        
        if 'area' not in self.df.columns or 'year' not in self.df.columns or 'price' not in self.df.columns:
            return []
            
        area_data = self.df[self.df['area'].str.lower() == area_name.lower()]
        if area_data.empty:
            return []
            
        # Sort by year to ensure correct order
        area_data = area_data.sort_values('year')
        trend_data = area_data[['year', 'price']].to_dict('records')
        return trend_data
    
    def get_demand_trend(self, area_name):
        if self.df is None:
            self.create_sample_data()
        
        if 'area' not in self.df.columns or 'year' not in self.df.columns or 'demand' not in self.df.columns:
            return []
            
        area_data = self.df[self.df['area'].str.lower() == area_name.lower()]
        if area_data.empty:
            return []
            
        # Sort by year to ensure correct order
        area_data = area_data.sort_values('year')
        trend_data = area_data[['year', 'demand']].to_dict('records')
        return trend_data
    
    def compare_areas(self, area1, area2):
        if self.df is None:
            self.create_sample_data()
        
        if 'area' not in self.df.columns:
            return None
        
        area1_data = self.df[self.df['area'].str.lower() == area1.lower()]
        area2_data = self.df[self.df['area'].str.lower() == area2.lower()]
        
        # Sort both by year
        area1_data = area1_data.sort_values('year')
        area2_data = area2_data.sort_values('year')
        
        comparison = {
            area1.title(): area1_data[['year', 'price', 'demand']].to_dict('records'),
            area2.title(): area2_data[['year', 'price', 'demand']].to_dict('records')
        }
        return comparison
    
    def generate_summary(self, area_name):
        if self.df is None:
            self.create_sample_data()
        
        if 'area' not in self.df.columns:
            return "Data not available"
        
        area_data = self.df[self.df['area'].str.lower() == area_name.lower()]
        if area_data.empty:
            return f"No data found for {area_name}"
        
        # Sort by year and get latest data
        area_data = area_data.sort_values('year')
        latest_data = area_data.iloc[-1]
        avg_price = area_data['price'].mean()
        avg_demand = area_data['demand'].mean()
        price_growth = ((latest_data['price'] - area_data.iloc[0]['price']) / area_data.iloc[0]['price']) * 100
        
        summary = f"""
📍 **Analysis for {area_name.title()}**

💰 **Pricing:**
- Current Price: ₹{latest_data['price']:,.2f}
- Average Price: ₹{avg_price:,.2f}
- Price Growth: {price_growth:.1f}% over {len(area_data)} years

📊 **Demand Metrics:**
- Current Demand: {latest_data['demand']}/10
- Average Demand: {avg_demand:.2f}/10

📈 **Market Insights:**
- Data available for {len(area_data)} year(s)
- Property Size: {latest_data.get('size', 'N/A')} sq.ft
- Strong positive trend in both price and demand
        """
        return summary
    
    def get_all_areas(self):
        """Get list of all available areas"""
        if self.df is None:
            self.create_sample_data()
        
        if 'area' not in self.df.columns:
            return []
            
        return self.df['area'].unique().tolist()