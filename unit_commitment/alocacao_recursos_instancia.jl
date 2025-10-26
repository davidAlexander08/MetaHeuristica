using JuMP
using GLPK      # replace with your solver if needed
using DataFrames
using CSV
using Printf
using Plots
using StatsPlots
using JSON

# Read the JSON file
json_data = open("C:/Users/testa/Documents/git/MetaHeuristica/unit_commitment/instancias/output_instance.json") do io
#json_data = open("C:/Users/testa/Documents/Doutorado_materias/Metaheuristica/instancia_teste_TOFF_sanidade.json") do io
    JSON.parse(IOBuffer(read(io, String)))
end


Terms = []
Custo = Dict()
LimiteSup = Dict()
LimiteInf = Dict()
TON = Dict()
Toff = Dict()
# Loop over buses (or access first bus)
Demanda = []
for bus in json_data["buses"]
    println("Bus name: ", bus["bus"])
    println("Load: ", bus["load"])
    append!(Demanda, bus["load"])
    # Loop over thermal units
    for unit in bus["thermal_units"]
        push!(Terms, unit["nome"])
        Custo[unit["nome"]] = unit["CVU"]
        LimiteSup[unit["nome"]] = unit["max_power"]
        LimiteInf[unit["nome"]] = unit["min_power"]
        TON[unit["nome"]] = unit["min_uptime"]
        Toff[unit["nome"]] = unit["min_downtime"]
        println("Unit name: ", unit["nome"])
        println(" CVU: ", unit["CVU"])
        println(" max_power: ", unit["max_power"])
        println(" min_power: ", unit["min_power"])
        println(" min_uptime: ", unit["min_uptime"])
        println(" min_downtime: ", unit["min_downtime"])
        println(" ramp_up_limit: ", unit["ramp_up_limit"])
        println(" ramp_down_limit: ", unit["ramp_down_limit"])
        println(" initial_power: ", unit["initial_power"])
        println(" initial_status: ", unit["initial_status"])
    end
end
N = Terms
P = 1:json_data["instance"]
penalty_deficit = json_data["deficit"]
println("P: ", P)
#Demanda = Float64.(bus["load"])
print("Demanda: ", Demanda)

## Dados
#Demanda = [90, 90, 110, 90, 90, 90, 90, 90]
#Custo = Dict("H1" => 0.0, "T1" => 10.0, "T2" => 20, "T3"=>21)
#LimiteSup = Dict("H1" => 200.0, "T1" => 100.0, "T2" => 100 , "T3" => 100)
#LimiteInf = Dict("H1" => 0.0,   "T1" => 10.0, "T2" => 10 , "T3" => 10)
#TON = Dict("T1" => 2, "T2" => 5, "T3" =>4)
#Toff = Dict("T1" => 1, "T2"=>1, "T3"=>1)

## Conjuntos
#Hydros = []
#Terms = ["T1", "T2", "T3", "T4", "T5", "T6"]
#N = Hydros ∪ Terms
#P = 1:8
#Demanda = [90, 90, 110, 90, 90, 90, 90, 90]
#Custo = Dict("T1" => 10.0, "T2" => 20, "T3"=>21, "T4"=>22, "T5" => 23, "T6" => 24)
#LimiteSup = Dict("T1" => 100.0, "T2" => 100 , "T3" => 100, "T4"=>100, "T5"=>100, "T6"=>100)
#LimiteInf = Dict("H1" => 0.0,   "T1" => 20.0, "T2" => 30 , "T3" => 10, "T4"=> 10, "T5"=> 10, "T6"=> 10)
#TON = Dict("T1" => 2, "T2" => 5, "T3" =>4, "T4" => 3, "T5" => 2, "T6" => 1)
#Toff = Dict("T1" => 1, "T2"=>1, "T3"=>1, "T4"=>1, "T5"=>1, "T6"=>1)

# Modelo
model = Model(GLPK.Optimizer)
set_silent(model)

# Variáveis
@variable(model, p[u in N, t in P] >= 0)
@variable(model, u[u in N, t in P], Bin)
@variable(model, deficit[t in P] >= 0)

# Limites de geração
for term in Terms, t in P
    @constraint(model, p[term,t] <= LimiteSup[term]*u[term,t])
    @constraint(model, p[term,t] >= LimiteInf[term]*u[term,t])
end


## TON
    for termica in N
        for periodo in P
            if periodo + TON[termica] > length(P)
                @constraint(model,
                    sum(u[termica, per] for per in periodo:length(P)) >=
                    Toff[termica] * u[termica, periodo] -
                    Toff[termica] * u[termica, periodo - 1]
                )
            elseif periodo <= 1
                @constraint(model,
                    sum(u[termica, per] for per in periodo:min(periodo + TON[termica] - 1, length(P))) >=
                    TON[termica] * u[termica, periodo]
                )
            elseif periodo >= 2
                @constraint(model,
                    sum(u[termica, per] for per in periodo:min(periodo + TON[termica] - 1, length(P))) >=
                    TON[termica] * u[termica, periodo] -
                    TON[termica] * u[termica, periodo - 1]
                )
            end
        end
    end


##TOFF
    for termica in N
        for periodo in P
            if periodo + Toff[termica] > length(P)
                @constraint(model,
                    sum( (1 - u[termica, per]) for per in periodo:length(P)) >=
                    (length(P)-periodo) * u[termica, periodo - 1] - 
                    (length(P) - periodo) * u[termica, periodo]
                    
                )
            elseif periodo <= 1
                @constraint(model,
                    sum( (1- u[termica, per]) for per in periodo:min(periodo + Toff[termica] - 1, length(P))) >=
                    -Toff[termica] * u[termica, periodo]
                )
            elseif periodo >= 2
                @constraint(model,
                    sum((1- u[termica, per]) for per in periodo:min(periodo + Toff[termica] - 1, length(P))) >=
                    Toff[termica] * u[termica, periodo - 1] - 
                    Toff[termica] * u[termica, periodo]
                )
            end
        end
    end

# Balanço de energia
for t in P
    println("t: ", t)
    println("t: ", Demanda[t])
    println(sum(p[u,t] for u in N) + deficit[t] == Demanda[t])
    @constraint(model, sum(p[u,t] for u in N) + deficit[t] == Demanda[t])

end

# Função objetivo
@objective(model, Min, 
    sum(Custo[u] * p[u,t] for u in N, t in P) + penalty_deficit * sum(deficit[t] for t in P))

print(model)
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