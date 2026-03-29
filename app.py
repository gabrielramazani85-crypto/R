import streamlit as st
import pandas as pd
import datetime

# Helper functions

def load_data():
    try:
        return pd.read_csv('data.csv')
    except Exception as e:
        st.error(f'Error loading data: {e}')
        return pd.DataFrame()  # Return an empty DataFrame in case of error


def validate_order(order):
    valid = True
    if not order.get('item_name') or not isinstance(order['quantity'], int):
        valid = False
        st.warning('Invalid order data. Please check your input.')
    return valid

# Main app

def main():
    st.title('Restaurant Management System')

    # Load initial data
    data = load_data()
    orders = []

    # Order submission form
    with st.form(key='order_form'):
        item_name = st.text_input('Item Name')
        quantity = st.number_input('Quantity', min_value=1)
        submit_button = st.submit_button(label='Submit')

        if submit_button:
            order = {'item_name': item_name, 'quantity': quantity}
            if validate_order(order):
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                order['timestamp'] = timestamp
                orders.append(order)
                st.success(f'Order submitted successfully at {timestamp}!')

    # Display orders
    if orders:
        st.subheader('Orders')
        for order in orders:
            st.write(f"Item: {order['item_name']}, Quantity: {order['quantity']}, Time: {order['timestamp']}")

if __name__ == '__main__':
    main()