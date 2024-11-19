import streamlit as st
import pandas as pd
import numpy as np
from utils.stofn import *
from utils.eldi import *
from utils.dreifing import *
from utils.gogn import *
import random
st.set_page_config(layout="wide")

random.seed(0)
ITERS = 1000

## Setup
if 'rivers' not in st.session_state:
    st.session_state['rivers'] = getRivers()
if 'eldi' not in st.session_state:
    st.session_state['eldi'] = getFarms()
if 'settings' not in st.session_state:
    st.session_state['settings'] = getSetings()

st.header('Áhættumat 2024')
tab1, tab2, tab3, tab4 = st.tabs(['Laxastofn', 'Strok', 'Dreifing', 'Niðurstaða'])


## Laxastofn
river = tab1.selectbox(
    "Veldu á",
    ['Heild'] + list( st.session_state['rivers']['nafn']),
)
riverPlotType = tab1.pills(
    "Tegund grafs",
    options=['Tímalína', 'Stuðlarit'],
    selection_mode="single",
    default = 'Tímalína'
)
stofnar = stofnstaerdir(ITERS)
f, ax = plt.subplots()
plotStofnstaerdir(ax, stofnar, river, riverPlotType, ITERS)
tab1.pyplot(f)

## Strok
col31,col32 = tab2.columns([3, 1])
eldismagn = col32.expander('Eldismagn')
poisson = col32.expander('Meðaltímalengd milli atburða')
staerd = col32.expander('Stærð atburða')
eldisstudlar = col32.expander('Eldisstuðlar')

col311, col312, col313 = col31.columns([1, 1,1 ])

for eldisIdx in st.session_state['eldi'].index:
    row = st.session_state['eldi'].iloc[eldisIdx]
    eldismagn.slider(row['Nafn'], 0.0, row['max'], row['Stock'], step = 0.5, key = row['Stytting'], on_change=updateEldi, args=(row['Stytting'],))

escSchedule = calcEscapeEvents(ITERS)
farmEvents = splitEvents(escSchedule, ITERS)
farmEventsEarly, farmEventsLate = splitFarmEvents(farmEvents,ITERS)
farmNumbersEarly, farmNumbersLate = getSizeOfEvents(farmEventsEarly, farmEventsLate)
farmEarlyReturns, farmLateReturns = getNumberOfReturners(farmNumbersEarly, farmNumbersLate, ITERS)

col311.metric('Meðalfjöldi atburða á ári', escSchedule.mean())
col312.metric('Meðalfjöldi stroka á ári', round((farmNumbersEarly.to_numpy().sum()+farmNumbersLate.to_numpy().sum())/1000))
col313.metric('Meðalfjöldi endurkomulaxa á ári', round((farmEarlyReturns.to_numpy().sum()+farmLateReturns.to_numpy().sum())/1000))

f2, ax2 = plt.subplots()
eldi = col31.selectbox(
    "Veldu eldisstað",
    ['Heild'] + list( st.session_state['eldi']['Nafn']),
)
eldiPlotType = col31.pills(
    "Graf",
    options=['Atburðir', 'Strokfjöldi', 'Endurkomulaxar'],
    selection_mode="single",
    default = 'Atburðir'
)
ax2 = plotEldi(ax2, eldi, eldiPlotType, farmEventsEarly, farmEventsLate, farmNumbersEarly, farmNumbersLate, farmEarlyReturns, farmLateReturns)
col31.pyplot(f2)

## Dreifing

f3, ax3 = plt.subplots()
eldi2 = tab3.selectbox(
    "Veldu eldisstað",
    list( st.session_state['eldi']['Nafn']),
    key = 'eldi2'
)
dreifingPlotType = tab3.pills(
    "Graf",
    options=['Snemmbúnir', 'Síðbúnir'],
    selection_mode="single",
    default = 'Snemmbúnir'
)
plotDistribution(ax3, dreifingPlotType, eldi2)
tab3.pyplot(f3)



## Niðurstaða
results = getResults(stofnar, farmEarlyReturns, farmLateReturns, ITERS)
f4, ax4 = plt.subplots()
river2 = tab4.selectbox(
    "Veldu á",
    ['Heild'] + list( st.session_state['rivers']['nafn']),
    key = 'river2'
)
plotResult(ax4, river2, results)
tab4.pyplot(f4)