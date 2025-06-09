import streamlit as st
import pandas as pd
from html import escape

# Function to generate HTML table with premium styling
def generate_html_table(df, columns, image_col):
    html = '''
    <div class="table-container">
        <table class="luxury-table">
            <thead>
                <tr>
    '''
    
    # Add header columns
    for col in columns:
        html += f'<th><span class="header-text">{escape(col.title())}</span></th>'
    html += '</tr></thead><tbody>'
    
    # Add data rows
    for index, row in df.iterrows():
        html += '<tr class="table-row">'
        for col in columns:
            cell_value = str(row[col]) if pd.notna(row[col]) else ''
            if col == image_col and cell_value:
                images = cell_value.split(',')
                first_image = images[0].strip()
                cell_content = f'''<div class="image-preview">
                    <img src="{first_image}" class="product-image" onerror="this.style.display='none'">
                    <div class="image-overlay">
                        <span class="view-text">View</span>
                    </div>
                </div>'''
                data_type = 'image'
                data_content = escape(cell_value)
            else:
                highlight = cell_value[:50] + '...' if len(cell_value) > 50 else cell_value
                cell_content = f'<span class="cell-text">{escape(highlight)}</span>'
                data_type = 'text'
                data_content = escape(cell_value)
            
            html += f'''<td class="table-cell" data-type="{data_type}" data-content="{data_content}">
                <div class="cell-content">
                    {cell_content}
                    <button class="expand-btn" aria-label="Expand content">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M7 13l3 3 7-7"/>
                        </svg>
                    </button>
                </div>
            </td>'''
        html += '</tr>'
    
    html += '</tbody></table></div>'
    return html

