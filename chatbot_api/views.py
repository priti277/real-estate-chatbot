from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .data_processor import RealEstateProcessor
import os
import re

# Initialize processor
processor = RealEstateProcessor()

@api_view(['GET'])
def initialize_data(request):
    processor.create_sample_data()
    return Response({'message': 'Data initialized successfully'})

@api_view(['POST'])
def analyze_area(request):
    query = request.data.get('query', '').strip().lower()
    
    # Get all available areas for flexible matching
    available_areas = processor.get_all_areas()
    
    # Smart area detection - find any mentioned area
    mentioned_areas = []
    for area in available_areas:
        area_lower = area.lower()
        # More flexible matching
        if area_lower in query or area_lower.replace(' ', '') in query.replace(' ', ''):
            mentioned_areas.append(area)
    
    print(f"Query: {query}")
    print(f"Mentioned areas: {mentioned_areas}")
    
    # If multiple areas mentioned, do comparison
    if len(mentioned_areas) >= 2 and any(word in query for word in ['compare', 'vs', 'versus', 'difference', 'between']):
        return handle_comparison(mentioned_areas[:2], query)
    
    # If specific area mentioned, analyze it
    elif len(mentioned_areas) == 1:
        return handle_single_area(mentioned_areas[0], query)
    
    # If no area mentioned but query type detected
    elif len(mentioned_areas) == 0:
        return handle_general_query(query, available_areas)
    
    # Multiple areas but no comparison keyword - analyze first one
    elif len(mentioned_areas) > 1:
        return handle_single_area(mentioned_areas[0], query)

def handle_comparison(areas, query):
    """Handle comparison between two areas"""
    area1, area2 = areas
    comparison = processor.compare_areas(area1, area2)
    
    # Get detailed data for both areas
    area1_data = processor.df[processor.df['area'] == area1]
    area2_data = processor.df[processor.df['area'] == area2]
    
    # Calculate metrics
    area1_avg_price = area1_data['price'].mean()
    area2_avg_price = area2_data['price'].mean()
    area1_avg_demand = area1_data['demand'].mean()
    area2_avg_demand = area2_data['demand'].mean()
    area1_latest = area1_data.iloc[-1] if not area1_data.empty else None
    area2_latest = area2_data.iloc[-1] if not area2_data.empty else None
    
    price_diff = area1_avg_price - area2_avg_price
    demand_diff = area1_avg_demand - area2_avg_demand
    
    # Generate smart comparison summary
    if price_diff > 0:
        price_insight = f"{area1} is {price_diff:,.0f}% more expensive than {area2}"
    else:
        price_insight = f"{area2} is {abs(price_diff):,.0f}% more expensive than {area1}"
    
    if demand_diff > 0:
        demand_insight = f"{area1} has higher demand (+{demand_diff:.1f} points)"
    else:
        demand_insight = f"{area2} has higher demand (+{abs(demand_diff):.1f} points)"
    
    summary = f"""
🏢 **COMPARISON REPORT: {area1.upper()} vs {area2.upper()}**

💰 **PRICING ANALYSIS**
• {area1}: ₹{area1_avg_price:,.0f} (average)
• {area2}: ₹{area2_avg_price:,.0f} (average)
• {price_insight}

📊 **DEMAND METRICS**
• {area1}: {area1_avg_demand:.1f}/10 (average demand)
• {area2}: {area2_avg_demand:.1f}/10 (average demand)
• {demand_insight}

🎯 **RECOMMENDATION**
{area1 if area1_avg_demand > area2_avg_demand and price_diff < 1000000 else area2} appears to offer better value based on current metrics.
"""
    
    return Response({
        'summary': summary,
        'comparison_data': comparison,
        'type': 'comparison',
        'areas': areas
    })

def handle_single_area(area, query):
    """Handle analysis for a single area with smart response based on query"""
    area_data = processor.df[processor.df['area'] == area]
    
    if area_data.empty:
        return Response({
            'summary': f"❌ No data available for {area}. Available areas: {', '.join(processor.get_all_areas())}",
            'type': 'error'
        })
    
    # Calculate metrics
    latest_data = area_data.iloc[-1]
    avg_price = area_data['price'].mean()
    avg_demand = area_data['demand'].mean()
    price_growth = ((latest_data['price'] - area_data.iloc[0]['price']) / area_data.iloc[0]['price']) * 100
    years_available = len(area_data)
    
    # Smart response based on query content
    if any(word in query for word in ['price', 'cost', 'expensive', 'cheap', 'rate']):
        summary = generate_price_focused_summary(area, area_data, latest_data, avg_price, price_growth)
    elif any(word in query for word in ['demand', 'popular', 'trending', 'hot']):
        summary = generate_demand_focused_summary(area, area_data, latest_data, avg_demand)
    elif any(word in query for word in ['growth', 'increase', 'decrease', 'trend']):
        summary = generate_growth_summary(area, area_data, price_growth)
    elif any(word in query for word in ['investment', 'invest', 'return']):
        summary = generate_investment_summary(area, area_data, price_growth, avg_demand)
    else:
        summary = generate_comprehensive_summary(area, area_data, latest_data, avg_price, avg_demand, price_growth, years_available)
    
    price_trend = processor.get_price_trend(area)
    table_data = processor.filter_by_area(area)
    
    return Response({
        'summary': summary,
        'chart_data': {
            'labels': [item['year'] for item in price_trend],
            'prices': [item['price'] for item in price_trend]
        },
        'table_data': table_data,
        'area': area,
        'type': 'analysis'
    })

