import math
import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Request

def MatSzor(A,At):
    n=len(A)
    m=len(A[0])
    p=len(At[0])
    C=[[0 for j in range(p)] for i in range(n)]
    for i in range(n):
        for j in range(p):
            for k in range(m):
                C[i][j]+=A[i][k]*At[k][j]
    return C

def transpose(A):
    At=[[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
    return At

def getXValue(fuggveny_string, x):
    eredmeny = eval(fuggveny_string, {"__builtins__": None, "math": math, "x": x})
    return eredmeny


def get_F(f):
    resp=[]
    a= f.split("+")
    for i in range(len(a)):
        resp.append(a[i].replace("r", "1"))
    return resp

def getMatrix(X,f):
    fs = get_F(f)
    A = [[getXValue(fs[j], X[i]) for j in range(len(fs))] for i in range(len(X))]
    return A

def cholesky_decomposition(A):

    n = len(A)

    L = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1):
            if i == j:
                sum_sq = sum(L[i][k]**2 for k in range(j))
                
                term = A[i][i] - sum_sq
                    
                L[i][j] = math.sqrt(term)
            else:
                sum_prod = sum(L[i][k] * L[j][k] for k in range(j))
                L[i][j] = (A[i][j] - sum_prod) / L[j][j]
                
    return L

def calculateC(X,Y,f):
    A = getMatrix(X,f)
    print(A)
    At = transpose(A)
    print(At)
    AtA = MatSzor(At,A)
    print(AtA)
    AtY = MatSzor(At,[[y] for y in Y])
    print(AtY)
    print(cholesky_decomposition(AtA))





X=[-2,-1,0,1,2]
Y = [2,2,4,3,1]

f="r+r*x"

calculateC(X,Y,f)



app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("Matrix.html", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)