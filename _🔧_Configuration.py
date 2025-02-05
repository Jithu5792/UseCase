import os
import streamlit as st
import PyPDF2
from PyPDF2 import PdfReader
import docx
#h1 tag
st.html(
    '<h1 align=center>Upload a File</h1>'
)

#Session state
if "file" not in st.session_state:
    st.session_state["file"]=""
#Pdf text extractor
def read_pdf(file_path):
    pdf = PdfReader(file_path)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text
#Doc text extractor
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
    return text
#File Uploader
file_path = st.file_uploader("",type=["pdf","docx","txt"])

if st.button('Submit'):
    if file_path:
        if file_path.type=='application/pdf':
                document_text = read_pdf(file_path)
                st.session_state["file"]=document_text
                st.success("File Upload Successfully")
        elif file_path.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                document_text = read_docx(file_path)
                st.session_state["file"]=document_text
                st.success("File Upload Successfully")
        elif file_path.type=="text/plain":
                document_text = file_path.read().decode('utf-8')
                st.session_state["file"]=document_text
                st.success("File Upload Successfully")
        else:
         st.error('Unsupported file format')
    else:
        st.warning("Please Upload a File")

















    

 


