using JuMP
using GLPK      # replace with your solver if needed
using DataFrames
using CSV
using Printf
using Plots
using StatsPlots
# Conjuntos
Hydros = ["H1"]
Terms = ["T1"]
N = Hydros ∪ Terms
P = 1:3

# Dados
Demanda = [50.0, 100.0, 150.0]
Custo = Dict("H1" => 0.0, "T1" => 10.0)
LimiteSup = Dict("H1" => 200.0, "T1" => 100.0)
LimiteInf = Dict("H1" => 0.0,   "T1" => 0.0)
penalty_deficit = 1000.0

Afluencia = Dict("H1" => [100.0, 50.0, 0.0])
Armazenamento_inicial = Dict("H1" => 0.0)

# Modelo
model = Model(GLPK.Optimizer)
set_silent(model)

# Variáveis
@variable(model, p[u in N, t in P] >= 0)
@variable(model, turb[h in Hydros, t in P] >= 0)
@variable(model, armazenamento[h in Hydros, t in P] >= 0)
@variable(model, deficit[t in P] >= 0)

# Limites de geração
for u in N, t in P
    @constraint(model, p[u,t] <= LimiteSup[u])
    @constraint(model, p[u,t] >= LimiteInf[u])
end

# Relação p = turbina (hidros)
for h in Hydros, t in P
    @constraint(model, p[h,t] == turb[h,t])
end

# Balanço hídrico
for h in Hydros, t in P
    if t == 1
        @constraint(model, armazenamento[h,t] == Armazenamento_inicial[h] - turb[h,t] + Afluencia[h][t])
    else
        @constraint(model, armazenamento[h,t] == armazenamento[h,t-1] - turb[h,t] + Afluencia[h][t])
    end
end

# Balanço de energia
for t in P
    @constraint(model, sum(p[u,t] for u in N) + deficit[t] == Demanda[t])
end

# Função objetivo
@objective(model, Min, 
    sum(Custo[u] * p[u,t] for u in N, t in P) +
    penalty_deficit * sum(deficit[t] for t in P)
)

optimize!(model)



status = termination_status(model)
println("Status: ", status)
if status != MOI.OPTIMAL && status != MOI.LOCALLY_SOLVED
    println("Solver did not find an optimal solution. Terminating.")
else
    println("Objective (total cost): ", objective_value(model))
end

# --------------------------
# Print results to CSV
# --------------------------
open("Operacao-Despacho.csv", "w") do io
    println(io, "Periodo;Unidade;P(MW)")
    for u_unit in N
        for t in P
            println(io, "$(t);$(u_unit);", value(p[u_unit,t]))
        end
    end
end

println("\nUnidades (p):")
for u_unit in N
    println("Unit: ", u_unit)
    for t in P
        @printf("Period %2d: p = %7.2f\n", t, value(p[u_unit,t]))
    end
    println()
end

println("\n Armazenamento (p):")
for h in Hydros
    println("Unit: ", h)
    for t in P
        @printf("Period %2d: p = %7.2f\n", t, value(armazenamento[h,t]))
    end
    println()
end


# Print deficit, demand, total generation
println("Period; Deficit; Demand; TotalGen")
for t in P
    totalgen = sum(value(p[u,t]) for u in N)
    @printf("%2d ; %8.4f ; %6.1f ; %8.2f\n", t, value(deficit[t]), Demanda[t], totalgen)
end

# Save summary table
rows = Any[]
for t in P
    push!(rows, (
        Period = t,
        Demand = Demanda[t],
        Deficit = value(deficit[t]),
        TotalGen = sum(value(p[u,t]) for u in N)
    ))
end

df_summary = DataFrame(rows)
CSV.write("summary_dispatch.csv", df_summary)
println("\nSummary written to summary_dispatch.csv and Operacao-Despacho.csv")

# Plot results
plt = @df df_summary plot(
    :Period,
    [:Demand, :Deficit, :TotalGen],
    xlabel="Period",
    ylabel="MW",
    lw=2,
    label=["Demand" "Deficit" "TotalGen"],
    title="Dispatch Summary"
)

savefig(plt, "dispatch_plot.png")
println("Plot saved as dispatch_plot.png")