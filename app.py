import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from config import SYSTEM_PROMPT
from tools import handle_tool_call
import torch
import asyncio

st.set_page_config(page_title="Customer Service Chatbot", layout="wide")


# Initialize model and chain
@st.cache_resource
def init_chain():
    try:
        model_name = "unsloth/Llama-3.1-8B"

        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            use_fast=True,
            padding_side="left",
            trust_remote_code=True  # Add this line
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,  # Add this line
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_4bit=True,
            use_cache=True,
        )

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.15,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

        llm = HuggingFacePipeline(pipeline=pipe)

        # Simplified prompt template
        template = """
        {system_prompt}
        
        Current conversation:
        {chat_history}
        Human: {human_input}
        Assistant: Let me help you with that request.
        """
        
        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input", "system_prompt"],
            template=template
        )

        # Initialize memory
        memory = ConversationBufferMemory(
            memory_key="chat_history", input_key="human_input"
        )

        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=True)

        return chain

    except Exception as e:
        st.error(f"Error initializing model: {str(e)}")
        raise e


def should_use_tool(input_text):
    """Check if the input requires a tool call"""
    tool_keywords = {
        'order': ['order', 'purchase', 'bought', '#'],
        'track': ['track', 'shipping', 'delivery', 'where'],
        'product': ['product', 'item', 'stock', 'price'],
        'faq': ['return', 'returns', 'warranty', 'policy', 'how to', 'faq', 'help'],
        'complaint': ['complain', 'complaint', 'issue', 'problem', 'wrong', 'bad']
    }
    
    input_lower = input_text.lower()
    
    # Special case for FAQ queries
    if any(kw in input_lower for kw in tool_keywords['faq']):
        return True
        
    return any(
        any(keyword in input_lower for keyword in keywords)
        for keywords in tool_keywords.values()
    )


# UI Components
def render_hero():
    st.title("24/7 Customer Support AI Assistant")
    st.write(
        "Get instant answers to your questions, track orders, and resolve issues - all through our intelligent chat interface."
    )


def render_features():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Instant Responses")
        st.write("Get immediate answers to your questions, 24/7.")

    with col2:
        st.subheader("Order Tracking")
        st.write("Track your orders and get real-time updates.")

    with col3:
        st.subheader("Product Information")
        st.write("Get detailed product info and availability.")


async def process_response(prompt, response):
    """Process the response and handle tool calls"""
    input_lower = prompt.lower()
    
    # Handle product queries
    if "product" in input_lower or any(pid in input_lower.upper() for pid in ["P1", "P2", "P3"]):
        # Extract product ID (P1, P2, P3)
        product_id = next((pid for pid in ["P1", "P2", "P3"] if pid in prompt.upper()), None)
        if product_id:
            return await handle_tool_call(
                f'<tool_call>{{"name": "getProductInfo", "arguments": {{"productId": "{product_id}"}}}}</tool_call>'
            )
    
    # Handle complaints/issues
    elif any(word in input_lower for word in ['complain', 'complaint', 'issue', 'problem']):
        priority = "high" if any(word in input_lower for word in ['urgent', 'immediately', 'asap']) else "normal"
        return await handle_tool_call(
            f'<tool_call>{{"name": "createTicket", "arguments": {{"issue": "{prompt}", "priority": "{priority}"}}}}</tool_call>'
        )
    
    # Direct tool routing based on input patterns
    elif "order" in input_lower and any(c.isdigit() for c in input_lower):
        order_id = ''.join(c for c in input_lower if c.isdigit())
        return await handle_tool_call(f'<tool_call>{{"name": "checkOrder", "arguments": {{"orderId": "{order_id}"}}}}</tool_call>')
    
    elif any(word in input_lower for word in ["return", "refund", "policy"]):
        return await handle_tool_call('<tool_call>{"name": "getFAQ", "arguments": {"topic": "returns"}}</tool_call>')
    
    elif "track" in input_lower or "shipping" in input_lower:
        if any(c.isdigit() for c in input_lower):
            tracking_id = ''.join(c for c in input_lower if c.isdigit())
            return await handle_tool_call(f'<tool_call>{{"name": "trackShipment", "arguments": {{"trackingId": "{tracking_id}"}}}}</tool_call>')
        return await handle_tool_call('<tool_call>{"name": "getFAQ", "arguments": {"topic": "shipping"}}</tool_call>')
    
    elif "warranty" in input_lower:
        return await handle_tool_call('<tool_call>{"name": "getFAQ", "arguments": {"topic": "warranty"}}</tool_call>')
    
    elif "<tool_call>" in response:
        return await handle_tool_call(response)
    
    return response


# Main chat interface
def chat_interface():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chain = init_chain()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if any(word in prompt.lower() for word in ['hello', 'hey']):
                    response = "Hello! Welcome to customer service. How can I help you today?"
                else:
                    # Add debug print
                    print(f"Processing input: {prompt}")
                    response = st.session_state.chain.predict(
                        human_input=prompt,
                        system_prompt=SYSTEM_PROMPT
                    )
                    print(f"Raw response: {response}")  # Debug print
                    response = asyncio.run(process_response(prompt, response))
                    print(f"Processed response: {response}")  # Debug print

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )


def main():
    render_hero()
    render_features()
    st.divider()
    chat_interface()


if __name__ == "__main__":
    main()
