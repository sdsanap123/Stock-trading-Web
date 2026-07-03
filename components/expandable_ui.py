#!/usr/bin/env python3
"""
Expandable UI Components
Reusable UI components for displaying data in expandable rows with + icons.
"""

import streamlit as st
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class ModalWindow:
    """Custom modal window component for Streamlit."""
    
    @staticmethod
    def create_modal(modal_id: str, title: str, content: str, width: str = "80%", height: str = "80%"):
        """Create a modal window with HTML/CSS/JavaScript."""
        modal_html = f"""
        <div id="{modal_id}" class="modal" style="display: none;">
            <div class="modal-content" style="width: {width}; height: {height};">
                <div class="modal-header">
                    <h2>{title}</h2>
                    <span class="close" onclick="closeModal('{modal_id}')">&times;</span>
                </div>
                <div class="modal-body">
                    {content}
                </div>
            </div>
        </div>
        
        <style>
        .modal {{
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }}
        
        .modal-content {{
            background-color: #1e1e1e;
            margin: 5% auto;
            padding: 0;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border: 1px solid #333;
            max-height: 90vh;
            overflow: hidden;
        }}
        
        .modal-header {{
            background-color: #2d2d2d;
            padding: 15px 20px;
            border-bottom: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .modal-header h2 {{
            margin: 0;
            color: #ffffff;
            font-size: 1.5rem;
        }}
        
        .close {{
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s;
        }}
        
        .close:hover {{
            color: #ffffff;
        }}
        
        .modal-body {{
            padding: 20px;
            max-height: calc(90vh - 80px);
            overflow-y: auto;
            color: #ffffff;
        }}
        
        .modal-body h3 {{
            color: #4CAF50;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        .modal-body p {{
            margin: 8px 0;
            line-height: 1.5;
        }}
        
        .modal-body .metric {{
            background-color: #2d2d2d;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            border-left: 3px solid #4CAF50;
        }}
        </style>
        
        <script>
        function openModal(modalId) {{
            document.getElementById(modalId).style.display = "block";
            document.body.style.overflow = "hidden";
        }}
        
        function closeModal(modalId) {{
            document.getElementById(modalId).style.display = "none";
            document.body.style.overflow = "auto";
        }}
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {{
            var modals = document.querySelectorAll('.modal');
            modals.forEach(function(modal) {{
                if (event.target == modal) {{
                    modal.style.display = "none";
                    document.body.style.overflow = "auto";
                }}
            }});
        }}
        </script>
        """
        return modal_html
    
    @staticmethod
    def show_modal_button(button_text: str, modal_id: str, title: str, content: str):
        """Show a button that opens a wide modal-like display."""
        # Create a unique key for the button
        button_key = f"modal_btn_{modal_id}"
        
        # Use Streamlit button with session state
        if st.button(f"🔍 {button_text}", key=button_key, help="Click to view details in a wide popup"):
            # Store the modal data in session state
            st.session_state[f"show_modal_{modal_id}"] = True
            st.session_state[f"modal_title_{modal_id}"] = title
            st.session_state[f"modal_content_{modal_id}"] = content
        
        # Show wide modal if triggered
        if st.session_state.get(f"show_modal_{modal_id}", False):
            # Create a wide popup-like container
            st.markdown("---")
            
            # Add custom CSS for popup styling
            st.markdown("""
            <style>
            .popup-container {
                background-color: #1e1e1e;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }
            .popup-header {
                background-color: #2d2d2d;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #4CAF50;
            }
            .popup-content {
                background-color: #2a2a2a;
                padding: 15px;
                border-radius: 8px;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create the popup container
            with st.container():
                st.markdown(f"""
                <div class="popup-container">
                    <div class="popup-header">
                        <h2 style="color: #4CAF50; margin: 0;">{title}</h2>
                    </div>
                    <div class="popup-content">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Close button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("❌ Close Details", key=f"close_{modal_id}", help="Close this popup"):
                        st.session_state[f"show_modal_{modal_id}"] = False
                        st.rerun()
            
            st.markdown("---")
    
    @staticmethod
    def show_full_width_modal(button_text: str, modal_id: str, title: str, content: str):
        """Show a full-width modal that takes up most of the screen."""
        # Create a unique key for the button
        button_key = f"full_modal_btn_{modal_id}"
        
        # Use Streamlit button with session state
        if st.button(f"🔍 {button_text}", key=button_key, help="Click to view details in full width"):
            # Store the modal data in session state
            st.session_state[f"show_full_modal_{modal_id}"] = True
            st.session_state[f"full_modal_title_{modal_id}"] = title
            st.session_state[f"full_modal_content_{modal_id}"] = content
        
        # Show full-width modal if triggered
        if st.session_state.get(f"show_full_modal_{modal_id}", False):
            # Create a full-width popup-like container
            st.markdown("---")
            
            # Add custom CSS for full-width popup styling
            st.markdown("""
            <style>
            .full-popup-container {
                background-color: #1e1e1e;
                border: 3px solid #4CAF50;
                border-radius: 15px;
                padding: 25px;
                margin: 15px 0;
                box-shadow: 0 8px 30px rgba(0,0,0,0.5);
                width: 100%;
            }
            .full-popup-header {
                background-color: #2d2d2d;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 6px solid #4CAF50;
                text-align: center;
            }
            .full-popup-content {
                background-color: #2a2a2a;
                padding: 20px;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                line-height: 1.6;
            }
            .close-button {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
            .close-button:hover {
                background-color: #c82333;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create the full-width popup container
            with st.container():
                st.markdown(f"""
                <div class="full-popup-container">
                    <div class="full-popup-header">
                        <h1 style="color: #4CAF50; margin: 0; font-size: 2rem;">{title}</h1>
                    </div>
                    <div class="full-popup-content">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Close button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("❌ Close Full Details", key=f"close_full_{modal_id}", help="Close this full-width popup", type="primary"):
                        st.session_state[f"show_full_modal_{modal_id}"] = False
                        st.rerun()
            
            st.markdown("---")
    
    @staticmethod
    def show_popup_window(button_text: str, modal_id: str, title: str, content: str):
        """Show a button that opens a new browser window popup."""
        # Create a unique key for the button
        button_key = f"popup_btn_{modal_id}"
        
        # Create HTML content for popup window
        popup_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #1e1e1e;
                    color: white;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: #2d2d2d;
                    padding: 20px;
                    border-radius: 10px;
                    border: 2px solid #4CAF50;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .content {{
                    background-color: #2a2a2a;
                    padding: 20px;
                    border-radius: 8px;
                    line-height: 1.6;
                }}
                .close-btn {{
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 20px auto;
                    display: block;
                }}
                .close-btn:hover {{
                    background-color: #c82333;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    {content}
                </div>
                <button class="close-btn" onclick="window.close()">Close Window</button>
            </div>
        </body>
        </html>
        """
        
        # Encode the HTML content for URL
        import base64
        import urllib.parse
        encoded_html = base64.b64encode(popup_html.encode()).decode()
        
        # Create the popup button with JavaScript
        popup_script = f"""
        <script>
        function openPopup{modal_id}() {{
            var popup = window.open('', 'popup_{modal_id}', 'width=1200,height=800,scrollbars=yes,resizable=yes');
            popup.document.write(atob('{encoded_html}'));
            popup.document.close();
        }}
        </script>
        <button onclick="openPopup{modal_id}()" 
                style="background-color: #4CAF50; 
                       color: white; 
                       border: none; 
                       padding: 8px 16px; 
                       text-align: center; 
                       text-decoration: none; 
                       display: inline-block; 
                       font-size: 14px; 
                       margin: 4px 2px; 
                       cursor: pointer; 
                       border-radius: 4px;
                       transition: background-color 0.3s;">
            🪟 {button_text}
        </button>
        """
        
        st.markdown(popup_script, unsafe_allow_html=True)

class ExpandableUI:
    """Reusable expandable UI components for data display."""
    
    @staticmethod
    def display_news_row(article: Dict, index: int) -> bool:
        """Display a news article in an expandable row format."""
        try:
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            published = article.get('publishedAt', 'Unknown')
            sentiment = article.get('sentiment', 0)
            
            # Truncate title for display
            display_title = title[:60] + "..." if len(title) > 60 else title
            
            # Format published date
            try:
                if published and published != 'Unknown':
                    # Try to parse and format the date
                    from datetime import datetime
                    if 'T' in published:
                        date_obj = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%m/%d %H:%M')
                    else:
                        formatted_date = published[:10]
                else:
                    formatted_date = 'N/A'
            except:
                formatted_date = published[:10] if published else 'N/A'
            
            # Create main row
            col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1, 1, 0.8])
            
            with col1:
                st.write(f"**{display_title}**")
            
            with col2:
                st.write(source)
            
            with col3:
                st.write(formatted_date)
            
            with col4:
                # Sentiment with color
                if sentiment > 0.1:
                    st.markdown(f'<span style="color: #28a745;">+{sentiment:.2f}</span>', unsafe_allow_html=True)
                elif sentiment < -0.1:
                    st.markdown(f'<span style="color: #dc3545;">{sentiment:.2f}</span>', unsafe_allow_html=True)
                else:
                    st.write(f"{sentiment:.2f}")
            
            with col5:
                # Provide multiple viewing options
                modal_id = f"news_modal_{index}"
                modal_title = f"News Details - {article.get('title', 'Unknown')[:50]}..."
                modal_content = ExpandableUI._get_news_details_html(article)
                
                # Show both full-width modal and popup window options
                col5a, col5b = st.columns(2)
                with col5a:
                    ModalWindow.show_full_width_modal("📱 Wide View", modal_id, modal_title, modal_content)
                with col5b:
                    ModalWindow.show_popup_window("🪟 New Window", modal_id, modal_title, modal_content)
            
            return False
            
        except Exception as e:
            logger.error(f"Error displaying news row: {str(e)}")
            return False
    
    @staticmethod
    def _get_news_details_html(article: Dict) -> str:
        """Get HTML content for news details modal."""
        try:
            title = article.get('title', 'N/A')
            source = article.get('source', 'N/A')
            published = article.get('publishedAt', 'N/A')
            url = article.get('url', 'N/A')
            description = article.get('description', 'No description available')
            sentiment = article.get('sentiment', 0)
            
            # Format sentiment
            if sentiment > 0.1:
                sentiment_html = f'<span style="color: #28a745;">Positive ({sentiment:.3f})</span>'
            elif sentiment < -0.1:
                sentiment_html = f'<span style="color: #dc3545;">Negative ({sentiment:.3f})</span>'
            else:
                sentiment_html = f'<span style="color: #ffc107;">Neutral ({sentiment:.3f})</span>'
            
            html_content = f"""
            <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                    <h3>📰 Article Details</h3>
                    <div class="metric">
                        <p><strong>Title:</strong> {title}</p>
                        <p><strong>Source:</strong> {source}</p>
                        <p><strong>Published:</strong> {published}</p>
                        <p><strong>URL:</strong> <a href="{url}" target="_blank" style="color: #4CAF50;">{url}</a></p>
                        <p><strong>Sentiment:</strong> {sentiment_html}</p>
                    </div>
                </div>
                <div style="flex: 1;">
                    <h3>📝 Content</h3>
                    <div class="metric">
                        <p>{description}</p>
                    </div>
                </div>
            </div>
            """
            
            if url and url != 'N/A':
                html_content += f"""
                <div style="margin-top: 20px;">
                    <h3>🔗 Full Article</h3>
                    <p><a href="{url}" target="_blank" style="color: #4CAF50; text-decoration: none; font-weight: bold;">Read Full Article →</a></p>
                </div>
                """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating news details HTML: {str(e)}")
            return "<p>Error loading details</p>"
    
    @staticmethod
    def _display_news_details(article: Dict):
        """Display detailed news article information."""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📰 Article Details**")
                st.write(f"• **Title:** {article.get('title', 'N/A')}")
                st.write(f"• **Source:** {article.get('source', 'N/A')}")
                st.write(f"• **Published:** {article.get('publishedAt', 'N/A')}")
                st.write(f"• **URL:** {article.get('url', 'N/A')}")
                
                # Sentiment analysis
                sentiment = article.get('sentiment', 0)
                if sentiment > 0.1:
                    st.markdown(f"• **Sentiment:** <span style='color: #28a745;'>Positive ({sentiment:.3f})</span>", unsafe_allow_html=True)
                elif sentiment < -0.1:
                    st.markdown(f"• **Sentiment:** <span style='color: #dc3545;'>Negative ({sentiment:.3f})</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"• **Sentiment:** <span style='color: #ffc107;'>Neutral ({sentiment:.3f})</span>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📝 Content**")
                description = article.get('description', 'No description available')
                if description:
                    st.write(description)
                else:
                    st.write("No description available")
            
            # Full article link
            if article.get('url'):
                st.markdown("**🔗 Full Article**")
                st.markdown(f"[Read Full Article]({article['url']})")
            
        except Exception as e:
            logger.error(f"Error displaying news details: {str(e)}")
    
    @staticmethod
    def display_recommendation_row(rec: Dict, index: int, show_actions: bool = True) -> bool:
        """Display a recommendation in an expandable row format."""
        try:
            symbol = rec.get('symbol', 'UNKNOWN')
            company_name = rec.get('company_name', '')
            current_price = rec.get('current_price', 0)
            recommendation = rec.get('recommendation', '')
            confidence = rec.get('confidence', 0)
            target_price = rec.get('target_price', 0)
            stop_loss = rec.get('stop_loss', 0)
            created_at = rec.get('created_at', '')
            
            # Format entry date
            try:
                if created_at:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d-%m-%Y')  # Format as DD-MM-YYYY
                else:
                    formatted_date = 'N/A'
            except Exception as e:
                logger.warning(f"Error formatting date: {str(e)}")
                formatted_date = 'N/A'
            
            # Create main row with 7 columns to match the header
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 1, 1, 1, 1, 0.8, 0.8])
            
            with col1:
                badge_color = '#28a745' if recommendation == 'BUY' else '#dc3545' if recommendation == 'SELL' else '#ffc107'
                badge_label = '📈 BUY' if recommendation == 'BUY' else '📉 SELL' if recommendation == 'SELL' else '➡️ HOLD'
                st.markdown(
                    f'<div style="font-weight:bold; font-size:0.95rem;">{symbol}</div>'
                    f'<div style="display:inline-block; background:{badge_color}; color:#fff; '
                    f'border-radius:4px; padding:1px 7px; font-size:0.75rem; margin-top:2px;">'
                    f'{badge_label}</div>',
                    unsafe_allow_html=True
                )
                if company_name:
                    st.caption(company_name)
            
            with col2:
                st.write(f"₹{current_price:.2f}")
            
            with col3:
                st.write(f"{confidence:.1f}%")
            
            with col4:
                st.write(f"₹{target_price:.2f}")
            
            with col5:
                st.write(f"₹{stop_loss:.2f}")
            
            # Details column with View Details button
            with col6:
                # Create a unique key for the expander
                expander_key = f"expander_{index}"
                
                # Create a button to toggle the expander
                if st.button("🔍 Details", key=f"btn_{expander_key}", 
                           help="View detailed analysis"):
                    # Toggle the expander state in session state
                    if f"expanded_{expander_key}" in st.session_state:
                        st.session_state[f"expanded_{expander_key}"] = not st.session_state[f"expanded_{expander_key}"]
                    else:
                        st.session_state[f"expanded_{expander_key}"] = True
            
            # Actions column with Add to Watchlist button
            with col7:
                if st.button("👁️", 
                           key=f"watchlist_btn_{index}",
                           help="Add to Watchlist"):
                    # This will be handled by the parent component
                    st.session_state[f"add_to_watchlist_{index}"] = True
            
            # Show the expander if it's toggled on
            if st.session_state.get(f"expanded_{expander_key}", False):
                # Use container to create a modal-like appearance
                with st.container():
                    # Create a header with a close button
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown(f"### {symbol} - Detailed Analysis")
                    with col2:
                        if st.button("✕", key=f"close_{expander_key}"):
                            st.session_state[f"expanded_{expander_key}"] = False
                            st.rerun()
                    
                    # Add a divider
                    st.markdown("---")
                    
                    # Display the detailed content
                    ExpandableUI._display_recommendation_details(rec)
                    
                    # Add some spacing and a close button at the bottom
                    st.markdown("")
                    if st.button("Close Details", key=f"close_btn_{expander_key}"):
                        st.session_state[f"expanded_{expander_key}"] = False
                        st.rerun()
            
            return False
            
        except Exception as e:
            logger.error(f"Error displaying recommendation row: {str(e)}")
            return False
    
    @staticmethod
    def _get_recommendation_details_html(rec: Dict) -> str:
        """Get HTML content for recommendation details modal."""
        try:
            symbol = rec.get('symbol', 'N/A')
            current_price = rec.get('current_price', 0)
            target_price = rec.get('target_price', 0)
            stop_loss = rec.get('stop_loss', 0)
            confidence = rec.get('confidence', 0)
            recommendation = rec.get('recommendation', 'N/A')
            reasoning = rec.get('reasoning', '')
            swing_plan = rec.get('swing_plan', {})
            technical_data = rec.get('technical_data', {})
            groq_analysis = rec.get('groq_analysis', {})
            gemini_analysis = rec.get('gemini_analysis', {})
            
            # Calculate risk-reward ratio
            risk_reward_html = ""
            if current_price > 0 and target_price > 0 and stop_loss > 0:
                potential_profit = target_price - current_price
                potential_loss = current_price - stop_loss
                if potential_loss > 0:
                    risk_reward = potential_profit / potential_loss
                    risk_reward_html = f"<p><strong>Risk-Reward Ratio:</strong> {risk_reward:.2f}:1</p>"
            
            # Recommendation color
            rec_color = "#28a745" if recommendation == "BUY" else "#dc3545" if recommendation == "SELL" else "#ffc107"
            
            html_content = f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1;">
                    <h3>📊 Trading Details</h3>
                    <div class="metric">
                        <p><strong>Symbol:</strong> {symbol}</p>
                        <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
                        <p><strong>Target Price:</strong> ₹{target_price:.2f}</p>
                        <p><strong>Stop Loss:</strong> ₹{stop_loss:.2f}</p>
                        <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                        <p><strong>Recommendation:</strong> <span style="color: {rec_color}; font-weight: bold;">{recommendation}</span></p>
                        {risk_reward_html}
                    </div>
                </div>
                <div style="flex: 1;">
                    <h3>📈 Swing Trading Plan</h3>
                    <div class="metric">
            """
            
            if swing_plan:
                html_content += f"""
                        <p><strong>Position Size:</strong> {swing_plan.get('position_size', 0)} shares</p>
                        <p><strong>Investment:</strong> ₹{swing_plan.get('investment_amount', 0):,.0f}</p>
                        <p><strong>Risk Amount:</strong> ₹{swing_plan.get('risk_amount', 0):,.0f}</p>
                        <p><strong>Holding Period:</strong> {swing_plan.get('holding_period_days', 7)} days</p>
                """
            else:
                html_content += "<p>No swing plan available</p>"
            
            html_content += """
                    </div>
                </div>
            </div>
            """
            
            # AI Reasoning
            if reasoning:
                html_content += f"""
                <div style="margin-bottom: 20px;">
                    <h3>💭 AI Reasoning</h3>
                    <div class="metric">
                        <p>{reasoning}</p>
                    </div>
                </div>
                """
            
            # Technical Analysis
            if technical_data:
                html_content += """
                <div style="margin-bottom: 20px;">
                    <h3>📊 Technical Indicators</h3>
                    <div style="display: flex; gap: 20px;">
                        <div style="flex: 1;">
                            <div class="metric">
                """
                html_content += f"""
                                <p><strong>RSI:</strong> {technical_data.get('rsi', 0):.1f}</p>
                                <p><strong>MACD:</strong> {technical_data.get('macd', 0):.4f}</p>
                                <p><strong>SMA 20:</strong> ₹{technical_data.get('sma_20', 0):.2f}</p>
                """
                html_content += """
                            </div>
                        </div>
                        <div style="flex: 1;">
                            <div class="metric">
                """
                html_content += f"""
                                <p><strong>Volume Ratio:</strong> {technical_data.get('volume_ratio_20', 0):.2f}</p>
                                <p><strong>ATR:</strong> ₹{technical_data.get('atr', 0):.2f}</p>
                                <p><strong>Bollinger Position:</strong> {technical_data.get('bb_position', 0):.2f}</p>
                """
                html_content += """
                            </div>
                        </div>
                    </div>
                </div>
                """
            
            # AI Analysis (Groq and/or Gemini)
            has_groq = groq_analysis and groq_analysis.get('status') == 'success'
            has_gemini = gemini_analysis and gemini_analysis.get('status') == 'success'

            if has_groq or has_gemini:
                providers = []
                if has_groq:
                    providers.append("Groq AI")
                if has_gemini:
                    providers.append("Gemini AI")
                providers_text = " and ".join(providers)

                html_content += """
                <div style="margin-bottom: 20px;">
                    <h3>🤖 AI Analysis</h3>
                    <div class="metric">
                """

                # High-level fields from Groq
                if has_groq:
                    sentiment_label = groq_analysis.get('sentiment_label', 'N/A')
                    impact_level = groq_analysis.get('impact_level', 'N/A')
                    price_impact = groq_analysis.get('price_impact', 'N/A')
                    swing_potential = groq_analysis.get('swing_trading_potential', 'N/A')

                    html_content += f"""
                        <p><strong>Primary AI:</strong> {providers_text}</p>
                        <p><strong>Sentiment:</strong> {sentiment_label}</p>
                        <p><strong>Impact Level:</strong> {impact_level}</p>
                        <p><strong>Price Impact:</strong> {price_impact}</p>
                        <p><strong>Swing Potential:</strong> {swing_potential}</p>
                    """

                    # Optional news snippet used for sentiment (if present)
                    news_snippet = (
                        groq_analysis.get('news_snippet')
                        or groq_analysis.get('headline')
                        or groq_analysis.get('summary')
                        or ""
                    )
                    if news_snippet:
                        html_content += f"""
                        <p><strong>News context:</strong> {news_snippet}</p>
                        """

                # Additional Gemini summary if available
                if has_gemini:
                    gem_data = gemini_analysis.get('analysis', {})
                    gem_score = gem_data.get('overall_score', 0)
                    gem_conf = gem_data.get('confidence', 0)
                    gem_reco = gem_data.get('recommendation', 'N/A')
                    html_content += f"""
                        <p><strong>Gemini View:</strong> {gem_reco} (score {gem_score:.2f}, confidence {gem_conf:.1%})</p>
                    """

                html_content += """
                    </div>
                </div>
                """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating recommendation details HTML: {str(e)}")
            return "<p>Error loading details</p>"
    
    @staticmethod
    def _display_recommendation_details(rec: Dict):
        """Display detailed recommendation information."""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Trading Details**")
                st.write(f"• **Current Price:** ₹{rec.get('current_price', 0):.2f}")
                st.write(f"• **Target Price:** ₹{rec.get('target_price', 0):.2f}")
                st.write(f"• **Stop Loss:** ₹{rec.get('stop_loss', 0):.2f}")
                st.write(f"• **Confidence:** {rec.get('confidence', 0):.1f}%")
                
                # Risk-Reward Ratio
                current_price = rec.get('current_price', 0)
                target_price = rec.get('target_price', 0)
                stop_loss = rec.get('stop_loss', 0)
                
                if current_price > 0 and target_price > 0 and stop_loss > 0:
                    potential_profit = target_price - current_price
                    potential_loss = current_price - stop_loss
                    if potential_loss > 0:
                        risk_reward = potential_profit / potential_loss
                        st.write(f"• **Risk-Reward Ratio:** {risk_reward:.2f}:1")
            
            with col2:
                st.markdown("**📈 Swing Trading Plan**")
                swing_plan = rec.get('swing_plan', {})
                if swing_plan:
                    st.write(f"• **Position Size:** {swing_plan.get('position_size', 0)} shares")
                    st.write(f"• **Investment:** ₹{swing_plan.get('investment_amount', 0):,.0f}")
                    st.write(f"• **Risk Amount:** ₹{swing_plan.get('risk_amount', 0):,.0f}")
                    st.write(f"• **Holding Period:** {swing_plan.get('holding_period_days', 7)} days")
                else:
                    st.write("No swing plan available")
            
            # Reasoning
            reasoning = rec.get('reasoning', '')
            if reasoning:
                st.markdown("**💭 AI Reasoning**")
                st.markdown(reasoning)
            
            # Technical Analysis
            technical_data = rec.get('technical_data', {})
            if technical_data:
                st.markdown("**📊 Technical Indicators**")
                tech_col1, tech_col2 = st.columns(2)
                
                with tech_col1:
                    st.write(f"• **RSI:** {technical_data.get('rsi', 0):.1f}")
                    st.write(f"• **MACD:** {technical_data.get('macd', 0):.4f}")
                    st.write(f"• **SMA 20:** ₹{technical_data.get('sma_20', 0):.2f}")
                
                with tech_col2:
                    st.write(f"• **Volume Ratio:** {technical_data.get('volume_ratio_20', 0):.2f}")
                    st.write(f"• **ATR:** ₹{technical_data.get('atr', 0):.2f}")
                    st.write(f"• **Bollinger Position:** {technical_data.get('bb_position', 0):.2f}")
            
            # Groq Analysis
            groq_analysis = rec.get('groq_analysis', {})
            if groq_analysis:
                st.markdown("**🤖 Groq AI Analysis**")
                
                # Debug: Print the structure of groq_analysis
                if 'status' in groq_analysis and groq_analysis['status'] == 'error':
                    st.warning(f"Analysis error: {groq_analysis.get('message', 'Unknown error')}")
                    return
                
                # Check if we have a direct analysis result
                if 'recommendation' in groq_analysis:
                    # This is a direct analysis result
                    st.write(f"• **Recommendation:** {groq_analysis.get('recommendation', 'N/A')}")
                    st.write(f"• **Confidence:** {float(groq_analysis.get('confidence', 0)) * 100:.1f}%")
                    st.write(f"• **Price Target:** ₹{groq_analysis.get('price_target', 'N/A')}")
                    st.write(f"• **Stop Loss:** ₹{groq_analysis.get('stop_loss', 'N/A')}")
                    
                    # Show sentiment if available
                    if 'sentiment' in groq_analysis:
                        st.write(f"• **Sentiment:** {groq_analysis.get('sentiment', 'N/A')}")
                    
                    # Show time horizon if available
                    if 'time_horizon' in groq_analysis:
                        st.write(f"• **Time Horizon:** {groq_analysis.get('time_horizon', 'N/A')}")
                
                # Check if we have stocks array format
                elif 'stocks' in groq_analysis and isinstance(groq_analysis['stocks'], list) and groq_analysis['stocks']:
                    # Use the first stock's analysis
                    stock_analysis = groq_analysis['stocks'][0]
                    st.write(f"• **Sentiment:** {stock_analysis.get('sentiment_label', stock_analysis.get('sentiment', 'N/A'))}")
                    st.write(f"• **Impact Level:** {stock_analysis.get('impact_level', 'N/A')}")
                    st.write(f"• **Price Impact:** {stock_analysis.get('price_impact', 'N/A')}")
                    st.write(f"• **Swing Potential:** {stock_analysis.get('swing_trading_potential', stock_analysis.get('swing_potential', 'N/A'))}")
                    if 'confidence' in stock_analysis:
                        st.write(f"• **Confidence:** {float(stock_analysis.get('confidence', 0)) * 100:.1f}%")
                
                # Fallback to direct attributes if available
                elif any(key in groq_analysis for key in ['sentiment', 'sentiment_label', 'impact_level', 'price_impact']):
                    st.write(f"• **Sentiment:** {groq_analysis.get('sentiment_label', groq_analysis.get('sentiment', 'N/A'))}")
                    st.write(f"• **Impact Level:** {groq_analysis.get('impact_level', 'N/A')}")
                    st.write(f"• **Price Impact:** {groq_analysis.get('price_impact', 'N/A')}")
                    st.write(f"• **Swing Potential:** {groq_analysis.get('swing_trading_potential', groq_analysis.get('swing_potential', 'N/A'))}")
                    if 'confidence' in groq_analysis:
                        st.write(f"• **Confidence:** {float(groq_analysis.get('confidence', 0)) * 100:.1f}%")
                
                # Display the unstructured AI analysis if available
                if 'analysis' in groq_analysis and isinstance(groq_analysis['analysis'], str):
                    st.markdown("---")
                    st.markdown("#### 📝 Groq AI Analysis Summary")
                    st.markdown(groq_analysis['analysis'])
                # Handle case where analysis is in a different field or format
                elif any(key in groq_analysis for key in ['summary', 'analysis_text', 'detailed_analysis']):
                    analysis_text = next((groq_analysis[key] for key in ['summary', 'analysis_text', 'detailed_analysis'] 
                                       if key in groq_analysis), None)
                    if analysis_text and isinstance(analysis_text, str):
                        st.markdown("---")
                        st.markdown("#### 📝 Groq AI Analysis Summary")
                        st.markdown(analysis_text)
                
                # If no structured data was found, show a warning
                if not any(key in groq_analysis for key in ['recommendation', 'stocks', 'sentiment', 'analysis', 'summary', 'analysis_text', 'detailed_analysis']):
                    st.warning("No detailed analysis data available. The Groq API might not be properly configured or returned an empty response.")
                    
                    # Debug: Show the actual structure of groq_analysis
                    if st.checkbox("Show raw analysis data (for debugging)"):
                        st.json(groq_analysis)
            
        except Exception as e:
            logger.error(f"Error displaying recommendation details: {str(e)}")
    
    @staticmethod
    def display_watchlist_row(item: Dict, index: int, show_actions: bool = True) -> bool:
        """Display a watchlist item in an expandable row format with selection checkbox."""
        try:
            # Add compact styling
            st.markdown("""
            <style>
                .compact-row {
                    line-height: 1 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .compact-row .stMarkdown {
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .compact-row .stMarkdown p {
                    margin: 0 !important;
                    padding: 0 !important;
                    line-height: 1.1 !important;
                }
                .stButton>button {
                    min-height: 1.5rem !important;
                    height: 1.5rem !important;
                    padding: 0 0.5rem !important;
                    margin: 0 !important;
                }
                .stButton {
                    line-height: 1 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                [data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            symbol = item.get('symbol', 'UNKNOWN')
            company_name = item.get('company_name', '')
            current_price = item.get('current_price', 0)
            entry_price = item.get('entry_price', 0)
            target_price = item.get('target_price', 0)
            stop_loss = item.get('stop_loss', 0)
            status = item.get('status', 'ACTIVE')
            added_date = item.get('added_date', '')
            
            # Calculate P&L
            if entry_price > 0:
                pnl = ((current_price - entry_price) / entry_price) * 100
                pnl_amount = current_price - entry_price
            else:
                pnl = 0
                pnl_amount = 0
            
            # Format date
            try:
                if added_date:
                    date_obj = datetime.fromisoformat(added_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                else:
                    formatted_date = 'N/A'
            except:
                formatted_date = added_date[:10] if added_date else 'N/A'
            
            # Create main row - more compact with headers
            # Column layout (11 columns): [Select] [Stock] [Date] [Current] [Entry] [S/L] [P&L] [Target] [Status] [Details] [X]
            if index == 0:
                # Add header row with adjusted column widths to match data rows
                header_cols = st.columns([0.5, 1.2, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.6, 0.5])
                with header_cols[0]:
                    st.markdown("**✔**")
                with header_cols[1]: st.markdown("**Stock**")
                with header_cols[2]: st.markdown("<div style='text-align: center;'>**Date**</div>", unsafe_allow_html=True)
                with header_cols[3]: st.markdown("<div style='text-align: right;'>**Current**</div>", unsafe_allow_html=True)
                with header_cols[4]: st.markdown("<div style='text-align: right;'>**Entry**</div>", unsafe_allow_html=True)
                with header_cols[5]: st.markdown("<div style='text-align: right;'>**S/L**</div>", unsafe_allow_html=True)
                with header_cols[6]: st.markdown("<div style='text-align: right;'>**P&L**</div>", unsafe_allow_html=True)
                with header_cols[7]: st.markdown("<div style='text-align: right;'>**Target**</div>", unsafe_allow_html=True)
                with header_cols[8]: st.markdown("<div style='text-align: center;'>**Status**</div>", unsafe_allow_html=True)
                with header_cols[9]: st.markdown("**Details**")
                with header_cols[10]: st.markdown("**X**")
                st.markdown("---")
            
            # Data row with consistent column widths (including selection checkbox)
            col_sel, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.5, 1.2, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.6, 0.5])
            
            # Selection checkbox (no rerun, just sets session_state)
            with col_sel:
                select_key = f"watchlist_select_{symbol}"
                current_val = st.session_state.get(select_key, False)
                st.checkbox(
                    f"Select {symbol} from watchlist",
                    key=select_key,
                    value=current_val,
                    label_visibility="collapsed",
                )
            
            with col1:
                st.markdown(f'<div class="compact-row">', unsafe_allow_html=True)
                st.markdown(f'<div style="font-weight: bold;">{symbol}</div>', unsafe_allow_html=True)
                if company_name:
                    st.markdown(f'<div style="font-size: 0.8em; opacity: 0.8;">{company_name}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown(f'<div class="compact-row">{formatted_date}</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'<div style="text-align: right;">₹{current_price:,.2f}</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown(f'<div style="text-align: right;">₹{entry_price:,.2f}</div>', unsafe_allow_html=True)
            
            with col5:
                st.markdown(f'<div style="text-align: right;">₹{stop_loss:,.2f}</div>', unsafe_allow_html=True)
            
            with col6:
                # P&L with color and right alignment
                if pnl > 0:
                    st.markdown(f'<div style="text-align: right;"><span style="color: #28a745;">+{pnl:.1f}%<br>+₹{pnl_amount:,.2f}</span></div>', unsafe_allow_html=True)
                elif pnl < 0:
                    st.markdown(f'<div style="text-align: right;"><span style="color: #dc3545;">{pnl:.1f}%<br>₹{pnl_amount:,.2f}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="text-align: right;">0.0%<br>₹0.00</div>', unsafe_allow_html=True)
            
            with col7:
                st.markdown(f'<div style="text-align: right;">₹{target_price:,.2f}</div>', unsafe_allow_html=True)
            
            with col8:
                # Status with color and centered
                if status == 'ACTIVE':
                    st.markdown('<div style="text-align: center; color: #28a745;">🟢</div>', unsafe_allow_html=True)
                elif status == 'TARGET_HIT':
                    st.markdown('<div style="text-align: center; color: #ffc107;">🎯</div>', unsafe_allow_html=True)
                elif status == 'STOP_LOSS_HIT':
                    st.markdown('<div style="text-align: center; color: #dc3545;">🛑</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="text-align: center;">📊</div>', unsafe_allow_html=True)
            
            with col9:
                # Create a unique key for the expander
                expander_key = f"watchlist_expander_{index}"
                
                # Create a button to toggle the expander
                if st.button("🔍", key=f"btn_{expander_key}", 
                           help="View details"):
                    # Toggle the expander state in session state
                    if f"expanded_{expander_key}" in st.session_state:
                        st.session_state[f"expanded_{expander_key}"] = not st.session_state[f"expanded_{expander_key}"]
                    else:
                        st.session_state[f"expanded_{expander_key}"] = True
            
            with col10:
                if st.button("X", key=f"delete_{index}", help="Remove from watchlist"):
                    st.session_state[f"delete_from_watchlist_{symbol}"] = True
                    st.rerun()
            
            # Show the expander if it's toggled on
            if st.session_state.get(f"expanded_{expander_key}", False):
                # Use container to create a modal-like appearance
                with st.container():
                    # Create a header with a close button
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown(f"### {symbol} - Watchlist Details")
                    with col2:
                        if st.button("✕", key=f"close_{expander_key}"):
                            st.session_state[f"expanded_{expander_key}"] = False
                            st.rerun()
                    
                    # Add a divider
                    st.markdown("---")
                    
                    # Display the detailed content
                    ExpandableUI._display_watchlist_details(item)
                    
                    # Add some spacing and a close button at the bottom
                    st.markdown("")
                    if st.button("Close Details", key=f"close_btn_{expander_key}"):
                        st.session_state[f"expanded_{expander_key}"] = False
                        st.rerun()
            
            return False
            
        except Exception as e:
            logger.error(f"Error displaying watchlist row: {str(e)}")
            return False
    
    @staticmethod
    def _get_watchlist_details_html(item: Dict) -> str:
        """Get HTML content for watchlist details modal."""
        try:
            symbol = item.get('symbol', 'N/A')
            entry_price = item.get('entry_price', 0)
            current_price = item.get('current_price', 0)
            target_price = item.get('target_price', 0)
            stop_loss = item.get('stop_loss', 0)
            status = item.get('status', 'N/A')
            confidence = item.get('confidence', 0)
            notes = item.get('notes', '')
            
            # Calculate P&L
            pnl_percent = 0
            pnl_amount = 0
            if entry_price > 0:
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                pnl_amount = current_price - entry_price
            
            # Calculate distances
            target_distance_html = ""
            stop_distance_html = ""
            if current_price > 0:
                if target_price > 0:
                    target_distance = ((target_price - current_price) / current_price) * 100
                    target_distance_html = f"<p><strong>Distance to Target:</strong> {target_distance:.1f}%</p>"
                
                if stop_loss > 0:
                    stop_distance = ((current_price - stop_loss) / current_price) * 100
                    stop_distance_html = f"<p><strong>Distance to Stop Loss:</strong> {stop_distance:.1f}%</p>"
            
            # Risk-Reward calculation
            risk_reward_html = ""
            if target_price > 0 and stop_loss > 0 and entry_price > 0:
                potential_profit = target_price - entry_price
                potential_loss = entry_price - stop_loss
                if potential_loss > 0:
                    risk_reward = potential_profit / potential_loss
                    risk_reward_html = f"<p><strong>Risk-Reward Ratio:</strong> {risk_reward:.2f}:1</p>"
            
            # P&L color
            pnl_color = "#28a745" if pnl_percent > 0 else "#dc3545" if pnl_percent < 0 else "#ffc107"
            
            html_content = f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1;">
                    <h3>📊 Position Details</h3>
                    <div class="metric">
                        <p><strong>Symbol:</strong> {symbol}</p>
                        <p><strong>Entry Price:</strong> ₹{entry_price:.2f}</p>
                        <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
                        <p><strong>Target Price:</strong> ₹{target_price:.2f}</p>
                        <p><strong>Stop Loss:</strong> ₹{stop_loss:.2f}</p>
                        {target_distance_html}
                        {stop_distance_html}
                    </div>
                </div>
                <div style="flex: 1;">
                    <h3>📈 Performance Metrics</h3>
                    <div class="metric">
                        <p><strong>P&L Percentage:</strong> <span style="color: {pnl_color}; font-weight: bold;">{pnl_percent:.2f}%</span></p>
                        <p><strong>P&L Amount:</strong> <span style="color: {pnl_color}; font-weight: bold;">₹{pnl_amount:.2f}</span></p>
                        <p><strong>Status:</strong> {status}</p>
                        <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                        {risk_reward_html}
                    </div>
                </div>
            </div>
            """
            
            # Notes section
            if notes:
                html_content += f"""
                <div style="margin-bottom: 20px;">
                    <h3>📝 Notes</h3>
                    <div class="metric">
                        <p>{notes}</p>
                    </div>
                </div>
                """
            
            # Action buttons
            html_content += """
            <div style="margin-bottom: 20px;">
                <h3>⚡ Actions</h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button onclick="alert('Update Price functionality will be implemented')" 
                            style="background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        📊 Update Price
                    </button>
                    <button onclick="alert('Edit Notes functionality will be implemented')" 
                            style="background-color: #2196F3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        ✏️ Edit Notes
                    </button>
                    <button onclick="alert('Delete functionality will be implemented')" 
                            style="background-color: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        🗑️ Delete
                    </button>
                </div>
            </div>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating watchlist details HTML: {str(e)}")
            return "<p>Error loading details</p>"
    
    @staticmethod
    def _display_watchlist_details(item: Dict):
        """Display detailed watchlist information."""
        try:
            # If this watchlist item came from a full recommendation, reuse the
            # same detailed recommendation renderer so the information matches
            # what is shown in the recommendations tab.
            full_rec = item.get('full_recommendation')
            if isinstance(full_rec, dict):
                ExpandableUI._display_recommendation_details(full_rec)
                return

            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Position Details**")
                st.write(f"• **Symbol:** {item.get('symbol', 'N/A')}")
                st.write(f"• **Entry Price:** ₹{item.get('entry_price', 0):.2f}")
                st.write(f"• **Current Price:** ₹{item.get('current_price', 0):.2f}")
                st.write(f"• **Target Price:** ₹{item.get('target_price', 0):.2f}")
                st.write(f"• **Stop Loss:** ₹{item.get('stop_loss', 0):.2f}")
                
                # Calculate distances to targets
                current_price = item.get('current_price', 0)
                target_price = item.get('target_price', 0)
                stop_loss = item.get('stop_loss', 0)
                
                if current_price > 0:
                    if target_price > 0:
                        target_distance = ((target_price - current_price) / current_price) * 100
                        st.write(f"• **Distance to Target:** {target_distance:.1f}%")
                    
                    if stop_loss > 0:
                        stop_distance = ((current_price - stop_loss) / current_price) * 100
                        st.write(f"• **Distance to Stop Loss:** {stop_distance:.1f}%")
            
            with col2:
                st.markdown("**📈 Performance Metrics**")
                
                # P&L calculations
                entry_price = item.get('entry_price', 0)
                current_price = item.get('current_price', 0)
                
                if entry_price > 0:
                    pnl_percent = ((current_price - entry_price) / entry_price) * 100
                    pnl_amount = current_price - entry_price
                    
                    st.write(f"• **P&L Percentage:** {pnl_percent:.2f}%")
                    st.write(f"• **P&L Amount:** ₹{pnl_amount:.2f}")
                    
                    # Risk-Reward
                    target_price = item.get('target_price', 0)
                    stop_loss = item.get('stop_loss', 0)
                    
                    if target_price > 0 and stop_loss > 0:
                        potential_profit = target_price - entry_price
                        potential_loss = entry_price - stop_loss
                        if potential_loss > 0:
                            risk_reward = potential_profit / potential_loss
                            st.write(f"• **Risk-Reward Ratio:** {risk_reward:.2f}:1")
                
                st.write(f"• **Status:** {item.get('status', 'N/A')}")
                st.write(f"• **Confidence:** {item.get('confidence', 0):.1f}%")
            
            # Notes
            notes = item.get('notes', '')
            if notes:
                st.markdown("**📝 Notes**")
                st.write(notes)
            
            # Action buttons
            st.markdown("**⚡ Actions**")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button(f"📊 Update Price", key=f"update_{item.get('symbol')}_watchlist"):
                    st.session_state[f"update_price_{item.get('symbol')}"] = True
            
            with action_col2:
                if st.button(f"✏️ Edit Notes", key=f"edit_{item.get('symbol')}_watchlist"):
                    st.session_state[f"edit_notes_{item.get('symbol')}"] = True
            
            with action_col3:
                if st.button(f"🗑️ Delete", key=f"remove_{item.get('symbol')}_watchlist", type="primary"):
                    st.session_state[f"delete_from_watchlist_{item.get('symbol')}"] = True
                    st.rerun()
            
        except Exception as e:
            logger.error(f"Error displaying watchlist details: {str(e)}")
    
    @staticmethod
    def display_swing_strategy_row(strategy: Dict, index: int, show_actions: bool = True) -> bool:
        """Display a swing strategy in an expandable row format."""
        try:
            symbol = strategy.get('symbol', 'UNKNOWN')
            company_name = strategy.get('company_name', '')
            
            # Get entry price, target, and stop loss from the strategy
            # First try to get from the top level, then from the 'levels' dictionary if it exists
            entry_price = strategy.get('entry_price', strategy.get('current_price', 0))
            take_profit = strategy.get('take_profit', 0)
            stop_loss = strategy.get('stop_loss', 0)
            
            # If we have a 'levels' dictionary, use those values
            if 'levels' in strategy and isinstance(strategy['levels'], dict):
                entry_price = strategy['levels'].get('entry_price', entry_price)
                take_profit = strategy['levels'].get('take_profit', take_profit)
                stop_loss = strategy['levels'].get('stop_loss', stop_loss)
            
            # Ensure we have valid values
            current_price = strategy.get('current_price', entry_price)
            entry_price = entry_price or current_price
            take_profit = take_profit or (entry_price * 1.02)  # Default 2% take profit if not set
            stop_loss = stop_loss or (entry_price * 0.98)  # Default 2% stop loss if not set
            
            position_size = strategy.get('position_size', 0)
            investment_amount = strategy.get('investment_amount', 0)
            risk_reward_ratio = strategy.get('risk_reward_ratio', 0)
            status = strategy.get('status', 'ACTIVE')
            created_at = strategy.get('created_at', '')
            
            # Calculate days remaining (7 days from creation)
            days_remaining = 7  # Default value
            try:
                if created_at:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_passed = (datetime.now(created_date.tzinfo) - created_date).days
                    days_remaining = max(0, 7 - days_passed)  # Clamp between 0 and 7
            except Exception as e:
                logger.warning(f"Error calculating days remaining: {str(e)}")
                days_remaining = 7
            
            # Create main row - more compact
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 1, 0.8, 0.8])
            
            with col1:
                st.write(f"**{symbol}**")
                if company_name:
                    st.caption(company_name)
            
            with col2:
                st.write(f"₹{entry_price:.2f}")
            
            with col3:
                st.write(f"₹{take_profit:.2f}")
            
            with col4:
                st.write(f"₹{stop_loss:.2f}")
            
            with col5:
                # Show days remaining with color coding
                days_text = f"{days_remaining}d"
                if days_remaining <= 1:
                    st.markdown(f"<span style='color: #dc3545; font-weight: bold;'>{days_text}</span>", unsafe_allow_html=True)
                elif days_remaining <= 3:
                    st.markdown(f"<span style='color: #ffc107;'>{days_text}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #28a745;'>{days_text}</span>", unsafe_allow_html=True)
            
            with col6:
                # Calculate current status based on price action
                if current_price <= stop_loss * 1.01:  # Within 1% of stop loss
                    status_emoji = "🔴"  # Risk
                    status_text = "Risk: Near Stop Loss"
                    status_color = "#dc3545"
                elif current_price >= take_profit * 0.99:  # Within 1% of take profit
                    status_emoji = "🟢"  # Target
                    status_text = "Target: Near Take Profit"
                    status_color = "#28a745"
                else:
                    # Calculate distance to stop and target as percentage
                    stop_distance_pct = ((current_price - stop_loss) / stop_loss) * 100
                    target_distance_pct = ((take_profit - current_price) / current_price) * 100
                    
                    if stop_distance_pct < 1.5 or target_distance_pct < 1.5:
                        status_emoji = "🟡"  # Caution
                        status_text = "Caution: Near Key Level"
                        status_color = "#ffc107"
                    else:
                        status_emoji = "🟢"  # Safe
                        status_text = "Safe: Within Range"
                        status_color = "#28a745"
                
                # Display status with tooltip
                st.markdown(
                    f'<span style="color: {status_color};" title="{status_text}">{status_emoji} {status_text.split(":")[0]}</span>', 
                    unsafe_allow_html=True
                )
            
            with col7:
                # Create a unique key for the expander
                expander_key = f"swing_expander_{index}"
                
                # Create a button to toggle the expander
                if st.button("🔍 Details", key=f"btn_{expander_key}", 
                           help="Click to view detailed analysis"):
                    # Toggle the expander state in session state
                    if f"expanded_{expander_key}" in st.session_state:
                        st.session_state[f"expanded_{expander_key}"] = not st.session_state[f"expanded_{expander_key}"]
                    else:
                        st.session_state[f"expanded_{expander_key}"] = True
            
            # Add delete button in the actions column
            with col8:
                if st.button("🗑️", key=f"delete_{expander_key}", 
                           help="Delete this strategy"):
                    if 'data_persistence' in st.session_state:
                        deleted = st.session_state.data_persistence.delete_swing_strategy(symbol)
                        if deleted:
                            st.success(f"Deleted strategy for {symbol}")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete strategy for {symbol}")
            
            # Show the expander if it's toggled on
            if st.session_state.get(f"expanded_{expander_key}", False):
                # Use container to create a modal-like appearance
                with st.container():
                    # Create a header with a close button
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown(f"### {symbol} - Swing Strategy Details")
                    with col2:
                        if st.button("✕", key=f"close_{expander_key}"):
                            st.session_state[f"expanded_{expander_key}"] = False
                            st.rerun()
                    
                    # Add a divider
                    st.markdown("---")
                    
                    # Display the detailed content
                    ExpandableUI._display_swing_strategy_details(strategy)
                    
                    # Add some spacing and a close button at the bottom
                    st.markdown("")
                    if st.button("Close Details", key=f"close_btn_{expander_key}"):
                        st.session_state[f"expanded_{expander_key}"] = False
                        st.rerun()
            
            with col8:
                pass
            
            return False
            
        except Exception as e:
            logger.error(f"Error displaying swing strategy row: {str(e)}")
            return False
    
    @staticmethod
    def _get_swing_strategy_details_html(strategy: Dict) -> str:
        """Get HTML content for swing strategy details modal."""
        try:
            symbol = strategy.get('symbol', 'N/A')
            strategy_name = strategy.get('strategy_name', 'N/A')
            entry_price = strategy.get('entry_price', 0)
            take_profit = strategy.get('take_profit', 0)
            stop_loss = strategy.get('stop_loss', 0)
            holding_period = strategy.get('holding_period_days', 7)
            position_size = strategy.get('position_size', 0)
            investment_amount = strategy.get('investment_amount', 0)
            risk_amount = strategy.get('risk_amount', 0)
            risk_reward_ratio = strategy.get('risk_reward_ratio', 0)
            confidence = strategy.get('confidence', 0)
            status = strategy.get('status', 'N/A')
            entry_date = strategy.get('entry_date', 'N/A')
            created_at = strategy.get('created_at', 'N/A')
            expected_exit_date = strategy.get('expected_exit_date', 'N/A')
            
            # Calculate days remaining
            days_remaining_html = ""
            try:
                if expected_exit_date and expected_exit_date != 'N/A':
                    exit_date = datetime.fromisoformat(expected_exit_date.replace('Z', '+00:00'))
                    days_remaining = (exit_date - datetime.now()).days
                    if days_remaining > 0:
                        days_remaining_html = f"<p><strong>Days Remaining:</strong> {days_remaining}</p>"
                    else:
                        days_remaining_html = "<p><strong>Status:</strong> <span style='color: #dc3545;'>Expired</span></p>"
            except:
                days_remaining_html = "<p><strong>Days Remaining:</strong> N/A</p>"
            
            html_content = f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1;">
                    <h3>📊 Strategy Overview</h3>
                    <div class="metric">
                        <p><strong>Symbol:</strong> {symbol}</p>
                        <p><strong>Strategy Name:</strong> {strategy_name}</p>
                        <p><strong>Entry Price:</strong> ₹{entry_price:.2f}</p>
                        <p><strong>Take Profit:</strong> ₹{take_profit:.2f}</p>
                        <p><strong>Stop Loss:</strong> ₹{stop_loss:.2f}</p>
                        <p><strong>Holding Period:</strong> {holding_period} days</p>
                    </div>
                </div>
                <div style="flex: 1;">
                    <h3>💰 Position Details</h3>
                    <div class="metric">
                        <p><strong>Position Size:</strong> {position_size} shares</p>
                        <p><strong>Investment Amount:</strong> ₹{investment_amount:,.0f}</p>
                        <p><strong>Risk Amount:</strong> ₹{risk_amount:,.0f}</p>
                        <p><strong>Risk-Reward Ratio:</strong> {risk_reward_ratio:.2f}:1</p>
                        <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                        <p><strong>Status:</strong> {status}</p>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3>📅 Timeline</h3>
                <div style="display: flex; gap: 20px;">
                    <div style="flex: 1;">
                        <div class="metric">
                            <p><strong>Entry Date:</strong> {entry_date[:10] if entry_date != 'N/A' else 'N/A'}</p>
                            <p><strong>Created:</strong> {created_at[:19] if created_at != 'N/A' else 'N/A'}</p>
                        </div>
                    </div>
                    <div style="flex: 1;">
                        <div class="metric">
                            <p><strong>Expected Exit:</strong> {expected_exit_date[:10] if expected_exit_date != 'N/A' else 'N/A'}</p>
                            {days_remaining_html}
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3>📋 Strategy Rules</h3>
                <div class="metric">
                    <p>• Hold for maximum 7 days</p>
                    <p>• Stop loss at 8% below entry</p>
                    <p>• Take profit at 15% above entry</p>
                    <p>• Monitor daily for exit signals</p>
                    <p>• Do not average down if trade goes against you</p>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3>⚡ Actions</h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button onclick="alert('Update Status functionality will be implemented')" 
                            style="background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        📊 Update Status
                    </button>
                    <button onclick="alert('Edit Strategy functionality will be implemented')" 
                            style="background-color: #2196F3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        ✏️ Edit Strategy
                    </button>
                    <button onclick="alert('Remove Strategy functionality will be implemented')" 
                            style="background-color: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        🗑️ Remove Strategy
                    </button>
                </div>
            </div>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating swing strategy details HTML: {str(e)}")
            return "<p>Error loading details</p>"
    
    @staticmethod
    def _display_swing_strategy_details(strategy: Dict):
        """Display detailed swing strategy information."""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Strategy Overview**")
                st.write(f"• **Symbol:** {strategy.get('symbol', 'N/A')}")
                st.write(f"• **Strategy Name:** {strategy.get('strategy_name', 'N/A')}")
                st.write(f"• **Entry Price:** ₹{strategy.get('entry_price', 0):.2f}")
                st.write(f"• **Take Profit:** ₹{strategy.get('take_profit', 0):.2f}")
                st.write(f"• **Stop Loss:** ₹{strategy.get('stop_loss', 0):.2f}")
                st.write(f"• **Holding Period:** {strategy.get('holding_period_days', 7)} days")
            
            with col2:
                st.markdown("**💰 Position Details**")
                st.write(f"• **Position Size:** {strategy.get('position_size', 0)} shares")
                st.write(f"• **Investment Amount:** ₹{strategy.get('investment_amount', 0):,.0f}")
                st.write(f"• **Risk Amount:** ₹{strategy.get('risk_amount', 0):,.0f}")
                st.write(f"• **Risk-Reward Ratio:** {strategy.get('risk_reward_ratio', 0):.2f}:1")
                st.write(f"• **Confidence:** {strategy.get('confidence', 0):.1f}%")
                st.write(f"• **Status:** {strategy.get('status', 'N/A')}")
            
            # Timeline
            st.markdown("**📅 Timeline**")
            timeline_col1, timeline_col2 = st.columns(2)
            
            with timeline_col1:
                st.write(f"• **Entry Date:** {strategy.get('entry_date', 'N/A')[:10]}")
                st.write(f"• **Created:** {strategy.get('created_at', 'N/A')[:19]}")
            
            with timeline_col2:
                st.write(f"• **Expected Exit:** {strategy.get('expected_exit_date', 'N/A')[:10]}")
                
                # Calculate days remaining
                try:
                    exit_date = datetime.fromisoformat(strategy.get('expected_exit_date', '').replace('Z', '+00:00'))
                    days_remaining = (exit_date - datetime.now()).days
                    if days_remaining > 0:
                        st.write(f"• **Days Remaining:** {days_remaining}")
                    else:
                        st.write(f"• **Status:** Expired")
                except:
                    st.write(f"• **Days Remaining:** N/A")
            
            # Strategy Rules
            st.markdown("**📋 Strategy Rules**")
            st.write("• Hold for maximum 7 days")
            st.write("• Stop loss at 8% below entry")
            st.write("• Take profit at 15% above entry")
            st.write("• Monitor daily for exit signals")
            st.write("• Do not average down if trade goes against you")
            
            # Action buttons
            st.markdown("**⚡ Actions**")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button(f"📊 Update Status", key=f"update_swing_{strategy.get('symbol')}"):
                    st.info("Status update functionality will be implemented")
            
            with action_col2:
                if st.button(f"✏️ Edit Strategy", key=f"edit_swing_{strategy.get('symbol')}"):
                    st.info("Edit functionality will be implemented")
            
            with action_col3:
                if st.button(f"🗑️ Remove Strategy", key=f"remove_swing_{strategy.get('symbol')}"):
                    st.info("Remove functionality will be implemented")
            
        except Exception as e:
            logger.error(f"Error displaying swing strategy details: {str(e)}")
    
    @staticmethod
    def display_data_summary(summary: Dict):
        """Display a summary of all saved data."""
        try:
            st.markdown("**📊 Data Summary**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Recommendations",
                    summary.get('recommendations', {}).get('total_count', 0),
                    f"{summary.get('recommendations', {}).get('dates_count', 0)} dates"
                )
            
            with col2:
                watchlist_data = summary.get('watchlist', {})
                st.metric(
                    "Watchlist Items",
                    watchlist_data.get('total_count', 0),
                    f"{watchlist_data.get('active_count', 0)} active"
                )
            
            with col3:
                swing_data = summary.get('swing_strategies', {})
                st.metric(
                    "Swing Strategies",
                    swing_data.get('total_count', 0),
                    f"{swing_data.get('dates_count', 0)} dates"
                )
            
        except Exception as e:
            logger.error(f"Error displaying data summary: {str(e)}")
