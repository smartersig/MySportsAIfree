import streamlit as st
import pandas as pd
#import numpy as np
import pickle
import requests
import csv

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
      print ('filename ',fileName)

      #try:
      with open(fileName, "rb") as f:
        m = pickle.load(f)
        for col in cols:
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

response = requests.get('http://www.smartersig.com/utils/mysportsaisample.csv', auth=(st.secrets['siguser'], st.secrets['sigpassw']), verify=False)
decoded_content = response.content.decode('utf-8')
cr = csv.reader(decoded_content.splitlines(), delimiter=',')
my_list = list(cr)

if len(my_list) == 0:
  st.write('No races today')
else:
  decs = pd.DataFrame(my_list) #, index=None)

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

