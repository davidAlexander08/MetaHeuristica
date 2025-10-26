using JuMP
using GLPK
using DataFrames
using Plots

# -----------------------------
# DADOS DO PROBLEMA
# -----------------------------
# Conjunto de unidades
unidades = [:U1, :U2, :U3]
periodos = 1:3

# Parâmetros
Pmin = Dict(:U1 => 50.0, :U2 => 30.0, :U3 => 0.0)
Pmax = Dict(:U1 => 150.0, :U2 => 100.0, :U3 => 60.0)
Cvar = Dict(:U1 => 20.0, :U2 => 40.0, :U3 => 80.0)       # custo variável (R$/MWh)
Cfix = Dict(:U1 => 10.0, :U2 => 5.0,  :U3 => 2.0)        # custo fixo quando ligada
Cstart = Dict(:U1 => 120.0, :U2 => 50.0, :U3 => 10.0)    # custo de partida
rampa = Dict(:U1 => 100.0, :U2 => 80.0, :U3 => 60.0)     # limite de rampa (MW/periodo)
demanda = Dict(1 => 120.0, 2 => 160.0, 3 => 140.0)       # MW

# -----------------------------
# MODELO
# -----------------------------
model = Model(GLPK.Optimizer)

@variables(model, begin
    0 <= P[u in unidades, t in periodos] <= Pmax[u]     # geração (MW)
    x[u in unidades, t in periodos], Bin                 # 1 se ligada
    y[u in unidades, t in periodos], Bin                 # 1 se liga no período
end)

# -----------------------------
# RESTRIÇÕES
# -----------------------------

# Limite mínimo e máximo
@constraints(model, begin
    [u in unidades, t in periodos], P[u,t] >= Pmin[u] * x[u,t]
    [u in unidades, t in periodos], P[u,t] <= Pmax[u] * x[u,t]
end)

# Balanço de potência
@constraint(model, [t in periodos], sum(P[u,t] for u in unidades) == demanda[t])

# Rampa
@constraints(model, begin
    [u in unidades, t in 2:3], P[u,t] - P[u,t-1] <= rampa[u]
    [u in unidades, t in 2:3], P[u,t-1] - P[u,t] <= rampa[u]
end)

# Relação startup (ligamento)
@constraint(model, [u in unidades, t in 1:3],
    y[u,t] >= x[u,t] - (t == 1 ? 0 : x[u,t-1])
)

# -----------------------------
# FUNÇÃO OBJETIVO
# -----------------------------
@objective(model, Min,
    sum(Cvar[u]*P[u,t] + Cfix[u]*x[u,t] + Cstart[u]*y[u,t] for u in unidades, t in periodos)
)

# -----------------------------
# SOLVER
# -----------------------------
optimize!(model)

println("\nStatus da Otimização: ", termination_status(model))
println("Custo total mínimo = ", objective_value(model))

# -----------------------------
# RESULTADOS
# -----------------------------
Psol = value.(P)
xsol = value.(x)

println("\nGeração ótima (MW):")
for u in unidades
    println(u, ": ", [round(Psol[u,t], digits=1) for t in periodos])
end

println("\nLigamento (1=on, 0=off):")
for u in unidades
    println(u, ": ", [Int(round(xsol[u,t])) for t in periodos])
end

# Tabela resumida
df = DataFrame(Unit = repeat(unidades, inner=length(periodos)),
               Period = repeat(periodos, outer=length(unidades)),
               Commitment = [Int(round(xsol[u,t])) for u in unidades for t in periodos],
               Generation = [round(Psol[u,t], digits=1) for u in unidades for t in periodos])
println("\nTabela resumo:")
println(df)

# -----------------------------
# PLOT (Geração empilhada)
# -----------------------------
plot(
    periodos,
    [Psol[u,t] for u in unidades, t in periodos]',
    label = string.(unidades),
    xlabel = "Período",
    ylabel = "Geração (MW)",
    title = "Despacho ótimo - Unit Commitment (3 períodos)",
    lw = 2,
    fill = (0, 0.4)
)
