import sys
import mosek 

inf = 0

# Função para capturar a saída do MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def solve_problem_continuos(sense, c, bkx, bux, blx, bkc, blc, buc, asub, aval):
    # Create a task object
    with mosek.Task() as task:
        # Attach a log stream printer to the task
        task.set_Stream(mosek.streamtype.log, streamprinter)

        numvar = len(bkx)
        numcon = len(bkc)

        # Append 'numcon' empty constraints.
        # The constraints will initially have no bounds.
        task.appendcons(numcon)

        # Append 'numvar' variables.
        # The variables will initially be fixed at zero (x=0).
        task.appendvars(numvar)
        

        for j in range(numvar):
            # Set the linear term c_j in the objective.
            task.putcj(j, c[j])

            # Set the bounds on variable j
            # blx[j] <= x_j <= bux[j]
            task.putvarbound(j, bkx[j], blx[j], bux[j])
        
        # Set the bounds on constraints.
        # blc[i] <= constraint_i <= buc[i]
        for i in range(numcon):
            task.putconbound(i, bkc[i], blc[i], buc[i])
            task.putarow(i, asub[i], aval[i])

        # Input the objective sense (minimize/maximize)
        task.putobjsense(sense)

        # Solve the problem
        task.optimize()
        # Print a summary containing information
        # about the solution for debugging purposes
        task.solutionsummary(mosek.streamtype.msg)

        # Get status information about the solution
        solsta = task.getsolsta(mosek.soltype.bas)

        if (solsta == mosek.solsta.optimal):
            xx = task.getxx(mosek.soltype.bas)
            
            print("Optimal solution: ")
            for i in range(numvar):
                print("x[" + str(i) + "]=" + str(xx[i]))

            return {"status": "optimal", "solution": xx.tolist()}
        elif (solsta == mosek.solsta.dual_infeas_cer or
              solsta == mosek.solsta.prim_infeas_cer):
            print("Primal or dual infeasibility certificate found.\n")
            return {"status": "infeasible"}
        else:
            print("Unknown solution status")
            return {"status": "unknown"}
    return 


def solve_problem_integer(sense, c, bkx, bux, blx, bkc, blc, buc, asub, aval, vartypes):
    # Make a MOSEK environment
    with mosek.Env() as env:
        # Attach a printer to the environment
        env.set_Stream(mosek.streamtype.log, streamprinter)

        # Create a task
        with env.Task(0, 0) as task:
            # Attach a printer to the task
            task.set_Stream(mosek.streamtype.log, streamprinter)

            numvar = len(bkx)
            numcon = len(bkc)

            # Append 'numcon' empty constraints.
            # The constraints will initially have no bounds.
            task.appendcons(numcon)

            #Append 'numvar' variables.
            # The variables will initially be fixed at zero (x=0).
            task.appendvars(numvar)

            for j in range(numvar):
                # Set the linear term c_j in the objective.
                task.putcj(j, c[j])
                # Set the bounds on variable j
                # blx[j] <= x_j <= bux[j]
                task.putvarbound(j, bkx[j], blx[j], bux[j])
               
            # Set the bounds on constraints.
            # blc[i] <= constraint_i <= buc[i]
            for i in range(numcon):
                task.putconbound(i, bkc[i], blc[i], buc[i])
                task.putarow(i, asub[i], aval[i])


            # Input the objective sense (minimize/maximize)
            task.putobjsense(sense)

            # Define variables to be integers
            task.putvartypelist(vartypes, len(vartypes)*[mosek.variabletype.type_int])

            # Set max solution time
            task.putdouparam(mosek.dparam.mio_max_time, 60.0);

            # Optimize the task
            task.optimize()

            # Print a summary containing information
            # about the solution for debugging purposes
            task.solutionsummary(mosek.streamtype.msg)

            solsta = task.getsolsta(mosek.soltype.itg)

            if (solsta == mosek.solsta.integer_optimal):
                xx = task.getxx(mosek.soltype.itg)
            
                print("Optimal solution: ")
                for i in range(numvar):
                    print("x[" + str(i) + "]=" + str(xx[i]))

                return {"status": "optimal", "solution": xx.tolist()}
            elif (solsta == mosek.solsta.dual_infeas_cer or
                solsta == mosek.solsta.prim_infeas_cer):
                print("Primal or dual infeasibility certificate found.\n")
                return {"status": "infeasible"}
            else:
                print("Unknown solution status")
                return {"status": "unknown"}
    return 


