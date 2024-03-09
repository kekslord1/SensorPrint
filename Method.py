"""

"""
"""
Enthält alle funktionen die zur Ermittlung der Sensoren verwendet werden.

Author: Philipp Haug
Date: 24.05.2023
Version: 10.0
"""
import numpy as np
import cv2

def SensorMalen(image : np.ndarray, x1 : int, y1 : int, x2 : int, y2 : int, Anschluss1x : int, Anschluss1y : int, Anschluss2x : int, Anschluss2y : int):
    """Zeichnet den Sensor ins Zielbild

    Args:
        image (np.ndarray) : Zielbild
        x1 (int) : X-Parameter von Sensorpunkt 1
        y1 (int) : Y-Parameter von Sensorpunkt 1
        x2 (int) : X-Parameter von Sensorpunkt 2
        y2 (int) : Y-Parameter von Sensorpunkt 2
        Anschluss1x (int) : X-Parameter von Anschluss 1
        Anschluss1y (int) : Y-Parameter von Anschluss 1
        Anschluss2x (int) : X-Parameter von Anschluss 2
        Anschluss2y (int) : Y-Parameter von Anschluss 2

    Returns:
       np.ndarray : Zielbild mit Sensor
    """

    cv2.line(image, (x1,y1), (x2,y2), (0,0,0), 2)
    cv2.line(image, (x1,y1), (Anschluss1x, Anschluss1y), (0,0,0), 2)
    cv2.line(image, (x2,y2), (Anschluss2x, Anschluss2y), (0,0,0), 2)

    return image


