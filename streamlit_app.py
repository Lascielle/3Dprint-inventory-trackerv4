import streamlit as st
import pandas as pd
import sqlite3
import os

# Ensure image directory exists
IMAGE_DIR = './images/'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

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
        SELECT sku_dictionary.sku, sku_dictionary.description, sku_dictionary.image_path, inventory.quantity 
        FROM inventory 
        JOIN sku_dictionary ON inventory.sku = sku_dictionary.sku
    ''', conn)

    # Prepare data for display
    for index, row in inventory_data.iterrows():
        col1, col2 = st.columns([1, 4])

        # Display the image in the first column
        with col1:
            if row['image_path']:
                st.image(row['image_path'], width=80)  # Adjust image size
            else:
                st.text("No Image")

        # Display the rest of the inventory data in the second column
        with col2:
            st.markdown(f"""
                **SKU**: {row['sku']}  
                **Description**: {row['description']}  
                **Quantity**: {row['quantity']}
            """)
        st.write("---")  # Horizontal separator

def add_sku():
    conn = sqlite3.connect('printer_inventory.db')
    st.subheader('Add SKU')

    # Input fields for SKU information
    sku = st.text_input('SKU', key='add_sku')
    description = st.text_input('Description', key='add_description')
    category = st.selectbox('Category', ['filament', 'consumable', 'wear part'], key='add_category')

    # Image upload field
    uploaded_file = st.file_uploader("Upload an image for the SKU", type=['jpg', 'jpeg', 'png'], key='add_image')

    if st.button('Add SKU', key='add_button'):
        # If an image is uploaded, save it to the images directory
        image_path = None
        if uploaded_file is not None:
            image_path = os.path.join(IMAGE_DIR, f"{sku}_{uploaded_file.name}")
            with open(image_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success('Image uploaded successfully!')

        # Insert the SKU data into the database
        conn.execute('INSERT INTO sku_dictionary (sku, description, category, image_path) VALUES (?, ?, ?, ?)', 
                     (sku, description, category, image_path))
        conn.commit()
        st.success('SKU added successfully!')

# Dummy function placeholders for other app functionalities
def transact_inventory():
    st.subheader("Transact Inventory")
    st.write("Transaction functionality here...")

def view_sku_dictionary():
    st.subheader("View SKU Dictionary")
    st.write("SKU dictionary view here...")

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
