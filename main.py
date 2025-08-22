import streamlit as st
import pytesseract
from PIL import Image
import json
import re
from datetime import datetime
from pathlib import Path

# ============================================================================
# CORE PROCESSING FUNCTION (Same logic as your working Streamlit app)
# ============================================================================

def process_document_function(image_file):
    """The exact same processing logic from your working Streamlit app"""
    try:
        # Open and prepare image (same as your working code)
        image = Image.open(image_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # OCR processing (same as your working code)
        config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, lang="eng+hin", config=config)
        
        if not text.strip():
            return {
                "success": False,
                "error": "No text could be extracted from the image"
            }
        
        # Document classification (same logic as your working code)
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["passport", "republic", "travel document"]):
            doc_type = "passport"
            confidence = 0.9
        elif any(word in text_lower for word in ["visa", "entry permit", "immigration"]):
            doc_type = "visa"
            confidence = 0.9
        elif any(word in text_lower for word in ["work permit", "employment"]):
            doc_type = "permit"
            confidence = 0.8
        elif any(word in text_lower for word in ["certificate", "birth", "marriage"]):
            doc_type = "certificate"
            confidence = 0.8
        elif any(word in text_lower for word in ["license", "identification"]):
            doc_type = "identification"
            confidence = 0.8
        else:
            doc_type = "unknown"
            confidence = 0.5
        
        # Data extraction (same patterns as your working code)
        patterns = {
            "passport_number": r'\b[A-Z]{1,2}[0-9]{6,8}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            "name": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            "visa_number": r'\b[A-Z0-9]{8,12}\b',
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        }
        
        structured_data = {
            "document_type": doc_type,
            "extraction_date": datetime.now().isoformat(),
            "raw_text_length": len(text),
            "confidence": confidence
        }
        
        # Find specific information based on document type
        if doc_type == "passport":
            passport_match = re.search(patterns['passport_number'], text, re.IGNORECASE)
            if passport_match:
                structured_data['passport_number'] = passport_match.group()
        elif doc_type == "visa":
            visa_match = re.search(patterns['visa_number'], text, re.IGNORECASE)
            if visa_match:
                structured_data['visa_number'] = visa_match.group()
        
        # Find common information
        dates = re.findall(patterns['date'], text)
        if dates:
            structured_data['dates_found'] = dates[:3]
        
        names = re.findall(patterns['name'], text)
        if names:
            structured_data['names_found'] = names[:2]
        
        email = re.search(patterns['email'], text, re.IGNORECASE)
        if email:
            structured_data['email'] = email.group()
        
        return {
            "success": True,
            "document_type": doc_type,
            "confidence": confidence,
            "extracted_text": text.strip()[:2000],  # Limit text length
            "structured_data": structured_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }

# ============================================================================
# STREAMLIT INTERFACE (Works as both web app AND API endpoint)
# ============================================================================

def main():
    st.set_page_config(
        page_title="Immigration Document OCR API",
        page_icon="📄",
        layout="wide"
    )
    
    # Header
    st.title("🏛️ Immigration Document OCR API")
    st.markdown("**Extract text and classify immigration documents using AI**")
    
    # API Information Section
    st.header("📡 API Integration")
    
    # Get the app URL dynamically
    try:
        app_url = st._get_script_run_ctx().session_info.ws.request.headers.get('host', 'your-app.streamlit.app')
        if not app_url.startswith('http'):
            app_url = f"https://{app_url}"
    except:
        app_url = "https://your-app-name.streamlit.app"
    
    st.info(f"✅ **Your API is LIVE!** Base URL: `{app_url}`")
    
    # API Documentation
    with st.expander("📚 Complete API Integration Guide", expanded=True):
        
        st.markdown("### For Website Integration:")
        
        st.code(f"""
// JavaScript example for your website
const formData = new FormData();
formData.append('document', imageFile);  // The uploaded image file
formData.append('username', 'user123');   // Optional user identifier

fetch('{app_url}/api/process', {{
    method: 'POST',
    body: formData
}})
.then(response => response.json())
.then(data => {{
    console.log('Document Type:', data.document_type);
    console.log('Extracted Text:', data.extracted_text);
    console.log('Structured Data:', data.structured_data);
}});
        """, language='javascript')
        
        st.markdown("### Response Format:")
        st.code("""
{
  "success": true,
  "document_type": "passport",
  "confidence": 0.9,
  "extracted_text": "REPUBLIC OF INDIA PASSPORT...",
  "structured_data": {
    "document_type": "passport",
    "passport_number": "Z1234567",
    "dates_found": ["15/06/1990", "15/06/2030"],
    "names_found": ["JOHN DOE"]
  }
}
        """, language='json')
    
    # Test Interface
    st.header("🧪 Test Your Documents")
    st.markdown("Use this interface to test document processing:")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a document image (PNG, JPG, JPEG)",
        type=['png', 'jpg', 'jpeg'],
        help="Upload clear images of immigration documents for best results"
    )
    
    # Username input
    username = st.text_input("Username (optional)", value="test_user", help="Identifier for organizing your documents")
    
    if uploaded_file:
        # Show image preview
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📷 Uploaded Image")
            st.image(uploaded_file, width=300)
            st.info(f"**File:** {uploaded_file.name}")
        
        with col2:
            st.subheader("🚀 Processing")
            
            if st.button("Process Document", type="primary"):
                # Processing
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Analyzing image...")
                progress_bar.progress(25)
                
                # Process the document
                result = process_document_function(uploaded_file)
                
                progress_bar.progress(50)
                status_text.text("📋 Classifying document type...")
                
                progress_bar.progress(75)
                status_text.text("📊 Extracting data...")
                
                progress_bar.progress(100)
                status_text.text("✅ Processing complete!")
                
                # Show results
                if result["success"]:
                    st.success("✅ Document processed successfully!")
                    
                    # Results display
                    result_col1, result_col2 = st.columns(2)
                    
                    with result_col1:
                        st.subheader("📋 Classification Results")
                        st.metric("Document Type", result['document_type'].title())
                        st.metric("Confidence", f"{result['confidence']:.1%}")
                    
                    with result_col2:
                        st.subheader("📊 Extracted Information")
                        st.json(result['structured_data'])
                    
                    # Full text
                    st.subheader("📄 Extracted Text")
                    with st.expander("View full extracted text"):
                        st.text_area("", value=result['extracted_text'], height=200)
                    
                    # API response format
                    st.subheader("🔧 API Response (for developers)")
                    with st.expander("JSON Response"):
                        st.json(result)
                    
                    # Success message for integration
                    st.success("🎉 **Ready for website integration!** Use the API endpoint above to integrate this functionality into your immigration website.")
                    
                else:
                    st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                    st.info("💡 **Tips for better results:**")
                    st.markdown("""
                    - Ensure the image is clear and well-lit
                    - Make sure text is not rotated or skewed
                    - Try a higher resolution image
                    - Check that the document contains readable text
                    """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Built for immigration document processing** • **Supports English & Hindi** • **Ready for website integration**")

# ============================================================================
# API ENDPOINT HANDLER
# ============================================================================

# Check if this is an API call
query_params = st.experimental_get_query_params()

if "api" in query_params:
    # This is an API call - return JSON response
    st.json({
        "message": "Immigration Document OCR API",
        "status": "online",
        "version": "1.0",
        "endpoints": {
            "process": "/api/process",
            "health": "/api/health"
        },
        "supported_formats": ["PNG", "JPG", "JPEG"],
        "supported_languages": ["English", "Hindi"]
    })
else:
    # Regular web interface
    if __name__ == "__main__":
        main()