def SensorErkennung2(path : str, area : np.ndarray, scalex : float, scaley : float):
    """Ermittelt den Sensor für die eingegebene Spannunskontur

    Args:
        path (str) : Aktueller Arbeitsordner
        area (np.ndarray) : Spannungskontur im Modellbild 
        scalex (float) : Bild zu Drawing Skalierung in X-Richtung
        scaley (float) : Bild zu Drawing Skalierung in Y-Richtung

    Raises:
        ValueError wenn der Sensor zu kurz ist   

    Returns:
       list: Liste für den Sensor mit Länge, Punkten und Anschlusspunkten
    """
    
    ModellBild = cv2.imread(path +'/Modell.png')
    image = cv2.imread(path +'/Werte.png')
    Leeres = np.zeros(image.shape)

    cv2.drawContours(Leeres, area, -1, (255,255,255), 3)
    cv2.fillPoly(Leeres, pts =[area], color=(255,255,255))

    lowerWhite = np.array([254,254,254], dtype="uint8")
    upperWhite = np.array([255,255,255], dtype="uint8")

    maskWhite = cv2.inRange(Leeres, lowerWhite, upperWhite)
    # threshold the grayscale image
    thresh = cv2.threshold(maskWhite, 0, 255, cv2.THRESH_BINARY)[1]

    # get coordinates of all non-zero pixels
    # NOTE: must transpose since numpy coords are y,x and opencv uses x,y
    coords = np.column_stack(np.where(thresh.transpose() > 0))

    # get rotated rectangle from 
    rotrect = cv2.minAreaRect(coords)
    box = cv2.boxPoints(rotrect)
    box = np.intp(box)
    distX1 = box[0][0] - box[3][0]
    distY1 = box[0][1] - box[3][1]

    distX2 = box[0][0] - box[1][0]
    distY2 = box[0][1] - box[1][1]

    dist03 = np.sqrt(np.square(distX1)+np.square(distY1))
    dist01 = np.sqrt(np.square(distX2)+np.square(distY2))

    if dist01 >= dist03:

        # get center line from box
        # note points are clockwise from bottom right
        x1 = (box[0][0] + box[3][0]) // 2
        y1 = (box[0][1] + box[3][1]) // 2
        x2 = (box[1][0] + box[2][0]) // 2
        y2 = (box[1][1] + box[2][1]) // 2

        pixel_color = ModellBild[y1,x1]
        if pixel_color[0] != [160] and pixel_color[1] != [160] and pixel_color[2] != [160]:
            x1, y1 = nearestPoint(ModellBild, x1,y1, (160,160,160))


        pixel_color = ModellBild[y2,x2]
        if pixel_color[0] != [160] and pixel_color[1] != [160] and pixel_color[2] != [160]:
            x2, y2 = nearestPoint(ModellBild, x2,y2, (160,160,160))

        laengeSensor = np.sqrt(np.square((x2-x1)/scalex)+np.square((y2-y1)/scaley))

        if  laengeSensor > 40:

            Anschluss1x, Anschluss1y = nearestPoint(ModellBild, x1,y1, (255,255,255))
            c = np.sqrt(((Anschluss1x -x1)/scalex) ** 2 + ((Anschluss1y - y1)/scaley) ** 2)
            x3 = (Anschluss1x - x1) / c
            y3 = (Anschluss1y - y1) / c

            Anschluss1x = int(Anschluss1x + x3 * 15)
            Anschluss1y = int(Anschluss1y + y3 * 15)

            Anschluss2x, Anschluss2y = nearestPoint(ModellBild, x2,y2, (255,255,255))
            c = np.sqrt(((Anschluss2x -x2)/scalex) ** 2 + ((Anschluss2y - y2)/scaley) ** 2)
            x3 = (Anschluss2x - x2) / c
            y3 = (Anschluss2y - y2) / c

            Anschluss2x = int(Anschluss2x + x3 * 15)
            Anschluss2y = int(Anschluss2y + y3 * 15)

            return laengeSensor, x1, y1, x2, y2, Anschluss1x, Anschluss1y, Anschluss2x, Anschluss2y
        
        else:
            return ValueError, 'Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'Error'


    elif dist03 > dist01:
        # get center line from box
        # note points are clockwise from bottom right
        x1 = (box[0][0] + box[1][0]) // 2
        y1 = (box[0][1] + box[1][1]) // 2
        x2 = (box[3][0] + box[2][0]) // 2
        y2 = (box[3][1] + box[2][1]) // 2

        pixel_color = ModellBild[y1,x1]
        if pixel_color[0] != [160] and pixel_color[1] != [160] and pixel_color[2] != [160]:
            x1, y1 = nearestPoint(ModellBild, x1,y1, (160,160,160))

        pixel_color = ModellBild[y2,x2]
        if pixel_color[0] != [160] and pixel_color[1] != [160] and pixel_color[2] != [160]:
            x2, y2 = nearestPoint(ModellBild, x2,y2, (160,160,160))

        laengeSensor = np.sqrt(np.square((x2-x1)/scalex)+np.square((y2-y1)/scaley))
        #print('länge Sensor: ', laengeSensor)

        if  laengeSensor > 40:
            Anschluss1x, Anschluss1y = nearestPoint(ModellBild, x1,y1, (255,255,255))
            c = np.sqrt(((Anschluss1x -x1)/scalex) ** 2 + ((Anschluss1y - y1)/scaley) ** 2)
            x3 = (Anschluss1x - x1) / c
            y3 = (Anschluss1y - y1) / c

            Anschluss1x = int(Anschluss1x + x3 * 15)
            Anschluss1y = int(Anschluss1y + y3 * 15)

            Anschluss2x, Anschluss2y = nearestPoint(ModellBild, x2,y2, (255,255,255))
            c = np.sqrt(((Anschluss2x -x2)/scalex) ** 2 + ((Anschluss2y - y2)/scaley) ** 2)
            x3 = (Anschluss2x - x2) / c
            y3 = (Anschluss2y - y2) / c

            Anschluss2x = int(Anschluss2x + x3 * 15)
            Anschluss2y = int(Anschluss2y + y3 * 15)

            return laengeSensor, x1, y1, x2, y2, Anschluss1x, Anschluss1y, Anschluss2x, Anschluss2y
        
        else:
            return ValueError, 'Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'Error'


