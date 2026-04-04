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
    url = "http://www.smartersig.com/mysportsaisample.csv"   # Use the protected URL if needed
    
    try:
        response = requests.get(
            url,
            auth=(st.secrets["siguser"], st.secrets["sigpassw"]),
            verify=False,      # Remove or set to True in production if possible
            timeout=20
        )
        response.raise_for_status()  # Will raise if not successful (e.g. 401, 404)
        
        # Parse the CSV safely
        decs = pd.read_csv(
            StringIO(response.text),
            on_bad_lines='skip',   # Skip any problematic rows
            dtype=str              # Read as strings to avoid type inference issues
        )
        return decs
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data from server: {str(e)}")
        if "401" in str(e) or "Unauthorized" in str(e):
            st.error("Authentication failed – check your secrets (siguser / sigpassw)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error parsing CSV: {str(e)}")
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

