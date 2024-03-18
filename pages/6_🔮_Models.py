import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
import config
import umap
import pandas as pd
import seaborn as sns
import itertools

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_curve, confusion_matrix, plot_confusion_matrix, classification_report
from sklearn.model_selection import train_test_split, StratifiedGroupKFold

st.title('Models')

@st.cache(allow_output_mutation=True)
def load_vecs():
	dfv = pd.read_json('data/frogid_v3_chunked_3.json')
	dfv['id'] = dfv.filename.map(lambda x: x.split('-')[0])
	dfv['n_chunks'] = dfv.groupby(['id'])['filename'].transform('count')
	return dfv

# Load vectors & inner join
dfv = load_vecs()
dfv['label'] = dfv.filename.map(st.session_state['labels'])
st.write('Original size:', len(dfv))
dfv = dfv[~dfv.label.isnull()]
dfv['label_str'] = dfv.label.map(lambda x: ','.join(x))
st.write('Munged size:', len(dfv))
st.write(dfv.head(20))

# Find unique labels
all_labels = dfv.label.tolist()
all_labels = sorted(set(list(itertools.chain.from_iterable(all_labels))))

# Choose one
label = st.selectbox('Choose label:', all_labels)

# Prepare for modelling
y = dfv.label.map(lambda x: label in x).astype('int').tolist()
X = dfv.vector.tolist()
g = dfv.id.tolist()
s = 1/dfv.n_chunks

# Diagnostics
st.write('Number positive labels:', np.sum(y), 'out of', len(y))

# Build the LR
cv = StratifiedGroupKFold(n_splits=5)
do_gridsearch = st.checkbox('Perform grid search for regularisation C?')

if do_gridsearch:
	cs = [0.001, 0.01, 0.1, 0.5, 1.0]
	aa = []
	for c in cs:
		lr = LogisticRegression(class_weight='balanced', C=c)
		with st.spinner('Building model... {} of {}'.format(len(aa)+1, len(cs))):
			y_pred = cross_val_predict(lr, X, y, groups=g, cv=cv, fit_params={'sample_weight':s})
		dfv['pred'] = y_pred
		dfv['correct'] = (y == y_pred).astype('int')
		a = round(100*dfv.correct.mean(),2)
		aa.append(a)
		st.write('C={}, Acc={}'.format(c, a))
	lr = LogisticRegression(class_weight='balanced', C=cs[np.argmin(aa)])

else:
	# Build final model
	lr = LogisticRegression(class_weight='balanced')

with st.spinner('Building final model'):
	y_pred = cross_val_predict(lr, X, y, groups=g, cv=cv, fit_params={'sample_weight':s})	
	dfv['pred'] = y_pred
	dfv['correct'] = (y == y_pred).astype('int')
	a = round(100*dfv.correct.mean(),2)
	st.write('Overall accuracy:', a)
	st.write('Num correct', len(dfv[dfv.correct==1]))
	st.write('Num incorrect', len(dfv[dfv.correct==0]))
	#st.write(dfv[dfv.correct==0].label.value_counts())
	st.write(dfv[dfv.correct==0].groupby('label_str').agg({'filename':'count', 'id':pd.Series.nunique}))