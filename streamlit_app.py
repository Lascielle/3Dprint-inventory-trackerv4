import streamlit as st
import pandas as pd
import sqlite3

# Main app functions (with top bar navigation included)
def main_app():
    st.title('3D Printer Inventory Management')

    # Call top navigation bar
    top_bar_navigation()

# Top bar navigation
def top_bar_navigation():
    tabs = st.tabs(["View Inventory", "Transact Inventory", "View SKU Dictionary", "Add SKU", "Edit/Delete SKU"])

    with tabs[0]:
        view_inventory()

    with tabs[1]:
        transact_inventory()

    with tabs[2]:
        view_sku_dictionary()

    with tabs[3]:
        add_sku()

    with tabs[4]:
        edit_sku()

# Functions for viewing, adding, editing SKUs and transacting inventory
def view_inventory():
    conn = sqlite3.connect('printer_inventory.db')
    st.header('Inventory')

    # Fetch the inventory data
    inventory_data = pd.read_sql_query('''
        SELECT sku_dictionary.sku, sku_dictionary.description, inventory.quantity 
        FROM inventory 
        JOIN sku_dictionary ON inventory.sku = sku_dictionary.sku
    ''', conn)

    def highlight_low_stock(s):
        return ['background-color: red' if v < 5 else '' for v in s]

    # Style the table to make it more visually appealing
    styled_inventory_data = inventory_data.style \
        .set_properties(**{
            'background-color': '#f7f7f7', 'color': 'black', 'border-color': 'black', 'width': '100%'}) \
        .apply(highlight_low_stock, subset=['quantity']) \
        .highlight_max(subset=['quantity'], color='lightgreen', axis=0) \
        .highlight_min(subset=['quantity'], color='lightcoral', axis=0) \
        .set_table_styles([
            {'selector': 'thead th', 'props': 'background-color: #1f77b4; color: white; font-weight: bold;'},
            {'selector': 'tbody tr:nth-child(even)', 'props': 'background-color: #f7f7f7;'},
            {'selector': 'tbody tr:nth-child(odd)', 'props': 'background-color: #ffffff;'},
            {'selector': 'table', 'props': 'width: 100%; margin-left: 0px;'}
        ]) \
        .set_properties(subset=['sku'], **{'text-align': 'left'}) \
        .set_properties(subset=['quantity'], **{'text-align': 'right'}) \
        .set_caption('**Current Inventory Levels (Low stock in red)**')

    # Use st.dataframe to display the styled table
    st.dataframe(styled_inventory_data, use_container_width=True)

# Dummy function placeholders for other app functionalities
def transact_inventory():
    st.subheader("Transact Inventory")
    st.write("Transaction functionality here...")

def view_sku_dictionary():
    st.subheader("View SKU Dictionary")
    st.write("SKU dictionary view here...")

def add_sku():
    st.subheader("Add SKU")
    st.write("Add SKU functionality here...")

def edit_sku():
    st.subheader("Edit/Delete SKU")
    st.write("Edit or delete SKU functionality here...")

# Main execution
if __name__ == '__main__':
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if st.session_state['logged_in']:
        # Show a logout button
        if st.button('Logout'):
            st.session_state['logged_in'] = False
            st.success('Logged out successfully!')
            st.rerun()  # To reload the page with the login form
        else:
            # Show the main app if logged in
            main_app()
    else:
        # Login form if not logged in
        st.title('Login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Login'):
            if username == '3dprint@harveyperformance.com' and password == '3618':
                st.session_state['logged_in'] = True
                st.success('Logged in successfully!')
                st.rerun()  # Reload to show the main app
            else:
                st.error('Invalid username or password')
