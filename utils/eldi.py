import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SIZE_PROPORTION = 0.5 # hlutfall snemmbúimma vs. síðbúinna

LATE_RETURNS_PROP = 0.05 # fjöldi síðbúinna stokulaxa sem snúa aftur
EARLY_RETURNS_PROP = 0.05 # fjöldi snemmbúinna stokulaxa sem snúa aftur
EARLY_YEARLY_DISTR = [0,0.33,0.33,0.33] # dreifing á snemmbúnum stokulöxum yfir fjögur ár



## Hægt að breyta
@st.cache_data
def calcEscapeEvents(ITERS):
    # Reiknar fjölda atburða per ár ITERS ár
    escSchedule = np.array([2]*ITERS)
    return escSchedule

@st.cache_data
def splitEvents(escSchedule, ITERS):
    # Skiptir atburðum niður á eldisstaði eftir eldismagni
    farmNumbers = st.session_state['eldi'].index.to_numpy()
    stocks = st.session_state['eldi']['Stock'].to_numpy()
    stocksProbabilities = stocks/np.sum(stocks)
    farmEvents = pd.DataFrame(0, index=np.arange(ITERS), columns=farmNumbers)
    for i in range(ITERS):
        for j in range(escSchedule[i]):
            farm = np.random.choice(farmNumbers,p=stocksProbabilities)
            farmEvents.loc[i,farm] += 1
    return farmEvents

@st.cache_data
def splitFarmEvents(farmEvents,ITERS):
    # Skiptir atburðum niður eftir stærð stokulaxa

    farmEventsEarly, farmEventsLate = pd.DataFrame(0, index=np.arange(ITERS), columns=farmEvents.columns), pd.DataFrame(0, index=np.arange(ITERS), columns=farmEvents.columns)
    for i in range(ITERS):
        for farm in farmEvents.columns:
            for j in range(farmEvents.loc[i,farm]):
                if np.random.uniform(0,1) < SIZE_PROPORTION:
                    farmEventsLate.loc[i,farm] += 1
                else:
                    farmEventsEarly.loc[i,farm] += 1
    return farmEventsEarly, farmEventsLate

@st.cache_data
def getSizeOfEvents(farmEventsEarly, farmEventsLate):
    # Reiknar meðalstærð atburða á eldisstað

    def getSizeOfEvents(numberOfEvents):
        # slembifall sem gefur stærð strokatburðar
        number = 0
        for i in range(numberOfEvents):
            number += np.random.normal(0, 1, 1)[0]*10+100
        return number
    

    farmNumbersEarly = farmEventsEarly.map(getSizeOfEvents)
    farmNumbersLate = farmEventsLate.map(getSizeOfEvents)

    return farmNumbersEarly, farmNumbersLate

@st.cache_data
def getNumberOfReturners(farmNumbersEarly, farmNumbersLate, ITERS):
    farmEarlyReturns = pd.DataFrame(0, index=np.arange(ITERS), columns=farmNumbersEarly.columns)
    farmLateReturns = farmNumbersLate.map(lambda x: round(x*LATE_RETURNS_PROP))
    # Reiknar fjölda stokulaxa
    for i in range(ITERS):
        for farm in farmNumbersEarly.columns:
            for j in range(len(EARLY_YEARLY_DISTR)):
                if i+j < ITERS:
                    farmEarlyReturns.loc[i+j,farm] += round(farmNumbersEarly.loc[i,farm]*EARLY_RETURNS_PROP*EARLY_YEARLY_DISTR[j])

    return farmEarlyReturns, farmLateReturns

## Óþarfi að breyta
def updateEldi(key):
    st.session_state['eldi'].loc[st.session_state['eldi']['Stytting'] == key, 'Stock'] = st.session_state[key]

def plotEldi(ax, farm, plotType,farmEventsEarly, farmEventsLate,farmNumbersEarly, farmNumbersLate,farmEarlyReturns, farmLateReturns):
    if farm == 'Heild':
        farmEventsEarly[0] = farmEventsEarly.sum(axis=1)
        farmEventsLate[0] = farmEventsLate.sum(axis=1)
        farmNumbersEarly[0] = farmNumbersEarly.sum(axis=1)
        farmNumbersLate[0]= farmNumbersLate.sum(axis=1)
        farmEarlyReturns[0] = farmEarlyReturns.sum(axis=1)
        farmLateReturns[0] = farmLateReturns.sum(axis=1)
        print(farmNumbersEarly.sum(axis=1).sum())
        print(farmNumbersLate.sum(axis=1).sum())
        farmNo = 0
    else:
        farmDict = pd.Series(st.session_state['eldi'].index, index=st.session_state['eldi']['Nafn'].values).to_dict()
        farmNo = farmDict[farm]

    if plotType == 'Atburðir':
        ax.bar(farmEventsEarly.iloc[0:100].index, farmEventsEarly.iloc[0:100][farmNo], label='Snemmbúnir')
        ax.bar(farmEventsLate.iloc[0:100].index, farmEventsLate.iloc[0:100][farmNo], bottom = farmEventsEarly.iloc[0:100][farmNo], label='Síðbúnir')
        ax.set_ylabel('Fjöldi atburða')
    elif plotType == 'Strokfjöldi':
        ax.bar(farmNumbersEarly.iloc[0:100].index, farmNumbersEarly.iloc[0:100][farmNo], label='Snemmbúnir')
        ax.bar(farmNumbersLate.iloc[0:100].index, farmNumbersLate.iloc[0:100][farmNo], bottom = farmNumbersEarly.iloc[0:100][farmNo], label='Síðbúnir')
        ax.set_ylabel('Fjöldi stokulaxa')
    else:
        ax.bar(farmEarlyReturns.iloc[0:100].index, farmEarlyReturns.iloc[0:100][farmNo], label='Snemmbúnir')
        ax.bar(farmLateReturns.iloc[0:100].index, farmLateReturns.iloc[0:100][farmNo], bottom = farmEarlyReturns.iloc[0:100][farmNo], label='Síðbúnir')
        ax.set_ylabel('Fjöldi endurkomulaxa')
    ax.legend()
    ax.set_title(f'{plotType} fyrstu 100 árin')
    ax.set_xlabel('Ár')
    return ax