# Customer Service Chatbot

An AI-powered customer service chatbot built with Streamlit and LangChain, using the Llama language model.

## Features

-   🤖 AI-powered responses using Llama 3.1 8B model
-   💬 Natural conversation handling
-   🛍️ Product information lookup
-   📦 Order status tracking
-   🚚 Shipment tracking
-   ❓ FAQ system
-   🎫 Support ticket creation
-   📊 Stock availability checking

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ifsvivek/CustomerChatbot
cd CustomerChatbot
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file:

```env
POSTGRES_URL=your_postgres_connection_string  # Optional, for database support
```

5. Create required directories:

```bash
mkdir -p data
```

## Project Structure

```
CustomerChatbot/
├── app.py              # Main Streamlit application
├── config.py           # Configuration and system prompts
├── tools.py           # Tool implementations
├── database.py        # Database utilities (optional)
├── requirements.txt   # Project dependencies
└── data/
    └── faqs.json      # FAQ data
```

## Available Tools

-   `checkOrder`: Check order status using order ID
-   `trackShipment`: Get shipping updates using tracking ID
-   `getProductInfo`: Get product details using product ID
-   `getFAQ`: Get FAQ information by topic
-   `createTicket`: Create support tickets
-   `checkAvailability`: Check product stock levels

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Access the chatbot at `http://localhost:8501`

3. Example interactions:

-   "What's my order status for #12345?"
-   "Tell me about product P1"
-   "I want to return my item"
-   "Track my shipment 789"
-   "I need to raise a complaint"

## Model Configuration

The chatbot uses the Llama 3.1 8B model with the following settings:

-   4-bit quantization for efficient memory usage
-   Maximum token length: 256
-   Temperature: 0.7
-   Top-p: 0.95
-   Repetition penalty: 1.15

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
