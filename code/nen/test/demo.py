from nen import Problem


problem_names = ['BerkeleyDB', 'ERS', 'WebPortal', 'Drupal', 'Amazon', 'E-Shop',
                 'rp', 'ms', 'Baan', 'classic-1', 'classic-2', 'classic-3', 'classic-4', 'classic-5']
for problem_name in problem_names:
    problem = Problem(problem_name)
    print(problem.name, ': ', problem.variables_num, ' ', problem.constraints_num)