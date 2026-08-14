# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from northstar_chatbot import NorthstarSupportBot
from config import APP_CONFIG
import time
import os

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG["app_name"],
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    
    .chat-header {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Message containers */
    .chat-messages {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        height: 450px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    
    .user-message {
        background: #0073e6;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 5px 18px;
        max-width: 80%;
        float: right;
        clear: both;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .bot-message {
        background: white;
        color: #1a1a1a;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 5px;
        max-width: 80%;
        float: left;
        clear: both;
        margin: 8px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #6c757d;
        clear: both;
        display: block;
        margin: 2px 5px;
    }
    
    /* Quick reply buttons */
    .quick-reply-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin: 15px 0;
    }
    
    .quick-reply-btn {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 25px;
        padding: 10px 15px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        font-weight: 500;
    }
    
    .quick-reply-btn:hover {
        background: #0073e6;
        color: white;
        border-color: #0073e6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Input area */
    .input-container {
        background: white;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        display: flex;
        gap: 10px;
    }
    
    .input-container textarea {
        flex: 1;
        border: none;
        outline: none;
        resize: none;
        font-size: 1rem;
        padding: 10px;
        border-radius: 10px;
        background: #f8f9fa;
    }
    
    .input-container button {
        padding: 10px 30px;
        background: #0073e6;
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .input-container button:hover {
        background: #0056b3;
        transform: scale(1.02);
    }
    
    /* Metrics cards */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #0073e6;
        text-align: center;
    }
    
    /* Status indicator */
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    
    /* Chat bubble formatting */
    .message-content {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bot' not in st.session_state:
    st.session_state.bot = NorthstarSupportBot(data_dir=APP_CONFIG["data_dir"])
    st.session_state.messages = []
    st.session_state.conversation_count = 0
    st.session_state.deflection_stats = {
        "order_status": 0,
        "returns_refunds": 0,
        "stock_availability": 0,
        "total": 0
    }
    st.session_state.input_key = 0

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #0073e6;">🛍️ Northstar</h1>
        <p style="color: #6c757d;">Support Deflection MVP</p>
        <hr>
    </div>
    """, unsafe_allow_html=True)
    
    # Bot status
    st.markdown("### 🤖 Bot Status")
    st.markdown('<span class="status-online">● Online & Operational</span>', unsafe_allow_html=True)
    st.caption(f"Last active: {datetime.now().strftime('%H:%M:%S')}")
    
    # Analytics section
    st.markdown("---")
    st.markdown("### 📊 Deflection Analytics")
    
    analytics = st.session_state.bot.get_analytics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Total Deflected",
            value=analytics['tickets_deflected']['total'],
            delta=f"+{analytics['tickets_deflected']['total'] - st.session_state.deflection_stats['total']}" 
                  if st.session_state.deflection_stats['total'] > 0 else None
        )
    with col2:
        st.metric(
            label="Conversations",
            value=analytics['total_conversations']
        )
    
    # Intent breakdown
    intent_data = {
        'Category': ['Order Status', 'Returns/Refunds', 'Stock Availability'],
        'Deflections': [
            analytics['intents_handled']['order_status'],
            analytics['intents_handled']['returns_refunds'],
            analytics['intents_handled']['stock_availability']
        ]
    }
    
    if sum(intent_data['Deflections']) > 0:
        fig = px.pie(
            intent_data,
            values='Deflections',
            names='Category',
            title='Deflections by Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=300, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    st.session_state.deflection_stats = analytics['tickets_deflected']
    
    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.bot = NorthstarSupportBot(data_dir=APP_CONFIG["data_dir"])
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    
    if st.button("📋 View Go-Live Readiness", use_container_width=True):
        readiness_note = st.session_state.bot.get_golive_readiness()
        with st.expander("📄 Go-Live Readiness Note", expanded=True):
            st.text(readiness_note)
    
    if st.button("💾 Save Chat History", use_container_width=True):
        filepath = st.session_state.bot.save_conversation()
        st.success(f"✅ Chat history saved to: {filepath}")

# Main chat interface
st.markdown("""
<div style="text-align: center; padding: 10px 0 20px 0;">
    <h2>🤖 Northstar Support Assistant</h2>
    <p style="color: #6c757d;">Get instant answers about orders, returns, and stock availability</p>
</div>
""", unsafe_allow_html=True)

# Chat container
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        # Welcome message
        st.markdown("""
        <div style="margin-bottom: 15px;">
            <div class="bot-message">
                <b>👋 Welcome to Northstar Support!</b><br><br>
                I can help you with:<br>
                📦 <b>Order Status</b> - Track your orders<br>
                🔄 <b>Returns & Refunds</b> - Return items, check refund status<br>
                📊 <b>Stock Availability</b> - Check if products are in stock<br><br>
                Try asking me something or use the quick replies below!
            </div>
            <span class="timestamp">Assistant • Just now</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div class="user-message">
                        {msg['content']}
                    </div>
                    <span class="timestamp" style="text-align: right;">You • {msg['timestamp']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div class="bot-message">
                        {msg['content']}
                    </div>
                    <span class="timestamp">Assistant • {msg['timestamp']}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Quick replies
st.markdown("### 💡 Quick Suggestions")
cols = st.columns(4)

quick_replies = APP_CONFIG["quick_replies"]

for idx, (col, reply) in enumerate(zip(cols, quick_replies)):
    with col:
        if st.button(reply["label"], use_container_width=True, key=f"qr_{idx}"):
            st.session_state.quick_reply = reply["text"]
            st.rerun()

# Chat input
st.markdown("---")

# Handle quick reply
if 'quick_reply' in st.session_state and st.session_state.quick_reply:
    user_input = st.session_state.quick_reply
    st.session_state.quick_reply = None
else:
    user_input = st.text_area(
        "Type your message...",
        key=f"chat_input_{st.session_state.input_key}",
        label_visibility="collapsed",
        placeholder="Ask about your order, returns, or product availability...",
        max_chars=APP_CONFIG["max_message_length"],
        height=50
    )

col1, col2, col3 = st.columns([5, 1, 1])
with col2:
    send_button = st.button("🚀 Send", use_container_width=True, type="primary")
with col3:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.input_key += 1
        st.rerun()

# Process message
if send_button and user_input:
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().strftime('%H:%M')
    })
    
    # Get bot response
    with st.spinner("🤔 Thinking..."):
        response = st.session_state.bot.process_message(user_input)
        time.sleep(0.5)
    
    # Add bot response
    st.session_state.messages.append({
        'role': 'bot',
        'content': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })
    
    st.session_state.conversation_count += 1
    st.session_state.input_key += 1
    st.rerun()

# Additional features - Expandable sections
with st.expander("📊 Detailed Analytics", expanded=False):
    analytics = st.session_state.bot.get_analytics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Order Status", analytics['intents_handled']['order_status'])
    with col2:
        st.metric("Returns/Refunds", analytics['intents_handled']['returns_refunds'])
    with col3:
        st.metric("Stock Availability", analytics['intents_handled']['stock_availability'])
    with col4:
        st.metric("Total Handled", analytics['tickets_deflected']['total'])

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
    {APP_CONFIG['app_name']} v{APP_CONFIG['version']} • Powered by Python & Streamlit
    <br>
    <span style="font-size: 0.7rem;">© 2024 Northstar Retail Co. • Support Deflection MVP</span>
</div>
""", unsafe_allow_html=True)