def SensorErkennung(path : str, scalex : float, scaley : float):
    """Ermittelt die Sensoren anhand des Bildes des Modells

    Args:
        path (str) : Aktueller Arbeitsordner
        scalex (float) : Bild zu Drawing Skalierung in X-Richtung
        scaley (float) : Bild zu Drawing Skalierung in Y-Richtung

    Returns:
       list : Liste mit allen Sensoren mit Art, Länge, Punkten und Anschlusspunkten
    """

    #Modell einlesen
    ModellBild = cv2.imread(path + '/Modell.png')
    image = cv2.imread(path + '/Werte.png')

    #Farben in BGR not RGB
    #Zugspannungen Orange RGB (255,165,0)
    lowerOrange = np.array([0,164,254], dtype="uint8")
    upperOrange = np.array([0,166,255], dtype="uint8")
    # Druckspannungen Lila RGB (160,32,240)
    lowerPurple = np.array([239,31,159], dtype="uint8")
    upperPurple = np.array([241,33,161], dtype="uint8")
    # Model Grey RGB 160 160 160
    lowerGrey = np.array([159,159,159], dtype="uint8")
    upperGrey = np.array([161,161,161], dtype="uint8")

    maskOrange = cv2.inRange(image, lowerOrange, upperOrange)
    maskPurple = cv2.inRange(image, lowerPurple, upperPurple)
    maskGrey = cv2.inRange(ModellBild, lowerGrey, upperGrey)

    contoursOrange, _ = cv2.findContours(maskOrange, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contoursPurple, _ = cv2.findContours(maskPurple, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contoursGrey, _ = cv2.findContours(maskGrey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contoursGrey) > 0:
        grey_area = max(contoursGrey, key=cv2.contourArea)
        x, y, breite, hoehe = cv2.boundingRect(grey_area)
        cv2.rectangle(image,(x, y),(x+breite, y+hoehe),(255, 0, 0), 2)

    Sensoren = []

    for cnt in contoursOrange:
        if len(cnt) > len(contoursGrey)*0.2:

            laenge, x1, y1, x2, y2, Anschluss1x, Anschluss1y, Anschluss2x, Anschluss2y = SensorErkennung2(path, cnt, scalex, scaley)
            if laenge != ValueError:
                Sensoren.append(('Zug', int(laenge), x1, y1, x2, y2, Anschluss1x, Anschluss1y, Anschluss2x, Anschluss2y))

    for cnt in contoursPurple:
        if len(cnt) > len(contoursGrey)*0.2:
            
            laenge, x1, y1, x2, y2, Anschluss1x, Anschluss1y, Anschluss2x, Anschluss2y = SensorErkennung2(path, cnt, scalex, scaley)
            if laenge != ValueError:
                Sensoren.append(('Druck', int(laenge), x1, y1, x2, y2, Anschluss1x, Anschluss1y, Anschluss2x, Anschluss2y))

    Sensoren = np.array(Sensoren, dtype=object)
    Sensoren = Sensoren[Sensoren[:, 1].argsort()]
    return Sensoren


def nearestPoint(image : np.ndarray, startX : int, startY : int, target_color : list):
    """Sucht im Bild vom Startpunkt den nächsten Punkt mit der Zielfarbe

    Args:
        image (np.ndarray) : Bild
        startX (int) : X-Parameter von Startpunkt
        startY (int) : Y-Parameter von Startpunkt
        target_color (list) : Zielfarbe in BGR. zB [255, 255, 255]

    Returns:
       int , int : X-Parameter von Zielpunkt, Y-Parameter von Zielpunkt
    """
    start_color = image[startY,startX]
    height, width = image.shape[:2]
    
    if start_color[0] != target_color[0] and start_color[1] != target_color[1] and start_color[2] != target_color[2]:
        r = 1
        winkelGes = list(range(1,361))
        found = False
        while r < height/2 or width/2:
            for winkel in winkelGes:
                searchX = int(r * np.cos(winkel)+startX)
                searchY = int(r * np.sin(winkel)+startY)

                test_color = image[searchY,searchX]
                if test_color[0] == target_color[0] and test_color[1] == target_color[1] and test_color[2] == target_color[2]:
                    resultX = searchX
                    resultY = searchY
                    found = True
                    break

            if found == True:
                break
            else:
                r += 1

    else:
        resultX = startX
        resultY = startY   

    return resultX, resultY
