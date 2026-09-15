import streamlit as st 


st.title("Hi Welcome To The Cricket Analysis Predictor ! ")
col1 , col2 = st.columns(2)


with col1:
   st.image("https://images.pexels.com/photos/20896073/pexels-photo-20896073.jpeg")
   pass 
with col2:
   st.image("https://images.pexels.com/photos/20896073/pexels-photo-20896073.jpeg")
   pass 
Score = st.sidebar.number_input("Score : " , min_value= 0 , step = 1)
st.selectbox("Select Your Favourite Team ! : " , ['Pakistan', 'India' , 'Australia' , 'New-Zealand' , 'England'])
st.slider("Innings " , 0  , 1 , 0)
if Score:
   print(f"You Selected Score Is {Score}")
 