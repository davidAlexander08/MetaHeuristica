# uc_from_mosel.jl
using JuMP
using GLPK      # replace with your solver if needed
using DataFrames
using CSV
using Printf
using Plots
using StatsPlots

# --------------------------
# Data (translated from MOSEL)
# --------------------------
N = [:T1, :T2]           # thermal units (N = 1..2)
NEol = [:W1]             # eolic units (1..1)
P = 1:24                 # periods
# Demand (as in MOSEL)
Demanda = Dict(t => v for (t, v) in enumerate([
    140, 131, 124, 124, 153, 160, 164, 164, 162, 167, 170, 170,
    168, 157, 162, 163, 163, 125, 141, 126, 129, 164, 157, 147
]))

# Wind profile
Eolica = Dict(t => v for (t, v) in enumerate([
    10, 40, 40, 5, 10, 15, 33, 43, 30, 50, 43, 32,
    0, 50, 0, 50, 30, 50, 30, 10, 40, 45, 35, 50
]))
##### CASO OFICIAL ACIMA

#### CASO ACADEMICO
N = [:T1, :T2]           # thermal units (N = 1..2)
NEol = [:W1]             # eolic units (1..1)
P = 1:8                 # periods
Demanda = Dict(t => v for (t, v) in enumerate([80,100,100,100,150,100,90,80]))
Eolica = Dict(t => v for (t, v) in enumerate([0,20,40,60,40,30,20,0]))
#DEMANDA  80, 70, 60, 40, 40, 110, 70, 80
############################
# Thermal cost, limits and other parameters (forall t set same as MOSEL)
Custo = Dict()
LimiteSup = Dict()
LimiteInf = Dict()
Combustivel = Dict()
for u in N
    for t in P
        if u == :T1
            Custo[(u,t)] = 10
            LimiteSup[(u,t)] = 100.0
            LimiteInf[(u,t)] = 10.0            
        else
            Custo[(u,t)] = 100
            LimiteSup[(u,t)] = 250.0
            LimiteInf[(u,t)] = 30.0
        end
    end
    Combustivel[(u)] = 500.0
end

# Wind limits
CustoEol = Dict((:W1,t) => 0 for t in P)
LimiteSupEol = Dict((:W1,t) => Eolica[t] for t in P)
LimiteInfEol = Dict((:W1,t) => 0.0 for t in P)

# Ton, Toff, Rampa from MOSEL
Ton = Dict(:T1 => 1, :T2 => 3)
#Toff = Dict(:T1 => 1, :T2 => 3)
Rampa = Dict(:T1 => 20.0, :T2 => 30.0)

# SWITCH flags (all 1 in MOSEL)
SWITCH = (0,0,0)

# --------------------------
# Model
# --------------------------
model = Model(GLPK.Optimizer)
set_silent(model) # comment out to see solver output

# variables
@variable(model, p[u in N, t in P] >= 0)        # thermal generation continuous
@variable(model, eol[e in NEol, t in P] >= 0)  # wind generation continuous
@variable(model, deficit[t in P] >= 0)        # deficit (load not served)
@variable(model, u[u in N, t in P], Bin)      # commitment on/off

# Optional: small "u cost" term like MOSEL (0.1 * u)
small_u_cost = 0.1

# bounds on p using u
for u_unit in N, t in P
    @constraint(model, p[u_unit,t] <= LimiteSup[(u_unit,t)] * u[u_unit,t])
    @constraint(model, p[u_unit,t] >= LimiteInf[(u_unit,t)] * u[u_unit,t])
    @constraint(model, p[u_unit,t] >= LimiteInf[(u_unit,t)] * u[u_unit,t])
end

for u_unit in N
    @constraint(model, sum(p[u_unit,t] for t in P) <= Combustivel[(u_unit)])
end
# wind bounds
for w in NEol, t in P
    @constraint(model, eol[w,t] <= LimiteSupEol[(w,t)])
    @constraint(model, eol[w,t] >= LimiteInfEol[(w,t)])
end

# energy balance: sum thermal + eolic + deficit = demand
for t in P
    @constraint(model, sum(p[u,t] for u in N) + deficit[t] + sum(eol[w,t] for w in NEol) == Demanda[t])
end

# Min-up (Ton) constraints if SWITCH(1) == 1
if SWITCH[1] == 1
    T = maximum(P)
    for u_unit in N, t in P
        ut = Ton[u_unit]
        t_end = min(t + ut - 1, T)
        # define u_prev (u_{t-1}); for t=1 treat as 0
        if t == 1
            # sum_{k=t..t_end} u_k >= Ton * u_t
            @constraint(model, sum(u[u_unit,k] for k in t:t_end) >= ut * u[u_unit,t])
        else
            @constraint(model, sum(u[u_unit,k] for k in t:t_end) >= ut * (u[u_unit,t] - u[u_unit,t-1]))
        end
    end
end