def handle_general_query(query, available_areas):
    """Handle queries without specific area mentions"""
    if any(word in query for word in ['list', 'show', 'all areas', 'available']):
        areas_list = "\n".join([f"• {area}" for area in available_areas])
        summary = f"🏘️ **AVAILABLE AREAS**\n\n{areas_list}\n\n💡 Ask about any area for detailed analysis!"
    
    elif any(word in query for word in ['help', 'what can', 'how to']):
        summary = """🤖 **REAL ESTATE AI ASSISTANT**

I can help you with:

🔍 **Area Analysis**
• "Tell me about Wakad"
• "Analyze Aundh prices"
• "Show me demand in Akurdi"

📊 **Comparisons**
• "Compare Aundh and Wakad"
• "Which is better: Aundh vs Akurdi?"

💹 **Trends & Growth**
• "Price growth in Wakad"
• "Demand trends for Aundh"
• "Investment potential in Akurdi"

📈 **Market Insights**
• "Latest market trends"
• "Best investment areas"
• "Price predictions"

Just ask me anything about real estate! 🏠"""
    
    elif any(word in query for word in ['best', 'top', 'recommend']):
        # Simple recommendation based on data
        best_areas = get_recommendations()
        summary = f"""🏆 **TOP RECOMMENDATIONS**

Based on current market data:

{best_areas}

💡 Ask about specific areas for detailed analysis!"""
    
    else:
        summary = f"""🤔 **I UNDERSTOOD: "{query}"**

I can help you analyze real estate data! Try:

• Mention an area: "Tell me about Wakad", "Aundh prices"
• Compare areas: "Compare Aundh and Wakad"
• Ask about trends: "Price growth", "Demand analysis"

Available areas: {', '.join(available_areas)}"""
    
    return Response({
        'summary': summary,
        'type': 'info'
    })

def generate_price_focused_summary(area, area_data, latest_data, avg_price, price_growth):
    """Generate summary focused on pricing"""
    min_price = area_data['price'].min()
    max_price = area_data['price'].max()
    
    return f"""💰 **PRICE ANALYSIS: {area.upper()}**

📊 **Current Market Price**
• Latest: ₹{latest_data['price']:,.0f}
• Average: ₹{avg_price:,.0f}
• Range: ₹{min_price:,.0f} - ₹{max_price:,.0f}

📈 **Price Performance**
• Growth: {price_growth:+.1f}% over time
• Trend: {'📈 Bullish' if price_growth > 15 else '📉 Stable' if price_growth > 0 else '🐻 Bearish'}

💡 **Market Position**
{area} is in the {'premium' if avg_price > 8000000 else 'mid-range' if avg_price > 5000000 else 'affordable'} segment.
"""

def generate_demand_focused_summary(area, area_data, latest_data, avg_demand):
    """Generate summary focused on demand"""
    current_demand = latest_data['demand']
    demand_trend = "increasing" if current_demand > avg_demand else "decreasing" if current_demand < avg_demand else "stable"
    
    return f"""📊 **DEMAND ANALYSIS: {area.upper()}**

🔥 **Current Demand Level**
• Current: {current_demand}/10
• Average: {avg_demand:.1f}/10
• Trend: {demand_trend}

🎯 **Market Popularity**
• Status: {'🔥 Hot Market' if current_demand >= 8 else '📈 Growing' if current_demand >= 6 else '📊 Stable'}
• Competition: {'High' if current_demand >= 8 else 'Medium' if current_demand >= 6 else 'Low'}

💡 **Insight**
This area shows {demand_trend} market interest.
"""

