


using HiGHS
using JuMP
using UnitCommitment
import Random
import UnitCommitment: XavQiuAhm2021
using Distributions
using JSON3


modified = UnitCommitment.read_benchmark("or-lib/10_0_1_w");
UnitCommitment.randomize!(modified)
UnitCommitment.generate_initial_conditions!(modified, HiGHS.Optimizer)
#modified = UnitCommitment.slice(instance, 1:2)
cenario_1 = modified.scenarios[1]


println("instance: ", modified.time)

vector_buses = cenario_1.buses
deficit = cenario_1.power_balance_penalty
println("deficit: ", deficit[1])

# Prepare a dictionary to hold the full instance
json_data = Dict(
    "instance" => modified.time,
    "deficit" => deficit[1],
    "buses" => []
)


for bus in vector_buses
    println("bus: ", bus.name)
    println("load: ", [round(x, digits=0) for x in bus.load])
    bus_dict = Dict(
        "bus" => bus.name,
        "load" => [round(x, digits=0) for x in bus.load],
        "thermal_units" => []
    )

    vector_thermal_units = bus.thermal_units
    for unidade_termica in vector_thermal_units
        println("nome: ", unidade_termica.name)
        #println("bus: ", unidade_termica.bus)
        println("max_power: ", unidade_termica.max_power[1])
        println("min_power: ", unidade_termica.min_power[1])
        #println("cost_segments: ", unidade_termica.cost_segments)
        first_costs = [cs.cost[1] for cs in unidade_termica.cost_segments]
        #println("CVU: ", first_costs)
        println("CVU: ", round(maximum(first_costs), digits=0))
        println("min_uptime: ", unidade_termica.min_uptime)
        println("min_downtime: ", unidade_termica.min_downtime)
        println("ramp_up_limit: ", round(unidade_termica.ramp_up_limit, digits = 2))
        println("ramp_down_limit: ", round(unidade_termica.ramp_down_limit, digits = 2))
        #println("startup_limit: ", unidade_termica.startup_limit)
        #println("shutdown_limit: ", unidade_termica.shutdown_limit)
        println("initial_status: ", unidade_termica.initial_status)
        println("initial_power: ", round(unidade_termica.initial_power, digits = 2) )
        #println("commitment_status: ", unidade_termica.commitment_status)

        unit_dict = Dict(
            "nome" => unidade_termica.name,
            "max_power" => unidade_termica.max_power[1],
            "min_power" => unidade_termica.min_power[1],
            "CVU" => round(maximum(first_costs), digits=0),
            "min_uptime" => unidade_termica.min_uptime,
            "min_downtime" => unidade_termica.min_downtime,
            "ramp_up_limit" => round(unidade_termica.ramp_up_limit, digits = 2),
            "ramp_down_limit" => round(unidade_termica.ramp_down_limit, digits = 2),
            "initial_status" => unidade_termica.initial_status, 
            "initial_power" => round(unidade_termica.initial_power, digits = 2) 
        )
        push!(bus_dict["thermal_units"], unit_dict)
    end

    push!(json_data["buses"], bus_dict)
end

open("C:/Users/testa/Documents/Doutorado_materias/Metaheuristica/output_instance.json", "w") do io
    JSON3.write(io, json_data; indent=4)
end


model =
    UnitCommitment.build_model(instance = modified, optimizer = HiGHS.Optimizer)
UnitCommitment.optimize!(model)

# 4. Write solution to a file
solution = UnitCommitment.solution(model)
UnitCommitment.write("output.json", solution)


println(json_data)