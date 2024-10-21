import streamlit as st
import pandas as pd
import sqlite3

# Main app functions (with top bar navigation included)
def main_app():
    # Add custom CSS for a full-width image banner
    st.markdown(
        """
        <style>
        .full-width-banner {
            width: 100%;
            height: auto;
        }
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #333333;
            text-align: center;
            margin-top: -20px;  /* Adjust margin to control spacing */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Use HTML to display the image with 100% width
    st.markdown(
        f'''
        <div>
            <img class="full-width-banner" src="Logo_HarveyPerformance_Primary.png">
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # Add main title below the image
    st.markdown('<div class="main-title">3D Printer Inventory Management</div>', unsafe_allow_html=True)

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
    try:
        inventory_data = pd.read_sql_query('''
            SELECT sku_dictionary.sku, sku_dictionary.description, inventory.quantity 
            FROM inventory 
            JOIN sku_dictionary ON inventory.sku = sku_dictionary.sku
        ''', conn)
    except Exception as e:
        st.error(f"Error retrieving inventory data: {str(e)}")
        return

    # Apply styling to the inventory table
    styled_inventory_data = inventory_data.style \
        .set_properties(subset=['sku', 'description'], **{'text-align': 'left', 'font-size': '14px'}) \
        .set_properties(subset=['quantity'], **{'text-align': 'center', 'font-size': '14px'}) \
        .set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#1f77b4'), ('color', 'white'), ('font-size', '16px')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f7f7f7')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#ffffff')]},
        ]) \
        .set_caption("**Current Inventory Levels**")

    # Use st.dataframe to display the styled table
    st.dataframe(styled_inventory_data, use_container_width=True)

def add_sku():
    conn = sqlite3.connect('printer_inventory.db')
    st.subheader('Add SKU')

    # Input fields for SKU information
    sku = st.text_input('SKU', key='add_sku')
    description = st.text_input('Description', key='add_description')
    category = st.selectbox('Category', ['filament', 'consumable', 'wear part'], key='add_category')

    if st.button('Add SKU', key='add_button'):
        # Insert the SKU data into the database
        conn.execute('INSERT INTO sku_dictionary (sku, description, category) VALUES (?, ?, ?)', 
                     (sku, description, category))
        conn.commit()
        st.success('SKU added successfully!')

def edit_sku():
    conn = sqlite3.connect('printer_inventory.db')
    st.subheader('Edit/Delete SKU')
    
    # Fetch SKU data
    skus = pd.read_sql_query("SELECT * FROM sku_dictionary", conn)
    sku_id = st.selectbox('Select SKU to edit/delete', skus['id'].values, key='edit_sku_select')

    if sku_id:
        sku_data = conn.execute('SELECT * FROM sku_dictionary WHERE id=?', (sku_id,)).fetchone()
        sku = st.text_input('SKU', value=sku_data[1], key='edit_sku')
        description = st.text_input('Description', value=sku_data[2], key='edit_description')
        category = st.selectbox('Category', ['filament', 'consumable', 'wear part'], 
                                index=['filament', 'consumable', 'wear part'].index(sku_data[3]), key='edit_category')

        if st.button('Update SKU', key='update_button'):
            conn.execute('UPDATE sku_dictionary SET sku=?, description=?, category=? WHERE id=?',
                          (sku, description, category, sku_id))
            conn.commit()
            st.success('SKU updated successfully!')

        if st.button('Delete SKU', key='delete_button'):
            conn.execute('DELETE FROM sku_dictionary WHERE id=?', (sku_id,))
            conn.commit()
            st.success('SKU deleted successfully!')

def transact_inventory():
    conn = sqlite3.connect('printer_inventory.db')
    st.header('Transact Inventory')

    # Fetch SKUs for transaction selection
    skus = pd.read_sql_query("SELECT sku, description FROM sku_dictionary", conn)
    sku = st.selectbox('Select SKU', skus['sku'].values, key='transact_sku')
    transaction_type = st.radio('Transaction Type', ['Receive', 'Remove'], key='transact_type')
    quantity = st.number_input('Quantity', min_value=1, step=1, key='transact_quantity')

    if st.button('Submit', key='transact_submit'):
        # Check current inventory for the selected SKU
        current_qty = conn.execute('SELECT quantity FROM inventory WHERE sku=?', (sku,)).fetchone()

        if current_qty is None:
            current_qty = 0
        else:
            current_qty = current_qty[0]

        if transaction_type == 'Receive':
            new_qty = current_qty + quantity
        else:  # Remove
            new_qty = current_qty - quantity if current_qty >= quantity else 0

        # Update or insert inventory
        if current_qty == 0:
            conn.execute('INSERT INTO inventory (sku, quantity) VALUES (?, ?)', (sku, new_qty))
        else:
            conn.execute('UPDATE inventory SET quantity=? WHERE sku=?', (new_qty, sku))

        conn.commit()
        st.success(f'Inventory updated successfully! New quantity for {sku}: {new_qty}')

def view_sku_dictionary():
    conn = sqlite3.connect('printer_inventory.db')
    st.header('SKU Dictionary')

    # Fetch the data from the SKU dictionary
    skus = pd.read_sql_query("SELECT sku, description, category FROM sku_dictionary", conn)

    # Display the SKU dictionary
    st.dataframe(skus, use_container_width=True)

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
