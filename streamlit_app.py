import streamlit as st
import pandas as pd
import sqlite3

# Connect to SQLite
conn = sqlite3.connect('printer_inventory.db')
c = conn.cursor()

# Create SKU Dictionary table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS sku_dictionary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL,
        description TEXT,
        category TEXT CHECK(category IN ('filament', 'consumable', 'wear part')),
        supplier_url TEXT
    )
''')
conn.commit()

# Create Inventory Table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        sku TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (sku) REFERENCES sku_dictionary (sku)
    )
''')
conn.commit()

# Function to display SKU dictionary
def view_sku_dictionary():
    st.header('SKU Dictionary')

    # Fetch the data
    skus = pd.read_sql_query("SELECT sku, description, category, supplier_url FROM sku_dictionary", conn)
    
    # Iterate over rows to display each entry with clickable link
    for index, row in skus.iterrows():
        st.markdown(f"**SKU**: {row['sku']}  
                     **Description**: {row['description']}  
                     **Category**: {row['category']}  
                     **Supplier URL**: [Link]({row['supplier_url']})", unsafe_allow_html=True)
        st.write("---")  # Horizontal separator

# Function to add a new SKU
def add_sku():
    st.subheader('Add SKU')
    sku = st.text_input('SKU', key='add_sku')
    description = st.text_input('Description', key='add_description')
    category = st.selectbox('Category', ['filament', 'consumable', 'wear part'], key='add_category')
    supplier_url = st.text_input('Supplier URL', key='add_supplier_url')

    if st.button('Add SKU', key='add_button'):
        c.execute('INSERT INTO sku_dictionary (sku, description, category, supplier_url) VALUES (?, ?, ?, ?)', 
                  (sku, description, category, supplier_url))
        conn.commit()
        st.success('SKU added successfully!')

# Function to edit or delete an existing SKU
def edit_sku():
    st.subheader('Edit/Delete SKU')
    skus = pd.read_sql_query("SELECT * FROM sku_dictionary", conn)
    sku_id = st.selectbox('Select SKU to edit/delete', skus['id'].values, key='edit_sku_select')
    
    if sku_id:
        sku_data = c.execute('SELECT * FROM sku_dictionary WHERE id=?', (sku_id,)).fetchone()
        sku = st.text_input('SKU', value=sku_data[1], key='edit_sku')
        description = st.text_input('Description', value=sku_data[2], key='edit_description')
        category = st.selectbox('Category', ['filament', 'consumable', 'wear part'], 
                                index=['filament', 'consumable', 'wear part'].index(sku_data[3]), key='edit_category')
        supplier_url = st.text_input('Supplier URL', value=sku_data[4], key='edit_supplier_url')
        
        if st.button('Update SKU', key='update_button'):
            c.execute('UPDATE sku_dictionary SET sku=?, description=?, category=?, supplier_url=? WHERE id=?',
                      (sku, description, category, supplier_url, sku_id))
            conn.commit()
            st.success('SKU updated successfully!')

        if st.button('Delete SKU', key='delete_button'):
            c.execute('DELETE FROM sku_dictionary WHERE id=?', (sku_id,))
            conn.commit()
            st.success('SKU deleted successfully!')

# Function to transact inventory
def transact_inventory():
    st.header('Transact Inventory')
    skus = pd.read_sql_query("SELECT sku, description FROM sku_dictionary", conn)
    sku = st.selectbox('Select SKU', skus['sku'].values, key='transact_sku')
    transaction_type = st.radio('Transaction Type', ['Receive', 'Remove'], key='transact_type')
    quantity = st.number_input('Quantity', min_value=1, step=1, key='transact_quantity')

    if st.button('Submit', key='transact_submit'):
        # Check current inventory for the selected SKU
        current_qty = c.execute('SELECT quantity FROM inventory WHERE sku=?', (sku,)).fetchone()
        
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
            c.execute('INSERT INTO inventory (sku, quantity) VALUES (?, ?)', (sku, new_qty))
        else:
            c.execute('UPDATE inventory SET quantity=? WHERE sku=?', (new_qty, sku))
        
        conn.commit()
        st.success(f'Inventory updated successfully! New quantity for {sku}: {new_qty}')

# Function to view inventory
def view_inventory():
    st.header('Inventory')
    inventory_data = pd.read_sql_query('''
        SELECT sku_dictionary.sku, sku_dictionary.description, inventory.quantity 
        FROM inventory 
        JOIN sku_dictionary ON inventory.sku = sku_dictionary.sku
    ''', conn)
    st.write(inventory_data)

# Top bar navigation
def top_bar_navigation():
    tabs = st.tabs(["View SKU Dictionary", "Add SKU", "Edit/Delete SKU", "Transact Inventory", "View Inventory"])
    
    with tabs[0]:
        view_sku_dictionary()

    with tabs[1]:
        add_sku()

    with tabs[2]:
        edit_sku()

    with tabs[3]:
        transact_inventory()

    with tabs[4]:
        view_inventory()

# Run the top bar navigation
if __name__ == '__main__':
    st.title('3D Printer Inventory Management')
    top_bar_navigation()