def generate_growth_summary(area, area_data, price_growth):
    """Generate summary focused on growth trends"""
    yearly_growth = price_growth / len(area_data) if len(area_data) > 0 else 0
    
    return f"""📈 **GROWTH ANALYSIS: {area.upper()}**

🚀 **Performance Metrics**
• Total Growth: {price_growth:+.1f}%
• Annualized: {yearly_growth:+.1f}% per year
• Data Period: {len(area_data)} years

📊 **Growth Rating**
• Trend: {'🚀 Strong Growth' if price_growth > 20 else '📈 Moderate Growth' if price_growth > 10 else '📊 Stable'}
• Outlook: {'Positive' if price_growth > 15 else 'Neutral' if price_growth > 5 else 'Cautious'}

💡 **Investment Perspective**
This area has shown {price_growth:+.1f}% appreciation historically.
"""

def generate_investment_summary(area, area_data, price_growth, avg_demand):
    """Generate investment-focused summary"""
    investment_score = (price_growth * 0.6) + (avg_demand * 4)  # Simple scoring
    
    return f"""💼 **INVESTMENT ANALYSIS: {area.upper()}**

⭐ **Investment Score: {investment_score:.1f}/100**

📊 **Key Metrics**
• Price Growth: {price_growth:+.1f}%
• Demand Level: {avg_demand:.1f}/10
• Market Stability: {'High' if avg_demand >= 7 else 'Medium' if avg_demand >= 5 else 'Low'}

🎯 **Recommendation**
{'🏆 Excellent Opportunity' if investment_score > 70 else '📈 Good Potential' if investment_score > 50 else '📊 Consider Research'}

💡 **Why Invest Here?**
• Strong historical performance
• {avg_demand:.1f}/10 demand indicates good liquidity
• {price_growth:+.1f}% growth shows market confidence
"""

def generate_comprehensive_summary(area, area_data, latest_data, avg_price, avg_demand, price_growth, years_available):
    """Generate comprehensive area summary"""
    return f"""🏢 **COMPREHENSIVE ANALYSIS: {area.upper()}**

💰 **PRICING**
• Current: ₹{latest_data['price']:,.0f}
• Average: ₹{avg_price:,.0f}
• Growth: {price_growth:+.1f}%

📊 **DEMAND & POPULARITY**
• Current: {latest_data['demand']}/10
• Average: {avg_demand:.1f}/10
• Trend: {'📈 Rising' if latest_data['demand'] > avg_demand else '📉 Falling' if latest_data['demand'] < avg_demand else '➡️ Stable'}

📈 **MARKET INSIGHTS**
• Segment: {'Premium' if avg_price > 8000000 else 'Mid-range' if avg_price > 5000000 else 'Affordable'}
• Stability: {'High' if price_growth > 0 and avg_demand > 7 else 'Medium' if avg_demand > 5 else 'Volatile'}
• Data Coverage: {years_available} years

💡 **OVERVIEW**
{area} presents a {avg_demand:.1f}/10 demand market with {price_growth:+.1f}% historical growth, positioning it as a {avg_demand >= 7 and price_growth > 15 and 'high-potential' or avg_demand >= 5 and price_growth > 5 and 'stable' or 'developing'} real estate market.
"""

def get_recommendations():
    """Get area recommendations based on data"""
    areas_data = []
    for area in processor.get_all_areas():
        area_data = processor.df[processor.df['area'] == area]
        if not area_data.empty:
            avg_price = area_data['price'].mean()
            avg_demand = area_data['demand'].mean()
            latest_price = area_data.iloc[-1]['price']
            first_price = area_data.iloc[0]['price']
            growth = ((latest_price - first_price) / first_price) * 100
            
            # Simple scoring
            score = (growth * 0.4) + (avg_demand * 6)
            areas_data.append((area, score, growth, avg_demand, avg_price))
    
    # Sort by score
    areas_data.sort(key=lambda x: x[1], reverse=True)
    
    recommendations = []
    for area, score, growth, demand, price in areas_data[:3]:
        rec_text = f"• {area}: ₹{price:,.0f} avg | {growth:+.1f}% growth | {demand:.1f}/10 demand"
        recommendations.append(rec_text)
    
    return "\n".join(recommendations)

@api_view(['POST'])
def upload_file(request):
    file = request.FILES.get('file')
    if file:
        os.makedirs('media', exist_ok=True)
        file_path = os.path.join('media', file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        success = processor.load_data(file_path)
        if success:
            return Response({'message': 'File uploaded successfully'})
    
    return Response({'error': 'File upload failed'}, status=400)

@api_view(['GET'])
def get_areas(request):
    areas = processor.get_all_areas()
    return Response({'areas': areas})

@api_view(['GET'])
def test_connection(request):
    return Response({
        'status': 'success', 
        'message': 'Django API is working!',
        'data_available': True
    })