#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 13:49:12 2020

@author: Yonatan Arieh
"""

import math
import csv
from filterpy.kalman import UnscentedKalmanFilter
from filterpy.kalman import unscented_transform, MerweScaledSigmaPoints
from filterpy.common import Q_discrete_white_noise
import numpy as np
from numpy.random import randn
import time as Time

start = Time.time()
#x = state, dt = dt, time = array with time value (1 element array only needs current value)
#Assumes acc, vel and pos in state are in ft/s**2, ft/s and ft
#Assumes spin components are in RPM and remain constant throughout
def fx(x,dt,wb = 1500+randn()*200,ws = 1000+randn()*200,wg = 0): #State transition function Pitch 1
#def fx(x,dt,wb = 1200+randn()*200,ws = -800+randn()*200,wg = 0): #State transition function Pitch 2
    if(spin == []):
        spin.append(wb)
        spin.append(ws)
        spin.append(wg)
    #baseballMass = 5.125 #Oz
    baseballCircumference = 9.125 #inches
    #rho = 0.0740 #Air density at (75 F) (50% Humidity) (760 mm Hg pressure) (0 elevation)
    const = 0.005316 #5.316E-03 = 0.07182*rho*(5.125/mass)*(circ/9.125)^2
                     #Edit values for mass, circ, or rho to find new const if necessary
    Cd = 0.330 #Drag Coefficient
    #beta = 0.0001217 #Constant in calculating actual pressure not used in this script just for reference
    #SVP constant (Saturation Vapor Pressure)
    
  
    
    
    
    #Vin = mph*1.467
    #Vinz = Vin*math.sin(theta) #Takes vertical component of throw
    #Vinx = Vin*math.cos(theta)*math.sin(phi) #Takes horizontal component of throw then adjusts on horizontal plane. X axis = 1st base-third base line
    #Viny = Vin*math.cos(theta)*math.cos(phi)#Takes horizontal component of throw then adjusts on horizontal plane. Y axis = Home plate to pitching mound line
    Vinx = x[3]
    Viny = x[4]
    Vinz = x[5]
    Vin = math.sqrt(Vinx**2 + Viny**2 + Vinz**2)
    theta = math.asin(Vinz/Vin)
    #print(Viny/(Vin*math.cos(theta)))
    try:
        phi = math.acos(Viny/(Vin*math.cos(theta)))
    except ValueError:
        phi = math.pi
    #print(math.degrees(theta),math.degrees(phi))
    
    #theta = theta*(math.pi/180) #Convert to radians
    #phi = phi*(math.pi/180) #Convert to radians
    
    wx = (wb*math.cos(phi)-ws*math.sin(theta)*math.sin(phi)+wg*Vinx/Vin)*math.pi/30
    wy = (-wb*math.sin(phi)-ws*math.sin(theta)*math.cos(phi)+wg*Viny/Vin)*math.pi/30
    wz = (ws*math.cos(theta)+wg*Vinz/Vin)*math.pi/30
   
    w = math.sqrt(wx**2 + wy**2 + wz**2) #rad per sec
    rw =(baseballCircumference/(2*math.pi))*(w/12) #ft per sec
    
    vxw = 0 #Wind speed in x direction ft/sec
    vyw = 0 #Wind speed in y direction ft/sec
    
    
    #Re_100 = 210000 #2.100E+05 Reynolds number for 100 mph throw
    
    positionVector = []
    velocityVector = []
    accelerationVector = []
    
    initialPos = [x[0],x[1],x[2]]
    positionVector.append(initialPos)
    
    initialVel = [Vinx,Viny,Vinz]
    velocityVector.append(initialVel)
    
    initAccel = [x[6],x[7],x[8]]
    accelerationVector.append(initAccel)
    t = time[0]
    dt = dt
    tau = 10000 #Spin decay constant. Set large so spin doesn't decay much
        
    vw = math.sqrt((velocityVector[-1][0]-vxw)**2 + (velocityVector[-1][1]-vyw)**2 + (velocityVector[-1][2])**2) #Wind adjusted Velocity
        
    aDragx = const*(velocityVector[-1][0]-vxw)*Cd*vw*-1
    aDragy = const*(velocityVector[-1][1]-vyw)*Cd*vw*-1
    aDragz = const*(velocityVector[-1][2])*Cd*vw*-1
        
    S = (rw/vw)*(math.e**((t*-1)/tau))
    Cl = 1.0/(2.32+(0.4/S))
    aMagx = const*vw*(wy*velocityVector[-1][2]-wz*(velocityVector[-1][1]-vyw))*(Cl/w)
    aMagy = const*vw*(wz*(velocityVector[-1][0]-vxw)-wx*(velocityVector[-1][2]))*(Cl/w)
    aMagz = const*vw*(wx*(velocityVector[-1][1]-vyw)-wy*(velocityVector[-1][0]))*(Cl/w)
        
    aX = aDragx+aMagx
    aY = aDragy+aMagy
    aZ = aDragz+aMagz - 32.174 #Gravity
    acceleration = [aX,aY,aZ]
    accelerationVector.append(acceleration)
        
    vX = velocityVector[-1][0] + aX*dt
    vY = velocityVector[-1][1] + aY*dt
    vZ = velocityVector[-1][2] + aZ*dt
    velocity = [vX,vY,vZ]
    velocityVector.append(velocity)
        
    pX = positionVector[-1][0] + vX*dt + 0.5*aX*dt*dt
    pY = positionVector[-1][1] + vY*dt + 0.5*aY*dt*dt
    pZ = positionVector[-1][2] + vZ*dt + 0.5*aZ*dt*dt
    position = [pX,pY,pZ]
    positionVector.append(position)
    
    x = np.array([positionVector[-1][0],positionVector[-1][1],positionVector[-1][2], velocityVector[-1][0],velocityVector[-1][1],velocityVector[-1][2],accelerationVector[-1][0],accelerationVector[-1][1],accelerationVector[-1][2]])
    #print(x)
    #print(time[0])
    return(x)
    
def hx(x):
    return x[:3]



dt = 0.0001
#p = np.array([[5,0,0,0,0,0,0,0,0], [0,10,0,0,0,0,0,0,0],[0,0,5,0,0,0,0,0,0],[0,0,0,20,0,0,0,0,0,0],[0,0,0,0,40,0,0,0,0,0],[0,0,0,0,0,20,0,0,0],[0,0,0,0,0,0,15,0,0],[0,0,0,0,0,0,0,15,0],[0,0,0,0,0,0,0,0,20]])
points = MerweScaledSigmaPoints(n=9, alpha=.2, beta=2., kappa=-6.)
#sigmas = points.sigma_points(mean, p)
ukf = UnscentedKalmanFilter(dim_x=9, dim_z=3, dt=dt, hx=hx, fx=fx, points=points)
ukf.x = np.array([0.,55.,5,0.,-100.,0,0.,0.,-32])
ukf.P *= 10000.
ukf.R = np.diag([(0.25/3)**2,(0.25/3)**2,(0.25/3)**2])
ukf.Q = Q_discrete_white_noise(dim=3, dt=dt, var=0.0000001, block_size=3)

data = []
'''with open('KalmanTestTrajectoryDataPosition(ts).csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        data.append(row)'''
with open('SimNoisySensorInput.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        data.append(row)

print("Time after CSV: ", Time.time()-start)        

#z_std = 0.20
zs = [] # measurements
timeStamps = []
for i in data:
    element = [float(i[0]), float(i[1]),float(i[2])]
    zs.append(element)
    timeStamps.append(float(i[3]))
#print(zs)
spin = []
#print(ukf.x)
#print(ukf.P)
#print(ukf.R)
#print(ukf.Q)

#(xs, ps) = ukf.batch_filter(zs)
counter = 0
xs = []
ps = []
#print(timeStamps)
Var = 0
time = [timeStamps[0]]
for z in zs:
    timeStamp = timeStamps[counter]
    #aprint(timeStamp)
    #print("Predict")
    while(time[0] <= timeStamp):
        ukf.predict()
        time[0] += dt
        xs.append(ukf.x.copy())
        ps.append(ukf.P.copy())
        Var = Var+1
        #print(time[0])
    #print("update")
    print(Var)
    Var = 0
    ukf.R = np.diag([(0.1/3)**2,(((10-z[2])*0.01)/3)**2,(0.1/3)**2])
    #ukf.R = np.diag([(0.01/3)**2,(0.01/3)**2,(0.01/3)**2])
    #print(ukf.R)
    ukf.update(z)
    xs.append(ukf.x.copy())
    ps.append(ukf.P.copy())
    #print(ukf.x)
    #print(counter)
    counter+=1;
xs = np.array(xs)
ps = np.array(ps)
print("Time after Filter: ", Time.time()-start)
#for z in zs:
#    ukf.predict()
#    ukf.update(z)
#    xs.append(ukf.x)
#    ps.append(ukf.P)
    #print(kf.x, 'log-likelihood', kf.log_likelihood)

netDistance = 10
netPosition = 55-netDistance
netIndex = 0
#print(xs)
for i in range(0,len(xs)):
    if(xs[i][1] < netPosition):
        netIndex = i
        print(i)
        break
(sxs, Ps, K) = ukf.rts_smoother(xs[:(i+1)], ps[:(i+1)])
print("Time after Smoother: ", Time.time()-start)
#print(spin)
spinA = ([str(spin[0])],[str(spin[1])],[str(spin[2])])
with open('KalmanFilterPosition.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(xs)
with open('KalmanFilterErrorDebug.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(ps[-1])
with open('KalmanFilterPositionSmooth.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sxs)
with open('MeasuredPosition.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(zs)
with open('Spin.csv', 'w', newline='') as f:
        writer = csv.writer(f,delimiter = ',')
        writer.writerows(spinA)
print("Time after CSV: ", Time.time()-start)