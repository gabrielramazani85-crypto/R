import streamlit as st
import pandas as pd
import datetime
import io
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
import re

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==================== Session State Initialization ====================

if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
    st.session_state.current_user = None
    st.session_state.users = {}
    st.session_state.orders = {}

if 'users' not in st.session_state:
    st.session_state.users = {}

# ==================== User Management Functions ====================

def load_users():
    """Load users from CSV file"""
    try:
        users_df = pd.read_csv('users.csv')
        users_dict = {}
        for _, row in users_df.iterrows():
            users_dict[row['username']] = {
                'email': row['email'],
                'phone': row['phone'],
                'password_hash': row['password_hash'],
                'registration_date': row['registration_date']
            }
        return users_dict
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.error(f'Error loading users: {e}')
        return {}


def save_users():
    """Save users to CSV file"""
    try:
        users_list = []
        for username, data in st.session_state.users.items():
            users_list.append({
                'username': username,
                'email': data['email'],
                'phone': data['phone'],
                'password_hash': data['password_hash'],
                'registration_date': data['registration_date']
            })
        df = pd.DataFrame(users_list)
        df.to_csv('users.csv', index=False)
    except Exception as e:
        st.error(f'Error saving users: {e}')


def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"


# ==================== Orders Management Functions ====================

def load_user_orders(username):
    """Load orders for a specific user"""
    try:
        filename = f'orders_{username}.csv'
        df = pd.read_csv(filename)
        return df.to_dict('records')
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f'Error loading orders: {e}')
        return []


def save_user_orders(username, orders):
    """Save orders for a specific user"""
    try:
        filename = f'orders_{username}.csv'
        df = pd.DataFrame(orders)
        df.to_csv(filename, index=False)
    except Exception as e:
        st.error(f'Error saving orders: {e}')


def validate_order(order):
    """Validate order data"""
    item_name = order.get('item_name', '').strip()
    quantity = order.get('quantity', 0)
    
    if not item_name or len(item_name) < 2:
        st.warning('❌ Item name is required and must be at least 2 characters long.')
        return False
    
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        st.warning('❌ Quantity must be a positive number.')
        return False
    
    return True


def add_order(username, order):
    """Add order to user's orders"""
    if username not in st.session_state.orders:
        st.session_state.orders[username] = load_user_orders(username)
    
    st.session_state.orders[username].append(order)
    save_user_orders(username, st.session_state.orders[username])


# ==================== Export Functions ====================

def export_to_csv(df):
    """Export DataFrame to CSV format"""
    return df.to_csv(index=False).encode('utf-8')


