using HiGHS, JuMP

model = Model(HiGHS.Optimizer)

@variable(model, x1)
@variable(model, x2>=0)
@variable(model, x3>=0)

@objective(model, Max, 2x1-x2+2x3)

@constraint(model, -x1 - 2x2 + x3 >= -1)
@constraint(model, x1 - x2 + x3 == 3)
@constraint(model, x2<=-1)

optimize!(model)
