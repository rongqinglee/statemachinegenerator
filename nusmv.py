import yaml
import specification
from nusmvbdr import ExpressionBuilder, ExpressionDefinitionBuilder, CaseDefinitionBuilder
import movement


def genmodel(in_file, out_file):
    specstream = open(in_file, "r")
    specs = yaml.safe_load(specstream)

    modelstream = open(out_file, "w")

    worldspec = specification.WorldSpec(specs["world"])
    islandspec = specification.IslandSpec(specs["island"])
    penguinspec = specification.PenguinSpec(specs["penguin"])
    snowballspec = specification.SnowballSpec(specs["snowball"])

    sbdefs = sbdefinitions(worldspec, islandspec, penguinspec, snowballspec)
    pgdefs = pgdefinitions(worldspec, islandspec, penguinspec, snowballspec)

    modelstream.write("// Snowball definitions\n\n")
    modelstream.write('\n\n'.join(list(map(lambda x: x.build(), sbdefs))))

    modelstream.write("\n\n// Penguin definitions\n\n")
    modelstream.write('\n\n'.join(list(map(lambda x: x.build(), pgdefs))))


def sbdefinitions(worldspec, islandspec, penguinspec, snowballspec):
    definitions = []

    flies = movement.moves(snowballspec.flyvel)
    definitions += [movecase(list(map(lambda point: point[0], flies)), "FlyOX")]
    definitions += [movecase(list(map(lambda point: point[1], flies)), "FlyOY")]

    return definitions


def pgdefinitions(worldspec, islandspec, penguinspec, snowballspec):
    definitions = []

    moves = movement.moves(penguinspec.movevel)
    definitions += [moveexp(moves, "MoveNext")]

    return definitions


def moveexp(points, name):
    fullexp = None
    direxp = ExpressionBuilder("direction")
    nextxexp = ExpressionBuilder("x").withnext()
    nextyexp = ExpressionBuilder("y").withnext()

    direction = 0
    for i in range(1, len(points) + 1):
        if i == len(points) or points[i][0] != points[direction][0] or points[i][0] != points[direction][1]:
            if (i - direction) > 1:
                expression = direxp.within(ExpressionBuilder(direction, i-1))
            else:
                expression = direxp.witheq(ExpressionBuilder(direction))

            expression = expression.withand(nextxexp.witheq(ExpressionBuilder(points[direction][0])))
            expression = expression.withand(nextyexp.witheq(ExpressionBuilder(points[direction][1])))

            if fullexp is None:
                fullexp = expression
            else:
                fullexp = fullexp.withnewline().withor(expression)

            direction = i

    return ExpressionDefinitionBuilder(name).withexp(fullexp.build())


def movecase(values, name):
    casebdr = CaseDefinitionBuilder(name)
    direxp = ExpressionBuilder("direction")

    direction = 0
    for i in range(1, len(values) + 1):
        if i == len(values) or values[i] != values[direction]:
            if (i - direction) > 1:
                expression = direxp.within(ExpressionBuilder(direction, i-1))
            else:
                expression = direxp.witheq(ExpressionBuilder(direction))
            casebdr = casebdr.withcase(expression.build(), ExpressionBuilder(values[direction]).build())
            direction = i

    return casebdr