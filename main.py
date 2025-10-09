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
                C[i][j]+=round(A[i][k]*At[k][j],4)
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

def is_upper_triangular(A):
    n = len(A)
    m = len(A[0])
    for i in range(n):
        for j in range(i):
            if abs(A[i][j]) > 1e-10:
                return False
    return True

def s(ATY,A):
    result=[]
    if is_lower_triangular(A):
        for i in range(len(ATY)):
            if i==0:
                result.append(round(ATY[0][0]/A[0][0],4))
            else:
                sum=ATY[i][0]
                for j in range(len(A[i])):
                    if j<len(result):
                        sum=sum-A[i][j]*result[j]
                    else:
                        if A[i][j]!=0:
                            sum=sum/A[i][j]
                result.append(round(sum,4))
    else:
        for i in range(len(ATY)):
            if i==0:
                result.append(round(ATY[len(ATY)-1][0]/A[len(ATY)-i-1][len(A[0])-1],4))
            else:
                sum=ATY[len(ATY)-1-i][0]
                for j in range(len(A[i])):
                    if j<len(result):
                        sum=sum-A[len(ATY)-1-i][len(A[0])-1-j]*result[j]
                    else:
                        if A[len(ATY)-1-i][len(A[0])-1-j]!=0:
                            sum=sum/A[len(ATY)-1-i][len(A[0])-1-j]
                result.append(round(sum,4))
    return result

def egy(X,f):
    minX = min(X)
    maxX = max(X)
    result=[]
    i=minX-1
    while i<maxX+1:
        result.append({"x": i, "y": getXValue(f, i)})
        i+=0.1
    return result

        
def getBackF(f,eredmeny):
    index=len(eredmeny)-1
    result = ""
    for i in range(len(f)):
        if f[i]=="r":
            result+=str(eredmeny[index])
            index-=1
        else:
            result+=f[i]
    return result


def calculateC(X,Y,f):
    A = getMatrix(X,f)
    At = transpose(A)
    AtA = MatSzor(At,A)
    AtY = MatSzor(At,[[y] for y in Y])
    if is_upper_triangular(AtA) and is_lower_triangular(AtA):
        e=AtY
        C = AtA
        Ak = [["r"+str(i)] for i in range(len(C))]
        eredmeny = list(reversed(s(e,C)))
        points = [{"x": X[i], "y": Y[i]} for i in range(len(X))]
        fBack = getBackF(f, eredmeny)
        egyenes = egy(X, fBack)
        try:
            return {"A": A,"Y":Y, "At": At, "AtA": AtA, "AtY": AtY, "C": C, "eredmeny": fBack, "Ak": Ak, "p": points, "line": egyenes, "e": e,"Ct":C}
        except Exception as e:
            return {"error": str(e)}
    if not is_upper_triangular(AtA) and not is_lower_triangular(AtA):
        C = cholesky_decomposition(AtA)
    if is_upper_triangular(AtA) and not is_lower_triangular(AtA):
        C = transpose(AtA)
    if is_lower_triangular(AtA) and not is_upper_triangular(AtA):
        C = AtA
    e=[[i] for i in s(AtY,C)]
    Ak = [["r"+str(i)] for i in range(len(C))]
    eredmeny = s(e,transpose(C))
    points = [{"x": X[i], "y": Y[i]} for i in range(len(X))]
    fBack = getBackF(f, eredmeny)
    egyenes = egy(X, fBack)
    try:
        return {"A": A,"Y":Y, "At": At, "AtA": AtA, "AtY": AtY, "C": C, "eredmeny": fBack, "Ak": Ak, "p": points, "line": egyenes, "e": e,"Ct":transpose(C)}
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