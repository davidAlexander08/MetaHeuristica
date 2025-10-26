import numpy as np

# ---------------- Example Data ----------------
np.random.seed(0)

num_gens = 2
num_hours = 4

# Generator parameters
P_min = np.array([10, 20])     # MW
P_max = np.array([50, 60])     # MW
fuel_cost = np.array([20, 25]) # $/MWh
startup_cost = np.array([100, 120])

# Demand per hour
demand = np.array([60, 80, 50, 30])

# ---------------- Functions ----------------

def solucao_inicial():
    """Generate initial feasible on/off schedule"""
    x = np.zeros((num_gens, num_hours), dtype=int)
    for t in range(num_hours):
        while True:
            x[:,t] = np.random.randint(0,2,num_gens)
            if np.sum(P_min * x[:,t]) <= demand[t] <= np.sum(P_max * x[:,t]):
                break
    return x

def dispatch_cost(u):
    """Compute total generation cost (fuel + startup)"""
    total_cost = 0
    for t in range(num_hours):
        on_gens = np.where(u[:,t]==1)[0]
        if len(on_gens)==0:
            return np.inf  # infeasible
        # Simple proportional dispatch (economic dispatch)
        P_needed = demand[t]
        P = np.zeros(num_gens)
        P_on_min = P_min[on_gens]
        P_on_max = P_max[on_gens]
        # Allocate proportionally to max capacity
        capacity_sum = np.sum(P_on_max)
        for i, g in enumerate(on_gens):
            P[g] = P_on_max[i] / capacity_sum * P_needed
            P[g] = max(P[g], P_min[g])
            P[g] = min(P[g], P_max[g])
        # Fuel cost
        total_cost += np.sum(P * fuel_cost)
    # Startup cost
    for g in range(num_gens):
        for t in range(num_hours):
            if t==0 and u[g,t]==1:
                total_cost += startup_cost[g]
            elif t>0 and u[g,t]==1 and u[g,t-1]==0:
                total_cost += startup_cost[g]
    return total_cost

def perturb(u):
    """Flip a random generator status in a random hour"""
    u_new = u.copy()
    g = np.random.randint(0,num_gens)
    t = np.random.randint(0,num_hours)
    u_new[g,t] = 1 - u_new[g,t]
    return u_new

# ---------------- Simulated Annealing ----------------

T = 1000.0
T_min = 1.0
alpha = 0.9
num_iter = 500

u = solucao_inicial()
best_u = u.copy()
best_cost = dispatch_cost(u)

while T > T_min:
    for _ in range(num_iter):
        u_new = perturb(u)
        cost_curr = dispatch_cost(u)
        cost_new = dispatch_cost(u_new)
        delta = cost_new - cost_curr
        if delta < 0 or np.random.rand() < np.exp(-delta/T):
            u = u_new
            if cost_new < best_cost:
                best_u = u_new
                best_cost = cost_new
    T *= alpha

# ---------------- Results ----------------

print("Best schedule (1=on,0=off):")
print(best_u)
print("Best cost:", best_cost)