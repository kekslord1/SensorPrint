"""
Enthält die Funktion 'Aufbereitung', welche die aus NX generierten Dateien mit Druck und Zugspannungen einliest, 
verarbeitet diese und ein Modellbild und ein Bild mit den Werten in den aktuellen Arbeitsordner abspeichert.

Author: Philipp Haug
Date: 24.05.2023
Version: 3.1
"""

import matplotlib.pyplot as plt
import pandas as pd

def Aufbereitung(MinPrincipal, MaxPrincipal, path):
    """Liest die aus NX generierten Dateien mit Druck und Zugspannungen ein, verarbeitet diese und speichert ein Modellbild 
    und ein Bild mit den Werten in den aktuellen Arbeitsordner

    Args:
        MinPrincipal (str) : Name der MinPrincipal.csv Datei mit den Druckspannungen
        MaxPrincipal (str) : Name der MaxPrincipal.csv Datei mit den Zugspannungen und Elementcoordinaten
        path (str) : Aktueller Arbeitsordner

    Returns:

    """
    #5 Größte/Kleinste Werte um Singularitäten auszuschließen
    n = 5

    #Figure
    plt.figure(figsize=(15,3))
    plt.axis('off')

    dfDruck = pd.read_csv(MinPrincipal)
    dfZug = pd.read_csv(MaxPrincipal, delim_whitespace=True)
    dfZug = dfZug.rename(columns={'Elem': 'Elem ID', 'ID': 'Y Coord', 'Y': 'Z Coord', 'Coord': 'Max Principal'})
    dfModell = dfZug[['Elem ID', 'Y Coord', 'Z Coord']]
    dfZug = dfZug.drop('Elem ID', axis=1)    
    dfZug = dfZug.drop('Y Coord', axis=1)
    dfZug = dfZug.drop('Z Coord', axis=1)

    plt.scatter(x= 'Y Coord', y= 'Z Coord',data=dfModell, color="#a0a0a0") #RGB (160,160,160)
    figurename = path + '/Modell.png'
    plt.savefig(figurename, dpi=120)

    MaxDruck = dfDruck['Min Principal'].nsmallest(n, keep= "all").mean()
    MaxZug = dfZug['Max Principal'].nlargest(n, keep= "all").mean()

    ThirdDruck = MaxDruck / 3
    QuarterZug = MaxZug / 4

    #Druck und Zug mit Element ID und Koordinaten versehen
    dfDruck = dfDruck.join(dfModell)
    dfZug = dfZug.join(dfModell)

    dfZug.drop(dfZug[dfZug['Max Principal'] < QuarterZug].index, inplace=True)
    dfDruck.drop(dfDruck[dfDruck['Min Principal'] > ThirdDruck].index, inplace=True)

    dfZug = dfZug[['Elem ID', 'Y Coord', 'Z Coord', 'Max Principal']]
    dfDruck = dfDruck[['Elem ID', 'Y Coord', 'Z Coord', 'Min Principal']]

    plt.scatter(x= 'Y Coord', y= 'Z Coord',data=dfZug, color="#ffa500") #RGB (255,165,0)
    plt.scatter(x= 'Y Coord', y= 'Z Coord',data=dfDruck, color="#a020f0") #RGB (160,32,240)

    figurename = path + '/Werte.png'
    plt.savefig(figurename, dpi=120)

    return