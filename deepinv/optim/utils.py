import torch
import torch.nn as nn
import sys 
from deepinv.optim.optim_iterators import *


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

def check_conv(X_prev, X, it, crit_conv, thres_conv, verbose=False):
    x_prev = X_prev['est'][0]
    F_prev = X_prev['cost']
    x = X['est'][0]
    F = X['cost']
    if crit_conv == 'residual' :
        crit_cur = (x_prev-x).norm() / (x.norm()+1e-06)
    elif crit_conv == 'cost' :
        crit_cur = (F_prev-F).norm()  / (F.norm()+1e-06)
    if crit_cur < thres_conv :
        if verbose: 
            print(f'Iteration {it}, current converge crit. = {crit_cur:.2E}, objective = {thres_conv:.2E} \r')
        return True 
    else :
        return False
   

def conjugate_gradient(A, b, max_iter=1e2, tol=1e-5):
    '''
    Standard conjugate gradient algorithm to solve Ax=b
        see: http://en.wikipedia.org/wiki/Conjugate_gradient_method
    :param A: Linear operator as a callable function, has to be square!
    :param b: input tensor
    :param max_iter: maximum number of CG iterations
    :param tol: absolute tolerance for stopping the CG algorithm.
    :return: torch tensor x verifying Ax=b

    '''

    def dot(s1, s2):
        return (s1 * s2).flatten().sum()

    x = torch.zeros_like(b)

    r = b
    p = r
    rsold = dot(r, r)

    for i in range(int(max_iter)):
        Ap = A(p)
        alpha = rsold / dot(p, Ap)
        x = x + alpha * p
        r = r - alpha * Ap
        rsnew = dot(r, r)
        #print(rsnew.sqrt())
        if rsnew.sqrt() < tol:
            break
        p = r + (rsnew / rsold) * p
        rsold = rsnew

    return x


def gradient_descent(grad_f, x, step_size=1., max_iter=1e2, tol=1e-5):
    '''
    Standard gradient descent algorithm to solve min_x f(x)
    :param grad_f: gradient of function to bz minimized as a callable function.
    :param x: input tensor
    :param step_size: (constant) step size of the gradient descent algorithm.
    :param max_iter: maximum number of iterations
    :param tol: absolute tolerance for stopping the algorithm.
    :return: torch tensor x verifying min_x f(x)

    '''

    for i in range(int(max_iter)):
        x_prev = x
        x = x - step_size * grad_f(x)
        if check_conv(x_prev, x, i, crit_conv=tol) :
            break
    return x