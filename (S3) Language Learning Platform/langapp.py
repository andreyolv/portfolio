import streamlit as st
import pandas as pd

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

#-----------------------------------------------------------------------------------
# HEAD PAGE
st.write("""
# Language Learning
This app ....!

Enter all info in left side bar to filter what you want
***
""")

#-----------------------------------------------------------------------------------
# SIDE BAR
# Sidebar - Selecting Native Language
languages = ["Portuguese", "English", "Spanish", "French", "Italian", "German"]
native_language = st.sidebar.selectbox('Select your native language', languages)

# Sidebar - Selecting Learning Language
learning_languages = st.sidebar.multiselect('Select the languages you are learning', languages)

# Sidebar - Selecting Learning Plan
pl = ["1000 most commom words", "3000 most commom words", "50 Languages", "Glossika Mass Sentences"]
plan = st.sidebar.selectbox('Select the mode of sentences will show', pl)

# Sidebar - Selecting Mode
md = ["Ordered", "Random"]
mode = st.sidebar.selectbox('Select the mode of sentences will show', md)

# Sidebar - Selecting Level
if plan == "50 Languages":
    level = st.sidebar.slider('Select the level of sentences', 0, 100, (0,10))
if plan == "Glossika Mass Sentences":
    level = st.sidebar.slider('Select the level of sentences', 0, 3000, (0,500))

#-----------------------------------------------------------------------------------
# MAIN CODE
# Loading Data
# df = pd.read_excel("Glo1 ONE - ALL.xlsx")



#-----------------------------------------------------------------------------------
# MAINPAGE DASHBOARD
# Native Language Sentence
st.title('Translate this Sentences')
col1, col2 = st.columns(2)
with col1:
    st.subheader(native_language)
    st.text("Sentence hahaha")
with col2:
    st.subheader("")
    file = "text.mp3"
    st.audio(file)

if st.button('Next sentence'):
    if mode == "Ordered":
        # df.
        a = 1
    if mode == "Random":
        # df.sample()
        b = 2

st.write("***")

#------------------------------------
# Learning Languages Sentences
st.header('Learning Sentences')

if st.button('Show me the sentences'):
    for lang in learning_languages:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(lang)
            st.text("Sentence hahaha")
        with col2:
            st.subheader("")
            file = "text.mp3"
            st.audio(file)
st.write("***")