import streamlit as st
import pandas as pd
#import numpy as np
import pickle
import requests
import csv
from io import StringIO


from image_loader import render_image

from sklearn.ensemble import GradientBoostingClassifier

def createCols ():

  cols = []
  if cl:
    cols.append("classMove")
  if da:
    cols.append("daysLto")
  if tr:
    cols.append("TRinrace")
  if jo:
    cols.append("Jockinrace")
  if si:
    cols.append("Sireinrace")
  if pa:
    cols.append("paceFig")

  return cols

############################################

def predModel():

    global cols,decs,horses

    try:

      fileName = "models/"
      for col in decs.columns:
        fileName = fileName + col[0:2]
      fileName = fileName + '.sav'

      #try:
      with open(fileName, "rb") as f:
        m = pickle.load(f)
        for col in cols:
          decs[col] = pd.to_numeric(decs[col], errors='coerce') # convert from string to numeric or NaN
          decs[col] = decs[col].fillna(m.repNaNs[col])
      #except Exception as e:
        #print ('EXCEPTION ',e)

      preds = m.predict_proba(decs)
      preds = preds[:,1:]
      #preds = np.around(preds,decimals=3)
      ratings = pd.DataFrame()
      ratings['Horse'] = horses
      ratings['Rating'] = preds * 100
      ratings = ratings.sort_values('Rating', ascending=False)
      with inputs:
        with rescol:
          st.dataframe(ratings, hide_index=True)
    except Exception as e:
      with inputs:
        with rescol:
          st.write ('Error No Predictors ? ', e)

#########################################

#decs = pd.read_csv('http://www.smartersig.com/mysportsaisample.csv')
#requests.packages.urllib3.disable_warnings()

#response = requests.get('http://www.smartersig.com/utils/mysportsaisample.csv', auth=(st.secrets['siguser'], #st.secrets['sigpassw']), verify=False)
#decoded_content = response.content.decode('utf-8')
#cr = csv.reader(decoded_content.splitlines(), delimiter=',')
#my_list = list(cr)

#print ('Debugging')
#st.write(my_list)
## the above loads as strings ##

def load_data():
    url = "http://www.smartersig.com/utils/mysportsaisample.csv"
    
    # Make the request look more like a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/csv, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "http://www.smartersig.com/",
        "Connection": "keep-alive"
    }
    
    try:
        response = requests.get(
            url,
            auth=(st.secrets["siguser"], st.secrets["sigpassw"]),
            headers=headers,
            verify=False,      # Keep only if necessary
            timeout=20
        )
        
        st.write(f"Debug: Status code = {response.status_code}")   # Temporary debug
        
        response.raise_for_status()
        
        decs = pd.read_csv(
            StringIO(response.text),
            on_bad_lines='skip',
            dtype=str
        )
        
        return decs
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            st.error("403 Forbidden: The server is blocking requests from Streamlit Cloud.")
            st.error("This is usually due to IP blocking or missing browser-like headers.")
            # Show first part of response for debugging
            st.write("Response content preview:", response.text[:800])
        else:
            st.error(f"HTTP Error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return pd.DataFrame()

# Call it
decs = load_data()

if len(decs) == 0:
  st.write('No races today')
else:
  #header = my_list[0]
  #decs = pd.DataFrame(my_list[1:], columns=header)
  trackTime = decs.iloc[0]['trackTimeDate']
  tt = trackTime.split('_')
  trackTime = tt[0][0:4] + ' ' + tt[1]
  horses = decs['horse']

  header = st.container()
  inputs = st.container()

  with header:
    render_image("MLImage5.png")
    st.title('MySportsAILite')

  with inputs:
    inputcol, rescol = st.columns([1, 1])
    with rescol:
      line = 'Ratings ' + trackTime
      st.subheader(line)
    with inputcol:
      st.subheader('Choose Inputs')
      cl = st.checkbox('Class Move')
      da = st.checkbox('Days Since Last Run')
      tr = st.checkbox('Trainer Strike Rate')
      jo = st.checkbox('Jockey Strike Rate')
      si = st.checkbox('Sire Strike Rate')
      pa = st.checkbox('Pace Figure')
    
      cols = createCols()

  try:
    decs = decs[cols]
  except Exception as e:
    print ('error ',e)

  with inputs:
    with inputcol:
      if st.button("Predict"):
        predModel()
      st.write('MySportsAI has over 90 predictors to choose from www.smartersig.com/mysportsai.php')