def export_to_excel(df):
    """Export DataFrame to Excel format"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')
    return output.getvalue()


def export_to_json(df):
    """Export DataFrame to JSON format"""
    return df.to_json(orient='records', indent=2).encode('utf-8')


def export_to_xml(df):
    """Export DataFrame to XML format"""
    root = ET.Element('Orders')
    
    for _, row in df.iterrows():
        order_elem = ET.SubElement(root, 'Order')
        for col, value in row.items():
            child = ET.SubElement(order_elem, col)
            child.text = str(value)
    
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_str.encode('utf-8')


def export_to_pdf(df):
    """Export DataFrame to PDF format"""
    if not PDF_AVAILABLE:
        st.error("❌ ReportLab library not installed")
        return None
    
    try:
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Restaurant Management System - Orders Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        data = [list(df.columns)]
        for _, row in df.iterrows():
            data.append([str(val) for val in row.values])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        
        doc.build(elements)
        return output.getvalue()
    except Exception as e:
        st.error(f"❌ PDF export error: {e}")
        return None


def export_to_png(df):
    """Export DataFrame as PNG image"""
    if not MATPLOTLIB_AVAILABLE:
        st.error("❌ Matplotlib library not installed")
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [list(df.columns)] + df.values.tolist()
        table = ax.table(cellText=table_data, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(len(df.columns)):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(1, len(table_data)):
            for j in range(len(df.columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#D9E1F2')
                else:
                    table[(i, j)].set_facecolor('#F2F2F2')
        
        plt.title('Orders Report', fontsize=14, weight='bold', pad=20)
        
        output = io.BytesIO()
        fig.savefig(output, format='png', bbox_inches='tight', dpi=100)
        output.seek(0)
        plt.close(fig)
        
        return output.getvalue()
    except Exception as e:
        st.error(f"❌ PNG export error: {e}")
        return None


def export_to_jpg(df):
    """Export DataFrame as JPG image"""
    if not MATPLOTLIB_AVAILABLE:
        st.error("❌ Matplotlib library not installed")
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [list(df.columns)] + df.values.tolist()
        table = ax.table(cellText=table_data, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(len(df.columns)):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(1, len(table_data)):
            for j in range(len(df.columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#D9E1F2')
                else:
                    table[(i, j)].set_facecolor('#F2F2F2')
        
        plt.title('Orders Report', fontsize=14, weight='bold', pad=20)
        
        output = io.BytesIO()
        fig.savefig(output, format='jpg', bbox_inches='tight', dpi=100, quality=95)
        output.seek(0)
        plt.close(fig)
        
        return output.getvalue()
    except Exception as e:
        st.error(f"❌ JPG export error: {e}")
        return None


def export_to_jpeg(df):
    """Export DataFrame as JPEG image"""
    return export_to_jpg(df)


# ==================== UI Components ====================

def registration_page():
    """User Registration Page"""
    st.title('🍽️ Restaurant Management System')
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader('📝 New User Registration')
        st.write("Create your account to manage orders")
        
        with st.form(key='registration_form'):
            new_username = st.text_input('Username', placeholder='Enter your username')
            new_email = st.text_input('Email', placeholder='Enter your email')
            new_phone = st.text_input('Phone Number', placeholder='Enter your phone (e.g., +1234567890)')
            new_password = st.text_input('Password', type='password', placeholder='Enter a strong password')
            confirm_password = st.text_input('Confirm Password', type='password')
            
            register_button = st.form_submit_button(label='✅ Register', use_container_width=True)
            
            if register_button:
                # Validation checks
                if new_username in st.session_state.users:
                    st.error('❌ Username already exists!')
                elif not validate_email(new_email):
                    st.error('❌ Invalid email format!')
                elif not validate_phone(new_phone):
                    st.error('❌ Invalid phone number format!')
                elif new_password != confirm_password:
                    st.error('❌ Passwords do not match!')
                else:
                    is_valid, message = validate_password(new_password)
                    if not is_valid:
                        st.error(f'❌ {message}')
                    else:
                        # Register user
                        st.session_state.users[new_username] = {
                            'email': new_email,
                            'phone': new_phone,
                            'password_hash': hash_password(new_password),
                            'registration_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        save_users()
                        st.success(f'✅ Registration successful! Welcome {new_username}!')
                        st.balloons()
    
    with col2:
        st.subheader('🔐 Existing User Login')
        st.write("Sign in with your credentials")
        
        with st.form(key='login_form'):
            login_username = st.text_input('Username', placeholder='Enter your username', key='login_username')
            login_password = st.text_input('Password', type='password', placeholder='Enter your password', key='login_password')
            
            login_button = st.form_submit_button(label='🔓 Login', use_container_width=True)
            
            if login_button:
                if login_username not in st.session_state.users:
                    st.error('❌ Username not found!')
                else:
                    user_data = st.session_state.users[login_username]
                    if user_data['password_hash'] != hash_password(login_password):
                        st.error('❌ Incorrect password!')
                    else:
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = login_username
                        st.success(f'✅ Welcome back, {login_username}!')
                        st.rerun()


def main_app():
    """Main Application Page"""
    st.set_page_config(page_title="Restaurant Management", layout="wide")
    st.title('🍽️ Restaurant Management System')
    
    # Top bar with user info
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.write(f"**👤 Logged in as:** {st.session_state.current_user}")
    
    with col3:
        if st.button('🚪 Logout', use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    st.divider()
    
    # Load user orders
    if st.session_state.current_user not in st.session_state.orders:
        st.session_state.orders[st.session_state.current_user] = load_user_orders(st.session_state.current_user)
    
    user_orders = st.session_state.orders[st.session_state.current_user]
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('📝 Add New Order')
        
        with st.form(key='order_form'):
            item_name = st.text_input('Item Name', placeholder='e.g., Burger, Pizza...')
            quantity = st.number_input('Quantity', min_value=1, step=1, value=1)
            price = st.number_input('Price ($)', min_value=0.0, step=0.01)
            submit_button = st.form_submit_button(label='✅ Submit Order', use_container_width=True)
            
            if submit_button:
                order = {
                    'item_name': item_name.strip(),
                    'quantity': int(quantity),
                    'price': price,
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if validate_order(order):
                    add_order(st.session_state.current_user, order)
                    st.success(f'✅ Order for {order["item_name"]} submitted successfully!')
                    st.rerun()
    
    with col2:
        st.subheader('📊 Statistics')
        if user_orders:
            df = pd.DataFrame(user_orders)
            st.metric("Total Orders", len(df))
            st.metric("Total Items", int(df['quantity'].sum()))
            st.metric("Total Sales", f"${df['price'].sum():.2f}")
        else:
            st.info("No orders yet. Add one to see statistics!")
    
    # Display orders
    st.divider()
    st.subheader('📋 Your Orders')
    
    if user_orders:
        df_orders = pd.DataFrame(user_orders)
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
        
        # ==================== Download Section ====================
        st.divider()
        st.subheader('📥 Download Orders')
        
        st.write("**📄 Document Formats:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            csv_data = export_to_csv(df_orders)
            st.download_button(
                label='📄 CSV',
                data=csv_data,
                file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
        
        with col2:
            try:
                excel_data = export_to_excel(df_orders)
                st.download_button(
                    label='📊 Excel',
                    data=excel_data,
                    file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                st.error(f"❌ Excel export error: {e}")
        
        with col3:
            json_data = export_to_json(df_orders)
            st.download_button(
                label='🔗 JSON',
                data=json_data,
                file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                mime='application/json'
            )
        
        with col4:
            xml_data = export_to_xml(df_orders)
            st.download_button(
                label='📑 XML',
                data=xml_data,
                file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xml',
                mime='application/xml'
            )
        
        with col5:
            if PDF_AVAILABLE:
                try:
                    pdf_data = export_to_pdf(df_orders)
                    if pdf_data:
                        st.download_button(
                            label='🖨️ PDF',
                            data=pdf_data,
                            file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                            mime='application/pdf'
                        )
                except Exception as e:
                    st.error(f"❌ PDF export error: {e}")
            else:
                st.warning("⚠️ PDF not available")
        
        # Image Formats
        st.write("**🖼️ Image Formats:**")
        col6, col7, col8 = st.columns(3)
        
        with col6:
            if MATPLOTLIB_AVAILABLE:
                try:
                    png_data = export_to_png(df_orders)
                    if png_data:
                        st.download_button(
                            label='🖼️ PNG',
                            data=png_data,
                            file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
                            mime='image/png'
                        )
                except Exception as e:
                    st.error(f"❌ PNG export error: {e}")
            else:
                st.warning("⚠️ PNG not available")
        
        with col7:
            if MATPLOTLIB_AVAILABLE:
                try:
                    jpg_data = export_to_jpg(df_orders)
                    if jpg_data:
                        st.download_button(
                            label='🖼️ JPG',
                            data=jpg_data,
                            file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
                            mime='image/jpeg'
                        )
                except Exception as e:
                    st.error(f"❌ JPG export error: {e}")
            else:
                st.warning("⚠️ JPG not available")
        
        with col8:
            if MATPLOTLIB_AVAILABLE:
                try:
                    jpeg_data = export_to_jpeg(df_orders)
                    if jpeg_data:
                        st.download_button(
                            label='🖼️ JPEG',
                            data=jpeg_data,
                            file_name=f'orders_{st.session_state.current_user}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.jpeg',
                            mime='image/jpeg'
                        )
                except Exception as e:
                    st.error(f"❌ JPEG export error: {e}")
            else:
                st.warning("⚠️ JPEG not available")
        
        # Delete orders
        st.divider()
        if st.button('🗑️ Clear All Orders', key='clear_button', use_container_width=True):
            st.session_state.orders[st.session_state.current_user] = []
            save_user_orders(st.session_state.current_user, [])
            st.success('✅ All orders cleared!')
            st.rerun()
    
    else:
        st.info('📭 No orders submitted yet. Add your first order above!')


# ==================== Main Entry Point ====================

def main():
    # Load users from file
    st.session_state.users = load_users()
    
    if not st.session_state.user_logged_in:
        registration_page()
    else:
        main_app()


if __name__ == '__main__':
    main()