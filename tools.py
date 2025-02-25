import json
import random
import os
import re


def load_faq_data():
    try:
        faq_path = os.path.join(os.path.dirname(__file__), "data", "faqs.json")
        with open(faq_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading FAQ data: {e}")
        return {}


async def handle_tool_call(response):
    try:
        pattern = r'<tool_call>(.*?)</tool_call>'
        match = re.search(pattern, response, re.DOTALL)
        
        if not match:
            return response
            
        tool_call_str = match.group(1).strip()
        print(f"Processing tool call: {tool_call_str}")
        
        tool_call = json.loads(tool_call_str)
        tool_name = tool_call.get('name', '').strip()
        args = tool_call.get('arguments', {})
        
        if tool_name not in TOOL_ACTIONS:
            print(f"Unknown tool requested: {tool_name}")
            return "I couldn't process that request. Please try asking in a different way."
            
        result = await TOOL_ACTIONS[tool_name](**args)
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return "I had trouble understanding that request. Could you rephrase it?"
    except Exception as e:
        print(f"Tool execution error: {e}")
        return "I encountered an error. Please try again or rephrase your request."


async def check_order(orderId):
    statuses = ["processing", "shipped", "delivered", "pending"]
    return f"Order #{orderId} is currently {random.choice(statuses)}"


async def track_shipment(trackingId):
    locations = ["warehouse", "in transit", "local facility", "out for delivery"]
    return f"Tracking #{trackingId} - Package is {random.choice(locations)}"


async def get_product_info(productId):
    products = {
        "P1": "Premium Widget - $99.99 (50 in stock)",
        "P2": "Basic Widget - $49.99 (100 in stock)",
        "P3": "Super Widget - $149.99 (25 in stock)",
    }
    return products.get(productId, "Product not found")


async def get_faq(topic):
    faq_data = load_faq_data()
    clean_topic = topic.lower().strip()
    
    # Normalize topic variations
    topic_mapping = {
        'return': 'returns',
        'refund': 'returns',
        'shipping': 'shipping',
        'delivery': 'shipping',
        'warranty': 'warranty',
        'payment': 'payment',
        'order': 'order_status',
        'contact': 'contact'
    }
    
    for key, value in topic_mapping.items():
        if key in clean_topic:
            clean_topic = value
            break
    
    return faq_data.get(
        clean_topic,
        "I couldn't find information about that topic. Please try asking about returns, shipping, warranty, payment methods, or order status."
    )


async def create_ticket(issue, priority):
    ticket_id = random.randint(1000, 9999)
    return f"Ticket #{ticket_id} created for: {issue} (Priority: {priority})"


async def check_availability(productId):
    stock = random.randint(0, 100)
    return f"Product {productId} has {stock} units in stock"


# Register all available tools
TOOL_ACTIONS = {
    "checkOrder": check_order,
    "trackShipment": track_shipment,
    "getProductInfo": get_product_info,
    "getFAQ": get_faq,
    "createTicket": create_ticket,
    "checkAvailability": check_availability,
}