## Min-down (Toff) constraints if SWITCH(2) == 1
#if SWITCH[2] == 1
#    T = maximum(P)
#    for u_unit in N, t in P
#        dt = Toff[u_unit]
#        t_end = min(t + dt - 1, T)
#        if t == 1
#            # MOSEL had a special case; translate to:
#            # sum_{k=1..t_end} (1 - u_k) >= -Toff * u_t  (equivalent to forcing if u_t=1)
#            @constraint(model, sum(1 - u[u_unit,k] for k in t:t_end) >= -dt * u[u_unit,t])
#        else
#            @constraint(model, sum(1 - u[u_unit,k] for k in t:t_end) >= dt * (u[u_unit,t-1] - u[u_unit,t]))
#        end
#    end
#end

## Ramp constraints if SWITCH(3) == 1
#if SWITCH[3] == 1
#    T = maximum(P)
#    for u_unit in N
#        for t in P
#            if t == 1
#                # replicate MOSEL special: abs(p1 - p2) <= ramp
#                if t+1 in P
#                    @constraint(model, p[u_unit,1] - p[u_unit,2] <= Rampa[u_unit])
#                    @constraint(model, p[u_unit,2] - p[u_unit,1] <= Rampa[u_unit])
#                end
#            else
#                # |p_t - p_{t-1}| <= ramp
#                @constraint(model, p[u_unit,t] - p[u_unit,t-1] <= Rampa[u_unit])
#                @constraint(model, p[u_unit,t-1] - p[u_unit,t] <= Rampa[u_unit])
#            end
#        end
#    end
#end

# Objective: sum(Custo * p) + sum(deficit*150000) + sum(0.1*u) + wind costs (zero)
@objective(model, Min, 
    sum(Custo[(u_unit,t)] * p[u_unit,t] for u_unit in N, t in P)
    + 150000 * sum(deficit[t] for t in P)
    + small_u_cost * sum(u[u_unit,t] for u_unit in N, t in P)
    + sum(CustoEol[(w,t)] * eol[w,t] for w in NEol, t in P)
)

# Solve
optimize!(model)

status = termination_status(model)
println("Status: ", status)
if status != MOI.OPTIMAL && status != MOI.LOCALLY_SOLVED
    println("Solver did not find an optimal solution. Terminating.")
else
    println("Objective (total cost): ", objective_value(model))
end

# --------------------------
# Print results similar to MOSEL output
# --------------------------
# Thermal outputs and commitment
open("Operacao-DespachoTermico.csv","w") do io
    println(io, "Periodo;Termica;P(MW);u(0/1)")
    for u_unit in N
        for t in P
            println(io, "$(t);$(u_unit);", value(p[u_unit,t]), ";", Int(round(value(u[u_unit,t]))))
        end
    end
end

# Print to console: per unit
println("\nThermal units (p and u):")
for u_unit in N
    println("Unit: ", u_unit)
    for t in P
        @printf("Period %2d: p = %7.2f   u = %d\n", t, value(p[u_unit,t]), Int(round(value(u[u_unit,t]))))
    end
    println()
end

# Print deficit, demand, wind, total generation
println("Period; Deficit; Demand; Wind; TotalGen")
for t in P
    totalgen = sum(value(p[u,t]) for u in N) + sum(value(eol[w,t]) for w in NEol)
    @printf("%2d ; %8.4f ; %6.1f ; %6.1f ; %8.2f\n", t, value(deficit[t]), Demanda[t], sum(value(eol[w,t]) for w in NEol), totalgen)
end

# Optional: save a summary table
rows = Any[]
for t in P
    push!(rows, (Period = t,
                 Demand = Demanda[t],
                 Deficit = value(deficit[t]),
                 Wind = sum(value(eol[w,t]) for w in NEol),
                 TotalThermal = sum(value(p[u,t]) for u in N),
                 TotalGen = sum(value(p[u,t]) for u in N) + sum(value(eol[w,t]) for w in NEol)
                ))
end
df_summary = DataFrame(rows)
CSV.write("summary_uc.csv", df_summary)
println("\nSummary written to summary_uc.csv and Operacao-DespachoTermico.csv")

plt = @df df_summary plot(
    :Period,
    [:Demand, :Deficit, :Wind, :TotalThermal, :TotalGen],
    xlabel="Period",
    ylabel="MW",
    lw=2,
    label=["Demand" "Deficit" "Wind" "Thermal" "Total"],
    title="Dispatch (thermal units)"
)

savefig(plt, "dispatch_plot.png")
println("Plot saved as dispatch_plot.png")


# Create folder to save plots (optional)
plots_dir = "plots"
isdir(plots_dir) || mkdir(plots_dir)

# Thermal units
for u_unit in N
    p_values = [value(p[u_unit, t]) for t in P]
    u_status = [Int(round(value(u[u_unit, t]))) for t in P]

    plt = plot(
        P, p_values,
        xlabel="Period",
        ylabel="MW",
        lw=2,
        marker=:circle,
        label="Generation (p)",
        title="Thermal Unit $(u_unit) Dispatch"
    )

    # Overlay commitment status as bars (optional)
    bar!(P, [v*maximum(p_values) for v in u_status], alpha=0.3, label="Commitment (u)")

    # Save figure
    filename = joinpath(plots_dir, "thermal_unit_$(u_unit).png")
    savefig(plt, filename)
    println("Plot saved: $filename")
end