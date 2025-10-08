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

def MatSzorA(A,At):
    n=len(A)
    m=len(A[0])
    for i in range(n):
        for k in range(m):
            A[i][k] = str(A[i][k])+"*"+"r"+str(k)
    return A

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
    if is_lower_triangular(A):
        return A
    else:
        L = np.linalg.cholesky(np.array(A))
                    
        return L.tolist()

def is_lower_triangular(A):
    n = len(A)
    m = len(A[0])
    for i in range(n):
        for j in range(i+1, m):
            if abs(A[i][j]) > 1e-10:
                return False
    return True

def s(ATY,A):
    result=[]
    for i in range(len(ATY)):
        if i==0:
            result.append(ATY[0][0]/A[0][0])
        else:
            sum=ATY[i][0]
            for j in range(len(ATY[0])):
                if j<len(result):
                    sum=sum-A[i][j]*result[j]
                else:
                    if A[i][j]!=0:
                        sum=sum/A[i][j]
            result.append(sum)
    return result

                

def calculateC(X,Y,f):
    A = getMatrix(X,f)
    At = transpose(A)
    AtA = MatSzor(At,A)
    AtY = MatSzor(At,[[y] for y in Y])
    C = cholesky_decomposition(AtA)
    Ak = [["r"+str(i)] for i in range(len(C))]
    eredmeny = s(AtY,C)
    try:
        return {"A": A,"Y":Y, "At": At, "AtA": AtA, "AtY": AtY, "C": C, "eredmeny": eredmeny, "Ak": Ak}
    except Exception as e:
        return {"error": str(e)}



app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("Matrix.html", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
    
@app.post("/solve")
async def solve(request: Request):
    data = await request.json()
    X = data.get("x", [])
    Y = data.get("y", [])
    f = data.get("f", "")
    return calculateC(X, Y, f)