# Enhanced Modal and JavaScript with luxury styling
modal_js = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --primary-gold: #D4AF37;
        --dark-gold: #B8962E;
        --luxury-black: #0A0A0A;
        --charcoal: #1A1A1A;
        --dark-grey: #2A2A2A;
        --light-grey: #F5F5F5;
        --white: #FFFFFF;
        --shadow-light: rgba(212, 175, 55, 0.1);
        --shadow-medium: rgba(0, 0, 0, 0.3);
        --shadow-heavy: rgba(0, 0, 0, 0.6);
    }
    
    .table-container {
        background: linear-gradient(135deg, var(--charcoal) 0%, var(--dark-grey) 100%);
        border-radius: 20px;
        padding: 0;
        box-shadow: 0 20px 60px var(--shadow-heavy);
        overflow: hidden;
        border: 1px solid rgba(212, 175, 55, 0.2);
    }
    
    .luxury-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: 'Inter', sans-serif;
        background: transparent;
    }
    
    .luxury-table thead th {
        background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
        color: var(--luxury-black);
        padding: 20px 16px;
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        position: sticky;
        top: 0;
        z-index: 100;
        border: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .luxury-table thead th:first-child {
        border-radius: 0;
    }
    
    .luxury-table thead th:last-child {
        border-radius: 0;
    }
    
    .header-text {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .table-row {
        background: var(--charcoal);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .table-row:hover {
        background: linear-gradient(135deg, var(--dark-grey) 0%, rgba(212, 175, 55, 0.05) 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.1);
    }
    
    .table-cell {
        padding: 20px 16px;
        border: none;
        color: var(--white);
        font-size: 13px;
        line-height: 1.6;
        vertical-align: middle;
        position: relative;
    }
    
    .cell-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    
    .cell-text {
        flex: 1;
        font-weight: 400;
    }
    
    .image-preview {
        position: relative;
        width: 80px;
        height: 80px;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .image-preview:hover {
        border-color: var(--primary-gold);
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
    }
    
    .product-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    
    .image-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .image-preview:hover .image-overlay {
        opacity: 1;
    }
    
    .view-text {
        color: var(--primary-gold);
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .expand-btn {
        background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
        color: var(--luxury-black);
        border: none;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        opacity: 0.8;
    }
    
    .expand-btn:hover {
        transform: scale(1.1) rotate(90deg);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
        opacity: 1;
    }
    
    #modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 2000;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, var(--charcoal) 0%, var(--dark-grey) 100%);
        border-radius: 20px;
        padding: 40px;
        max-width: 90vw;
        max-height: 90vh;
        overflow: auto;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.3);
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { 
            opacity: 0;
            transform: translate(-50%, -60%);
        }
        to { 
            opacity: 1;
            transform: translate(-50%, -50%);
        }
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 20px;
    }
    
    .modal-title {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 600;
        color: var(--primary-gold);
        margin: 0;
    }
    
    .close-btn {
        background: none;
        border: none;
        color: var(--white);
        font-size: 28px;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.3s ease;
    }
    
    .close-btn:hover {
        background: rgba(212, 175, 55, 0.2);
        color: var(--primary-gold);
        transform: rotate(90deg);
    }
    
    .modal-body {
        color: var(--white);
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    .modal-images {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .modal-image {
        width: 100%;
        max-width: 400px;
        height: auto;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease;
    }
    
    .modal-image:hover {
        transform: scale(1.02);
    }
    
    /* Scrollbar styling */
    .modal-content::-webkit-scrollbar {
        width: 8px;
    }
    
    .modal-content::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    .modal-content::-webkit-scrollbar-thumb {
        background: var(--primary-gold);
        border-radius: 4px;
    }
    
    .modal-content::-webkit-scrollbar-thumb:hover {
        background: var(--dark-gold);
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid rgba(212, 175, 55, 0.3);
        border-radius: 50%;
        border-top-color: var(--primary-gold);
        animation: spin 0.8s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>

<div id="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 class="modal-title">Product Details</h3>
            <button class="close-btn" id="close-modal">&times;</button>
        </div>
        <div class="modal-body" id="modal-body"></div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Handle expand button clicks
    document.querySelectorAll('.expand-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            
            const cell = btn.closest('.table-cell');
            const dataType = cell.getAttribute('data-type');
            const content = cell.getAttribute('data-content');
            const modalBody = document.getElementById('modal-body');
            
            if (dataType === 'image') {
                const images = content.split(',');
                const imageGrid = images.map(img => 
                    `<img src="${img.trim()}" class="modal-image" onerror="this.style.display='none'" loading="lazy">`
                ).join('');
                modalBody.innerHTML = `<div class="modal-images">${imageGrid}</div>`;
            } else {
                modalBody.textContent = content;
            }
            
            document.getElementById('modal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    });
    
    // Handle image preview clicks
    document.querySelectorAll('.image-preview').forEach(preview => {
        preview.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            
            const cell = preview.closest('.table-cell');
            const content = cell.getAttribute('data-content');
            const modalBody = document.getElementById('modal-body');
            
            const images = content.split(',');
            const imageGrid = images.map(img => 
                `<img src="${img.trim()}" class="modal-image" onerror="this.style.display='none'" loading="lazy">`
            ).join('');
            modalBody.innerHTML = `<div class="modal-images">${imageGrid}</div>`;
            
            document.getElementById('modal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    });
    
    // Close modal functionality
    function closeModal() {
        document.getElementById('modal').style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    document.getElementById('close-modal').addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    document.getElementById('modal').addEventListener('click', (e) => {
        if (e.target.id === 'modal') {
            closeModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.getElementById('modal').style.display === 'block') {
            closeModal();
        }
    });
});
</script>
"""

# Enhanced CSS for luxury styling
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --primary-gold: #D4AF37;
        --dark-gold: #B8962E;
        --luxury-black: #0A0A0A;
        --charcoal: #1A1A1A;
        --dark-grey: #2A2A2A;
        --light-grey: #F5F5F5;
        --white: #FFFFFF;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--luxury-black) 0%, var(--charcoal) 50%, var(--dark-grey) 100%);
        color: var(--white);
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Header Styling */
    h1 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        font-size: 3rem !important;
        text-align: center !important;
        background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 3rem !important;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: linear-gradient(135deg, var(--charcoal) 0%, var(--dark-grey) 100%);
        border: 2px dashed var(--primary-gold);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--dark-gold);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
        transform: translateY(-2px);
    }
    
    .stFileUploader label {
        color: var(--primary-gold) !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%) !important;
        color: var(--luxury-black) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Input styling */
    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stSelectbox > div > div {
        background: var(--dark-grey) !important;
        color: var(--white) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > input:focus,
    .stNumberInput > div > input:focus,
    .stSelectbox > div > div:focus {
        border-color: var(--primary-gold) !important;
        box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2) !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div {
        background: var(--dark-grey) !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect .st-emotion-cache-1dp5vir {
        background: var(--primary-gold) !important;
        color: var(--luxury-black) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--charcoal) 0%, var(--dark-grey) 100%) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 12px !important;
        color: var(--primary-gold) !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary-gold) !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--charcoal) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Labels */
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stMultiSelect label {
        color: var(--primary-gold) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%) !important;
        border: 1px solid var(--primary-gold) !important;
        border-radius: 12px !important;
        color: var(--white) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%) !important;
        border: 1px solid #dc3545 !important;
        border-radius: 12px !important;
        color: var(--white) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--charcoal);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-gold);
    }
</style>
"""

# Streamlit app
st.set_page_config(
    page_title="Luxury Fashion Collection", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(css, unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>Luxury Fashion Collection</h1>
    <p style="font-family: 'Inter', sans-serif; font-size: 1.2rem; color: #D4AF37; font-weight: 300; letter-spacing: 1px;">
        Discover Exceptional Craftsmanship & Timeless Elegance
    </p>
</div>
""", unsafe_allow_html=True)

# File upload section
uploaded_file = st.file_uploader(
    "Upload Your Collection Data", 
    type=["xlsx", "xls"],
    help="Upload an Excel file containing your luxury product collection data"
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        columns = df.columns.tolist()

        # Identify image column
        image_col = next((col for col in columns if "image" in col.lower()), None)

        # Determine column types
        col_types = {}
        for col in columns:
            if df[col].dtype == 'object':
                unique_ratio = len(df[col].dropna().unique()) / len(df[col].dropna()) if len(df[col].dropna()) > 0 else 0
                if unique_ratio < 0.05 and col != image_col:
                    col_types[col] = 'categorical'
                else:
                    col_types[col] = 'text'
            elif df[col].dtype in ['int64', 'float64']:
                col_types[col] = 'numerical'
            else:
                col_types[col] = 'text'

        # Advanced Filters
        with st.expander("🔍 Advanced Filters", expanded=False):
            st.markdown("*Refine your collection view with precision*")
            filter_dict = {}
            filter_cols = [col for col in columns if col != image_col]
            
            # Create dynamic columns based on number of filters
            num_cols = min(3, len(filter_cols))
            if num_cols > 0:
                for i in range(0, len(filter_cols), num_cols):
                    cols = st.columns(num_cols)
                    for j, col in enumerate(filter_cols[i:i+num_cols]):
                        if j < len(cols):
                            with cols[j]:
                                if col_types[col] == 'categorical':
                                    options = [str(x) for x in df[col].dropna().unique()]
                                    filter_dict[col] = st.multiselect(
                                        f"{col.title()}", 
                                        options=options, 
                                        key=f"filter_{col}",
                                        help=f"Filter by {col.lower()}"
                                    )
                                elif col_types[col] == 'numerical':
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        min_val = st.number_input(
                                            f"Min {col.title()}", 
                                            value=float(df[col].min()), 
                                            key=f"min_{col}"
                                        )
                                    with col2:
                                        max_val = st.number_input(
                                            f"Max {col.title()}", 
                                            value=float(df[col].max()), 
                                            key=f"max_{col}"
                                        )
                                    filter_dict[col] = {'min': min_val, 'max': max_val}
                                elif col_types[col] == 'text':
                                    filter_dict[col] = st.text_input(
                                        f"Search {col.title()}", 
                                        key=f"filter_{col}",
                                        help=f"Search within {col.lower()}"
                                    )

        # Apply filters
        filtered_df = df.copy()
        for col, filter_val in filter_dict.items():
            if col_types[col] == 'categorical' and filter_val:
                filtered_df = filtered_df[filtered_df[col].astype(str).isin(filter_val)]
            elif col_types[col] == 'numerical':
                min_val = filter_val['min']
                max_val = filter_val['max']
                filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
            elif col_types[col] == 'text' and filter_val:
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(filter_val, case=False, na=False)]

        # Display collection stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Products", len(filtered_df), delta=len(filtered_df) - len(df) if len(filtered_df) != len(df) else None)
        with col2:
            st.metric("Categories", len([c for c in columns if col_types.get(c) == 'categorical']))
        with col3:
            st.metric("Columns", len(columns))

        # Generate and display the luxury table
        if len(filtered_df) > 0:
            html_table = generate_html_table(filtered_df, columns, image_col)
            st.components.v1.html(
                f'<div style="margin: 2rem 0;">{html_table}</div>{modal_js}',
                height=700
            )
        else:
            st.warning("No products match your current filters. Please adjust your criteria.")
            
    except Exception as e:
        st.error(f"Error processing your collection data: {str(e)}")
        st.info("Please ensure your Excel file is properly formatted and try again.")
else:
    # Welcome message when no file is uploaded
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, rgba(42, 42, 42, 0.3) 0%, rgba(26, 26, 26, 0.3) 100%); border-radius: 20px; margin: 2rem 0; border: 1px solid rgba(212, 175, 55, 0.2);">
        <div style="margin-bottom: 2rem;">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="1" style="margin-bottom: 1rem;">
                <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
                <path d="m3.3 7 8.7 5 8.7-5"/>
                <path d="M12 22V12"/>
            </svg>
        </div>
        <h3 style="color: #D4AF37; font-family: 'Playfair Display', serif; margin-bottom: 1rem; font-size: 1.8rem;">
            Welcome to Your Luxury Collection Manager
        </h3>
        <p style="color: #F5F5F5; font-family: 'Inter', sans-serif; font-size: 1.1rem; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            Transform your product catalog into an elegant, interactive experience. Upload your Excel file to begin showcasing your luxury collection with sophisticated filtering and detailed product views.
        </p>
        <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(212, 175, 55, 0.1); border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3);">
            <h4 style="color: #D4AF37; font-family: 'Playfair Display', serif; margin-bottom: 1rem;">
                Features & Benefits
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; text-align: left;">
                <div>
                    <h5 style="color: #D4AF37; margin-bottom: 0.5rem;">📊 Smart Filtering</h5>
                    <p style="color: #F5F5F5; font-size: 0.9rem; margin: 0;">Advanced filters for categories, price ranges, and text search</p>
                </div>
                <div>
                    <h5 style="color: #D4AF37; margin-bottom: 0.5rem;">🖼️ Image Galleries</h5>
                    <p style="color: #F5F5F5; font-size: 0.9rem; margin: 0;">Beautiful product image previews with expandable galleries</p>
                </div>
                <div>
                    <h5 style="color: #D4AF37; margin-bottom: 0.5rem;">📱 Responsive Design</h5>
                    <p style="color: #F5F5F5; font-size: 0.9rem; margin: 0;">Optimized for desktop, tablet, and mobile viewing</p>
                </div>
                <div>
                    <h5 style="color: #D4AF37; margin-bottom: 0.5rem;">✨ Luxury Aesthetics</h5>
                    <p style="color: #F5F5F5; font-size: 0.9rem; margin: 0;">Premium styling that reflects your brand's sophistication</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)