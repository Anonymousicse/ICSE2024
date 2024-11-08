# Nen 工程文档

## 入门

### 关于环境配置

`doc/requirements.txt` 是依赖文件, 可以通过 `pip install -r requirements.txt` 配置.

Cplex 需要额外配置, 各版本下载: 
https://115.com/s/sw6nzk036m7?password=k767&#CPLEX
访问码：k767

Java 环境 (songhua) 请使用 Maven 配置, POM 在 `songhua/pom.xml`.

### 工程大体结构

`Nen` 文件夹结构如下:

* data
* doc
* example
* experiment
* lib
* nen
* songhua

`data` 中存储了数据文件, `doc` 中为文档文件夹(本文档), `example` 包含了一些样例, `lib` 是若干 Java 实现的求解器 (如: NSGAII.jar 是 基于 JMetal 的 NSGA-II 求解器);
`nen` 是本项目的 Python 源码, `songhua` 是本项目的 Java 源码.

### 基本原理

`data` 中存储了数据文件, 也就是问题数据, 包括 NRP 与 FSP, 文件名就是问题的名字.
使用 `Problem`, `LP`, 或 `QP` 可以用问题的名字将问题加载, 如:

```Python
from nen import LP

# load `ms.json` from `data` folder
# objective order is 'cost', 'revenue'
problem = LP('ms', ['cost', 'revenue'])
```

然后, 根据问题的需要选择或者自定义求解器:

```Python
from nen.Solver import ExactECSolver

result = ExactECSolver.solve(problem)
```

结果`result`包含两部分, `elapsed` 和 `solution_list`, 前者记录了求解器运行时间, 后者记录了求出的解. 对于单目标问题而言, 只有存在或不存在解两种情况, 可以使用 `result.single` 获得;而对于多目标问题而言, `solution_list` 是一个非支配解解集.

最后, 我们需要根据问题, 算法, 迭代来管理这些结果:

```Python
from nen import ProblemResult, MethodResult

problem_result = ProblemResult('ms', problem)
exact_method_result = MethodResult('exact-ec', problem_result.path, problem)
exact_method_result.add(result)
problem_result.add(exact_method_result)
```

`ProblemResult` 管理同一问题的不同算法/方法/求解器参数 (Method) 的结果, 即 `MethodResult`. `MethodResult` 管理同一问题同一方法多次迭代的结果, 即 `Result`.
此时, 实验结果仍在内存中. 为了方便起见, 可以将实验结果存储在硬盘上:

```Python
problem_result.dump()
```

## Nen 工程细节

### 问题相关文件

#### `Preprocess`

原问题数据均存储于 `data/raw` 文件下, 为了统一问题描述方法, 我将这些数据集转化为统一的问题描述文件 `.json` 形式. 转化的流程在 `Preprocess.py` 中展示. 实验中不会用到该代码文件, 只是用于保留数据转化前后是否一致的验证可能. 如果有新的数据加入到实验, 可以沿袭这个处理方法.

#### `DescribedProblem`

`DescribedProblem` 是问题描述的抽象, 在 `DescribedProblem.py` 中定义. 
一个问题描述文件 `.json` 由三部分组成:

* variables, 变量名称
* objectives, 优化目标 (最小化方向)
* constraints, 约束

其中, 变量名称是一个字符串列表, 各变量并无先后顺序, 因为在目标和约束中均使用变量名作为唯一索引. 优化目标是一个字典, 从目标名映射到"目标" (变量: 参数 的字典). 约束由若干三元数组构成, 每个约束的三部分分别为 `left` "左值", `sense` "符号", `right` "右值". 其中, `sense`
唯一确定约束的类型和格式.

* 线性等式, `[{variable: coef}, "=", constant]`
* 线性不等式, `[{variable: coef}, "<=", constant]`, 注: 只有 `"<="` 方向
* 等值, `[A, "<=>", B]`
* 互斥, `[A, "><", B]`
* 或, `[[a1, a2, ...], "or", B]`
* 选择, `[[a1, a2, ...], "alt", B]`

以 `BerkeleyDB.json` 为例 (为美观对排版稍作改动):

```json
{
  "variables": [ // 变量名列表
    "berkeleydb", "statistics", "cryptography", "indexes",
    "btree", "btreefast", "btreesmall", "hash", "queue",
    "replication", "verification", "diagnostic", "sequence"
  ],
  "objectives": { // 优化目标字典
    "COST": { // 目标 'COST', Min 10.2 x berkeleydb + 14 x statistics + ...
      "berkeleydb": 10.2, "statistics": 14.0, "cryptography": 5.2,
      "indexes": 5.7, "btree": 12.2, "btreefast": 4.2, "btreesmall": 3.5,
      "hash": 9.2, "queue": 19.9, "replication": 17.9, "verification": 14.0,
      "diagnostic": 18.2, "sequence": 5.9
    },
    "USED_BEFORE": { // 目标 'USED_BEFORE', Min indexes + btree + queue + ...
      "berkeleydb": 0, "statistics": 0, "cryptography": 0, "indexes": 1,
      "btree": 1, "btreefast": 0, "btreesmall": 0, "hash": 0, "queue": 1,
      "replication": 0, "verification": 1, "diagnostic": 1, "sequence": 0
    },
    "DEFECTS": { // 目标 'DEFECTS', Min 9 x berkeleydb + 8 x statistics + ...
      "berkeleydb": 9, "statistics": 8, "cryptography": 10, "indexes": 0,
      "btree": 0, "btreefast": 5, "btreesmall": 4, "hash": 4, "queue": 0,
      "replication": 3, "verification": 0, "diagnostic": 0, "sequence": 4
    },
    "DESELECTED": { // 目标 'DESELECTED', Min - berkeleydb - statistics - ...
      "berkeleydb": -1, "statistics": -1, "cryptography": -1, "indexes": -1,
      "btree": -1, "btreefast": -1, "btreesmall": -1, "hash": -1, "queue": -1,
      "replication": -1, "verification": -1, "diagnostic": -1, "sequence": -1
    }
  },
  "constraints": [ // 约束
    [{"berkeleydb": 1}, "=", 1], // 1 x berkeleydb = 1
    ["statistics", "=>", "berkeleydb"], // statistics => berkeleydb
    ["cryptography", "=>", "berkeleydb"], // cryptography => berkeleydb
    ["indexes", "<=>", "berkeleydb"], // indexes <=> berkeleydb
    ["replication", "=>", "berkeleydb"], // replication => berkeleydb
    ["verification", "=>", "berkeleydb"], // verification => berkeleydb
    ["diagnostic", "=>", "berkeleydb"], // diagnostic => berkeleydb
    ["sequence", "=>", "berkeleydb"], // sequence => berkeleydb
    ["btree", "<=>", "indexes"], // btree <=> indexes
    ["hash", "=>", "indexes"], // hash => indexes
    ["queue", "=>", "indexes"], // queue => indexes

    // btree is the parent node, btreefast and btreesmall are children nodes
    // (btreefast + btreesmall" <= 1)
    // and (btreefast => btree) and (btreesmall => btree)
    // and (btree => (btreefast or btreesmall))
    [["btreefast", "btreesmall"], "alt", "btree"]
  ]
}
```

#### `Problem`, `LP`, 和 `QP`

`Problem`, `LP`, 和 `QP` 在 `Problem.py` 中得到定义, 其中 `LP` 和 `QP` 是 `Problem` 的子类, 因此只需要重点了解 `Problem` 即可. 

`Problem` 是本工程的核心类之一, 当调用 `Problem.__init__` 时, `Problem` 会根据给定的问题名称, 借助 `DescribedProblem` 载入该问题, 其类的结构就是问题的统一格式:

* `name`, 问题名字.
* `variables`, `objectives`, `constraints`, 同前文的 `DescribedProblem` 为问题的结构. 注意 此处的 `constraints` 是 `Term::Constraint` 的列表, 它将三元列表抽象为一个类, 并定义了一些操作/方法/函数.
* `variable_num`, `objectives_num`, `constraints_num` 是 `variables`, `objectives`, `constraints` 的计数, 载入时确定.
* `violateds_count`, 非法约束计数开关. 当 `violateds_count=True` 时, 在为某一解进行赋值时, 统计多少约束没有得到满足 (解中的非法约束计数是 0 为可行解); 当 `violateds_count=False` 时, 只统计是否为可行解 (解中的非法约束计数是 0 为可行解).

同样, 为了求解的便捷, `Problem` 中会为变量和优化目标进行向量化处理.

* `variables_index`, 变量名对应索引编号, 初始化时生成.
* `objectives_order`, 优化目标名称顺序, 调用 `Problem.vectorize` 时作为输入参数记录. 注: `objectives_num` 会更改为 `len(objectives_order)`, 也就是说, 并不是所有优化目标都需要排序的, 只关注问题需要的目标即可.
* `objectives_index`, 优化目标名称索引, 调用 `Problem.vectorize` 时生成.
* `objectives_matrix`, 优化目标矩阵, 每一行是一个优化目标, 顺序由 `objectives_order` 确定; 每一行的优化目标是一个系数向量, 每一列对应 `variables_index` 中相应变量的系数.

`Problem` 类的另一功能就是为'解'赋值. 问题在某一求解器求解后, 得到若干解. 这些'解'其实是对于变量的取值. 通过变量的取值得出原问题中各个优化目标的取值, 以及统计哪些约束得到满足的这一过程称之为解的 `evaluate` '赋值'. 虽然没有写作模板类, 但倘若继承 `Problem` 类, 一定要实现 `Problem.evaluate` 方法.

`LP`, 缩写自 'Linear Programming', 意为线性规划 (问题), 继承自 `Problem`.
它将 `Problem.constraints` 从逻辑表达式转化为 `LP.constraints_lp` 线性规划形式.
注: 转化后线性规划约束**不能**与原约束列表共享索引.

`QP`, 缩写自 'Quadratic Programming', 意为二次规划 (问题)
注: 转化后二次规划约束**不能**与原约束列表共享索引.

### 基本概念项 

`Term.py` 中有三个类 `Linear`, `Quadratic`, 和 `Constraint`.

`Linear` 是线性等式或不等式, `Quadratic` 是最小化二次多项式.
`Constraint` 前文提过, 是逻辑约束的类. 里边包含一些线性或二次规划的转化操作方法.
如 `Constraint.to_linear` 是将逻辑约束转化为线性等式/不等式的集合 (可能一个逻辑约束对应多个线性不等式组); `Constraint.to_quadratic` 是将本逻辑约束转化为**一个**最小化二次多项式 (如果转化后也是一对多的关系, 则直接相加). `Constraint.evaluate` 即根据变量取值判别本约束是否得到满足. 此外, 还有一些辅助或者是工具性质的方法, 可以参考源码.

解的类型我使用了 JMetal 的 `BinarySolution` (`from jmetal.core.solution import BinarySolution`). 注意, `BinarySolution.variables` 是二位数组, 我们使用可以当作一维处理:
`BinarySolution.variables = [[True, False, False, True, ...]]` 只使用第一行, 当访问的时候需要使用 `BinarySolution.variables[0]`.

### 求解器

`Nen` 的所有 Python 实现的求解器均处于 `nen/Solver` 文件夹下, 此外 `.jar` 求解器处于 `lib` 内, 在使用 Python 调用它们时使用接口 `nen/Solver/JarSolver.py`.

#### 基础求解器

`MetaSolver.py`, `JarSolver`, 和 `EmbeddingSampler.py` 分别包含了各自方向的基础求解部件.

##### `SolverUtil` 和 `ExactSolver`

在 `MetaSolver.py` 中, `SolverUtil` 类作为求解的工具类承担了目标缩放, 最大/最小梯度计算, 加权求和, 计时(`SolverUtil.time()`)等工作.

另一个类 `ExactSolver` 则是对 Cplex 求解器的封装以及延伸. 可以通过修改 `ExactSolver.CPLEX_THREADS` 控制线程数 (0 代表自动, 1 为串行). `ExactSolver` 的初始化是由给定问题 (`LP`类型), 调用 `ExactSolver.initialized_cplex_solver` 进行初始化. 在这个函数内, 它进一步地, 调用 `ExactSolver.variables_initialized_cplex_solver` 初始化 Cplex 求解器并输入变量名称和类型 (`B` 意为 'Binary' 二值变量). 注意, 在这个函数内设计的 Cplex 求解器操作解释如下:

```Python
@staticmethod
def variables_initialized_cplex_solver(variables: List[str]) -> Cplex:
    """variables_initialized_cplex_solver [summary] initialize a cplex with variables,
    left objectives and constraints unset.
    """
    # 准备 Cplex 求解器
    solver: Cplex = Cplex()
    # 输出流设置, 我这里置空不允许它在控制台打印消息
    solver.set_results_stream(None)
    solver.set_warning_stream(None)
    solver.set_error_stream(None)
    # 设置线程数, 0 自动, 1 串行, > 1 时按给定线程并行
    solver.parameters.threads.set(ExactSolver.CPLEX_THREADS)
    # 设置偏差容忍, 0 意味着求出精确的最优解, 而非足够近似的最优解
    solver.parameters.emphasis.mip.set(0)
    solver.parameters.mip.tolerances.absmipgap.set(0.0)
    solver.parameters.mip.tolerances.mipgap.set(0.0)
    # 设置最大求解时间, 一般用于无法短时间内求解出精确解时放弃求解, 这里注释掉了
    # solver.parameters.timelimit.set(10000)
    # solver.parameters.dettimelimit.set(10000)
    # 添加变量, lb 和 ub 是变量的上下界, 项目内所有问题都是二值变量不需要设置
    # 'B' for Binary, names 指定了变量的名称列表
    solver.variables.add(obj=None, lb=None, ub=None, types='B' * len(variables), names=variables, columns=None)
    return solver
```

随后, `ExactSolver.initialized_cplex_solver` 为这个初始化后的求解器添加约束 (调用了 `ExactSolver.add_constraint`). 在求解之前, 我们还需要对优化目标进行设置, 这里提供了两个方法
`ExactSolver.set_minimizing_objective` 设置最小化目标, 另一个是针对二次多项式目标的 `ExactSolver.set_minimizing_qudratic_objective`.

将问题的全部信息都输入到求解器后, 下面就是求解, 包括 `ExactSolver.solve` 进行求解, `ExactSolver.solve_and_count` 求解并返回求解时间, `ExactSolver.solve_and_get_values` 求解并按照输入的变量名称表返回各个变量的取值 (字典键值对). 对于没有取解的求解方法, 可以使用 `ExactSolver.get_values` 按照输入的变量名称表返回上次求解的各个变量的取值. 值得注意的是,
虽然是二值变量, 但由于种种原因 (浮点数精度), 求得变量的取值可能并不完全等于 `0/1`, 我使用了 `</> 0.5` 进行判别.

最后, `ExactSolver` 甚至提供了 epsilon-constraint 求解方法 `ExactSolver.epsilon_constraint`, 它需要参数 `step` 指的是每次边界更新的步长.

##### `JarSolver`

`JarSolver` 所做的事其实就是在控制台执行了运行 `.jar` 求解器的命令. 所有的问题信息是通过文件传输的, 当 `JarSolver.solve` 被调用, 它会根据求解器的名称调用某一 `.jar`, 将所有参数输出到 `dump` 文件夹的某一个参数文件; 然后, 求解器会读入参数文件并根据指定的问题名称载入问题, 再根据求解参数初始化求解器, 随后根据指定位置输出求解结果.

**值得注意的是, 调用 `JarSolver` 的时候, 确保代码文件处于 `Nen` 文件夹中, 否则 `.jar` 求解器无法确认问题数据文件的位置.**

##### `EmbeddingSampler`

与 `ExactSolver` 类似, 这个类是对 D'Wave Leap 求解器的封装, 并沿用的 'embedding sampler' 的名字. 如名字所示, 它做了两件事: 嵌入和采样. `EmbeddingSampler` 初始化是沿用 D'Wave 的求解器的, 能够正常使用不会产生奇怪的问题, 也不需要理解. 其中, 求解/采样的方法是 `EmbeddingSampler.sample`, 我以这个函数为切入讲解:

```Python
def sample(self, qubo: Dict[Tuple[str, str], float], **parameters) -> Tuple[SampleSet, float]:
    """sample [summary] sample qubo with paramters passed to sampler.
    """
    # 将 QUBO 转化为 BQM, 没什么太大意义, 仅为习惯
    bqm = BinaryQuadraticModel.from_qubo(qubo)
    # embed, embedding: {var -> (qi)}
    # bqm_embedded: BinaryQuadraticModel({q -> bias}, {(q, q) -> offset}, constant, type}
    # to access lp/qp part: bqm_embedded.linear, bqm_embedded.quadratic
    embedding, bqm_embedded = self.embed(bqm)
    # 注意 bqm 是问题, embedding 是原问题中逻辑变量到量子退火机中的量子比特链的映射
    # bqm_embedding 即为嵌入后的问题形式

    # warings handle, 沿袭原 D'Wave 的求解器, 不需要管
    warnings = WarningAction.IGNORE
    warninghandler = WarningHandler(warnings)
    warninghandler.chain_strength(bqm, embedding.chain_strength, embedding)
    warninghandler.chain_length(embedding)

    # initialize state for reversed anneal
    # initialize state 是反向退火用的, 为初始状态进行赋值, 可以不用管
    if 'initial_state' in parameters:
        # state: variable_name -> {0, 1}
        # Here, for each var: (u1, u2, ...), u1 = u2 = ... = state[var]
        state = parameters['initial_state']
        parameters['initial_state'] = {u: state[v] for v, chain in embedding.items() for u in chain}

    # sample on QPU, 提交问题到 D'Wave Leap 平台
    response = self.sampler.sample(bqm_embedded, **parameters)

    # unembed, 异步获得解, 恢复原问题的采样解集 sampleset
    async_unembed = partial(EmbeddingSampler.async_unembed_complete,
                            embedding=embedding,
                            bqm=bqm,
                            warninghandler=warninghandler)
    sampleset = dimod.SampleSet.from_future(response, async_unembed)
    # 这里将运行时间拆出来了 (QPU时间, 具体计算方法请参考我的学位论文附录, 或查看源码)
    return sampleset, EmbeddingSampler.get_qpu_time(sampleset)
```

`EmbeddingSampler` 中还有一些极为重要的方法, 除了 `EmbeddingSampler.get_qpu_time` 拿到多次采样的时间外, `EmbeddingSampler.get_values_and_occurrence` 可以根据给定的 `sampleset` 拿到其中的解集 (不会排序, 只合并相同解) 并计算每个解出现的次数. `EmbeddingSampler.get_values` 则不会统计解出现的次数. (`EmbeddingSampler.sample_to_values` 是将一个采样结果转化为原问题变量的取值, 看起来很重要但在当前项目中并没有调用.)

`EmbeddingSampler.calculate_penalty` 在给定目标多项式 (最小化) 和约束多项式 (最小化)后, 计算惩罚因子的方法.

此外, `EmbedingSampler.refinement_sample` 是一次失败的优化采样方法, 它期望通过上次采样的最有解作为下次求解的初始化, 然后多次采样, 但似乎没什么用. 当然可以试试, 说不定我弄错了. 后面的能量比较等若干方法其实都是优化采样法的各种判别方法的尝试, 不需要了解.

#### 精确性求解

精确性求解指的是使用线性规划求解器 Cplex 进行求解的方法, 包括 `ExactECSolver`, `ExactIECSolver`, `ExactWSOSolver`, `ExactWSOQPSolver`, `ExactECQPSolver`, `SolRep3DSolver`
其中, `EC` 指的是 ;epsilon-constraint' 算法, `IEC` 指的是 'improved epsilon-constraint' 算法, `WSO` 指的是给定目标权值进行单目标求解, `QP` 指的是按照二次规划的形式使用 Cplex 求解, 可以用于验证: 其他 QP 算法, QP 建模是否正确 (一个问题转化为 LP 和 QP 形式的最有解应该保持一致, `ExactWSOQPSolverTest.py` 就是验证了这件事).

`SolRep3DSolver` 是三维问题的 `SolRep` 请参考我的学位论文.

#### 随机算法

这里的随机算法包括 `FSAQPSolver`, `SAQPSolver`, `SASolver`, `TabuQPSolver`, `RandomSolver`.
其中 `QP` 指的是将问题转化为最小化二次规划多项式形式求解, 但 `SASolver` 直接求解原问题而不建模. `FSA` 指的是 'Fast SA' 调用了 'sko.SA' (需要安装 `scikit-opt` Python 库), 很遗憾这个算法我还没有测试过.
`SA` 指的是标准的模拟退火算法 (教科书算法), `Tabu` 则是禁忌搜索, 一种邻域搜索算法.

`RandomSolver` 指的是随机算法, 完全随机生成解. 这个算法没有实用意义, 是之前用于验证量子退火技术的方法 (如果量子退火算法得到的解和随机生成效果相近, 那么该技术就是个骗局. 幸运的是, 量子退火算法表现要比 `RandomSolver` 结果好得太多.)

#### 量子退火

包括 `MOQASolver`, `QAECSolver`, `QAWSOSolver`, `RQAWSOSolver`.
其中 `WSO` 指的是给定权值的单目标优化, `RQA` 指的就是 'QA with refinement' 是一个失败的尝试. `QAEC` 指的是使用 'epsilon-constraint' 技术, 将求解器换成量子退火采样.

`MOQA` 就是本项目的核心, 多目标量子退火算法, 它的实现很简单:

```Python
@staticmethod
def solve(problem: QP, sample_times: int, num_reads: int) -> Result:
    """solve [summary] solve qp, results are recorded in result.
    """
    # 目标函数的缩放
    basic_weights = SolverUtil.scaled_weights(problem.objectives)

    samplesets: List[SampleSet] = []
    elapseds: List[float] = []
    # 多次采样, 每次选择一个随机方向 random_normalized_weights
    for _ in range(sample_times):
        weights = MOQASolver.random_normalized_weights(basic_weights)
        # 求出当前权重下的聚合目标, 解出惩罚因子, 计算得到问题的 QUBO
        wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.objectives, weights))
        penalty = EmbeddingSampler.calculate_penalty(wso, problem.constraint_sum)
        objective = Constraint.quadratic_weighted_add(1, penalty, wso, problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        # Solve in QA, 求解
        sampler = EmbeddingSampler()
        sampleset, elapsed = sampler.sample(qubo, num_reads=num_reads)
        samplesets.append(sampleset)
        elapseds.append(elapsed)
    # put samples into result, 收集所有目标并进行非支配排序
    result = Result(problem)
    for sampleset in samplesets:
        for values in EmbeddingSampler.get_values(sampleset, problem.variables):
            solution = problem.evaluate(values)
            result.add(solution) # Result 类继承自 NDArchive (非支配解集, 进行了排序)
    # add into method result
    result.elapsed = sum(elapseds)
    if 'solving info' not in result.info:
        result.info['solving info'] = [sampleset.info]
    else:
        result.info['solving info'].append(sampleset.info)
    # storage parameters
    result.info['sample_times'] = sample_times
    result.info['num_reads'] = num_reads
    return result
```

### 结果管理

`Result.py` 中包含了这些类:
* `NDArchive`, `jmetal.util.archive.NonDominatedSolutionsArchive` 的封装, 管理非支配解解集.
* `Result`, 继承自 `NDArchive` 是某问题某方法一次迭代求解的结果单位, 包含了解集和求解时间, 更多的信息可以存储在 `Result.info` 字典中 (比如量子退火的很多细节).
* `MethodResult`, 管理某问题某方法的全部结果, 指的是多次运行的 `Result` 的集合 (随机算法需要多次运行取平均值).
* `HashableObjectives`, 将一个解根据其目标值列表转化为 hashable 类, 这样可以加快相同解的对比速度.
* `ProblemArchive`, 管理某问题所有方法的解集, 并维持一个问题的总解集来归纳原问题的显存的非支配解, 用于统计每个方法分别找到了多少原问题的非支配解; 并可以计算一些指标如 'igd', 'hv', 'sp'.
* `ProblemResult`, 管理某问题所有方法的解集, 包括生成 `ProblemArchive`, 存储结果, 载入结果等操作, 并集成了计算某问题下两方法的全部指标.

在操作中, 最常用的是 `MethodResult` 和 `ProblemResult`.
在本项目中, 基于 Python 的求解器每次求解应返回一个 `Result`, 多次运行则需要将结果加入到 `MethodResult`. 而基于 Java 的求解器需要指定文件路径再载入到内存. 随后, `MethodResult` 会根据方法名称加入到 `ProblemResult` 并进行下一步的存储或是比较.

**比较的是什么?** 比较的究竟是 `MethodResult` 中的每一次运行结果的平均, 还是全部运行结果的总和 `MethodResult.method_result` ? 一般而言, 对于不需要平均的算法, 比较其总和(即单次运行结果)即可 `ProblemResult.result_compare`; 而针对多次运行取平均, 则需要把每次结果进行计算, 并取平均值.

对于 `ProblemResult.union_average_compare`, 它只比较两个方法, 且一个需要平均 (`average_method`), 一个不需要平均 (`union_method`):

```Python
def union_average_compare(self, union_method: str, average_method: str) -> List[Dict[str, float]]:
    """union_average_compare [summary] return union method compared with average method with scores indicated by
    [elapsed time, found, front, igd, hv, spacing].
    """
    assert union_method in self.methods_results
    assert average_method in self.methods_results
    # 准备不需要平均的结果
    union_method_result = self.methods_results[union_method]
    if union_method_result.method_result is None:
        union_method_result.make_method_result()
    union_result = union_method_result.method_result
    assert union_result is not None
    # 准备需要平均的结果
    average_method_result = self.methods_results[average_method]
    iteration = average_method_result.iteration
    # 计算平均时间
    average_elapsed = sum(average_method_result.get_elapseds()) / iteration
    # 准备每次运行结果
    average_results = average_method_result.results
    # 比较运行时间, {非平均方法: 运行时间, 平均方法: 平均运行时间}
    elapsed = {union_method: union_result.elapsed, average_method: average_elapsed}
    # 寻找到的非支配解数量 (分别), {非平均方法: 解集大小, 平均方法: 解集大小平均}
    found = {union_method: len(union_result),
                average_method: (sum([len(r) for r in average_results]) / iteration)}
    # 其余指标
    front_all: List[Dict[str, float]] = []
    igd_all: List[Dict[str, float]] = []
    hv_all: List[Dict[str, float]] = []
    sp_all: List[Dict[str, float]] = []
    # 针对平均方法的每次运行结果
    for i in range(iteration):
        average_result = average_results[i]
        # 将平均方法第 i 次结果与非平均方法当作两种非平均方法进行比较
        problem_archive = \
            ProblemArchive(self.problem, {union_method: union_result, average_method: average_result})
        # 记录每一次的"多少解在总的非支配解上", 其中非平均方法的一切指标都不会随着迭代改变
        front_all.append({k: float(v) for k, v in problem_archive.on_pareto_count().items()})
        # 记录每一次的 IGD, HV, SP
        igd_all.append(problem_archive.compute_igd())
        hv_all.append(problem_archive.compute_hv())
        sp_all.append(problem_archive.compute_sp())
    # 收集全部比较数据, 计算平均方法的平均值
    scores = [elapsed, found, ProblemResult.average_of_dicts(front_all),
                ProblemResult.average_of_dicts(igd_all),
                ProblemResult.average_of_dicts(hv_all),
                ProblemResult.average_of_dicts(sp_all)]
    return scores
```

最后的 `scores` 就是原始比较得出的数据, 它是一个列表, 每一项代表了一个指标; 在每个指标下, 是一个字典, 记录了 `{非平均方法: 该算法的该指标得分, 平均方法: 该算法的该指标平均得分}`.
值得注意的是, 非平均方法在后面的几个指标上其实也经历了"平均"的过程, 但不影响结果. (但可能会因为浮点数精度造成偏差, 需要额外注意, 但我没遇到过这个问题).

拿到 `scores` 并非重点, 需要将这个结果转化为图表, 这就涉及到 `Visualizer.py` 中的 `Visualizer` 类.

* `tabulate_single_problem`, 针对一个问题进行数据排版, 转化为 TableType: 每一行是一种方法, 每一列是一个指标.
* `tabulate_multiple_problems`, 针对多个问题进行数据排版, 转化为 TableType: 每一行是一个问题, 每一列是 '某方法+某指标'.
* `tabluate`, 将转化好的 TableType 输出为 csv 格式文件
* `scatter`, 绘制散点图 (解集二维目标值), 给定文件名则存储, 否则展示
* `scatter2`, 绘制两个系列的散点图 (解集二维目标值), 给定文件名则存储, 否则展示
* `scatter_n`, 绘制多个系列的散点图 (解集二维目标值), 给定文件名则存储, 否则展示
* `project`, 投影, 将目标维度高于二维的解集转化为二维目标值 (根据给定 x 和 y 的索引)

## Songhua 工程细节

项目管理遵循 maven, 项目文件在 `songhua/pom.xml`. `songhua/lib` 中是 Java 版的 Cplex 接口 `cplex.jar`. 源码在 `songhua/src`.

解 `CBSolution` 继承自 JMetal 的 `BinarySolution`, 添加了约束处理功能; `ConfigLoader` 用于加载配置文件, `Problem` 用于加载问题文件;

以下文件均处于 `songhua/src/main/java/org/osino`.

`Constraints/` 包含了多种约束类型, 它们均继承于基类 `MetaConstraint`; 此外 `Constraints` 用于管理多约束. `Algorithms/` 包含两种自定义算法 `ILP` 即 Cplex 精确求解器, `SeededNSGAII` 是给种子的 NSGA-II 算法 (和本实验不相关, 不加以赘述, 详情可参考源码). `Results/` 包含 `Result` 和 `Results` 分别对结果和多次结果进行管理.

如果需要自己实现某一算法, 那么请参考 `SeededNSGAII` 的仿写:

```Java
// SeededNSGAII 拓展自 NSGAII, 解类型为 BinarySolution
// 我的 CBSolution 继承自 BinarySolution, 所以是合法使用的
public class SeededNSGAII extends NSGAII<BinarySolution>{
    // 一定要有的 serialVersionUID = 1L
    private static final long serialVersionUID = 1L;
    // 自定义内部类
    // ...略去

    // 构造器, 一定需要 Problem 输入
    public SeededNSGAII(
        Problem problem, int iterations, int populationSize, int maxEvaluations,
        double crossoverProbability, double mutationProbability, ArrayList<String> seeds,
        boolean repair
    ) {
        // 初始化需要父类先初始化
        super(problem, maxEvaluations, populationSize, populationSize, populationSize,
              new SinglePointCrossover(crossoverProbability),
              new BitFlipMutation(mutationProbability),
              new NaryTournamentSelection<BinarySolution>(5, new RankingAndCrowdingDistanceComparator<BinarySolution>()),
              new SequentialSolutionListEvaluator<BinarySolution>()
              );

        // 其他初始化操作
        // ... 略去
    }

    // 遗传算法一定需要的创造初始类, 当然如果不在这里进行额外操作可以不需要重新实现
    @Override protected List<BinarySolution> createInitialPopulation() {
        List<BinarySolution> population = new ArrayList<>(getMaxPopulationSize());
        // ... 略去一些操作
        return population;
    }

    // 其他内部方法
    private void repairEvaluate(BinarySolution solution) {
        // ... 略去无关操作
    }

    // 最重要的是使用问题对解集赋值, 这里一定要 override
    @Override protected List<BinarySolution> evaluatePopulation(List<BinarySolution> population) {
        for (int index = 0; index < population.size(); ++ index) {
            // for each solution
            BinarySolution solution = population.get(index);
            if (this.repair) {
                this.repairEvaluate(solution);
            } else {
                this.myProblem.evaluate(solution);
            }
        }
        return population;
    }
}
```

`Runners` 是算法运行的接口, 它们带有 `main` 函数, 用于接受配置文件, 根据配置文件加载问题, 根据配置文件参数初始化算法, 运行算法, 存储结果的功能. `NSGAII` 是标准的 'NSGA-II' 算法的实现; `SNSGAII` 即 'Seeded NSGAII', `CSNSGAII` 是拓展的增加一个约束 (bi-NRP + constraint) 的`SNSGAII`, 这两个算法与本实验无关.

下面根据 `NSGAII` 将如何根据算法实现它的 Runner:

```Java
public class NSGAII {
    // 提炼核心求解过程, 不一定要单写函数, 这里只是遵循某种自以为好看的格式
    public Results solve(
        Problem problem, int iterations, int populationSize, int maxEvaluations,
        double crossoverProbability, double mutationProbability
        ) {
        Results results = new Results();
        // 多次投影必须并非
        for (int i = 0; i < iterations; ++ i) {
            // 看清, XXBuilder(parameters).[...].build()
            Algorithm<List<BinarySolution>> algorithm = new NSGAIIBuilder<BinarySolution>(
                problem,
                new SinglePointCrossover(crossoverProbability), 
                new BitFlipMutation(mutationProbability),
                populationSize
                )
                .setSelectionOperator(new BinaryTournamentSelection<BinarySolution>())
                .setMaxEvaluations(maxEvaluations)
                .build();
            // clock wall 计时法
            long start = System.nanoTime();
            // 算法执行
            new AlgorithmRunner.Executor(algorithm).execute();
            long end = System.nanoTime();
            double elapsedTime = (end - start) / 1e9;
            // 记录结果, 包括运行时间
            results.put(new Result(elapsedTime, algorithm.getResult()));
        }
        return results;
    }

    // main 方法, 生成 jar 文件的接口, args 是参数列表
    public static void main(String[] args) {
        // 我这里只接受一个参数, 那就是配置文件的路径+名字, 如 `/dump/xxx.json`
        assert (args.length == 1);
        // 利用 ConfigLoader 加载配置文件
        ConfigLoader config = new ConfigLoader(args[0]);
        // 检查参数列表
        assert (config.containsKey("problem"));
        assert (config.containsKey("objectiveOrder"));
        assert (config.containsKey("iterations"));
        assert (config.containsKey("populationSize"));
        assert (config.containsKey("maxEvaluations"));
        assert (config.containsKey("crossoverProbability"));
        assert (config.containsKey("mutationProbability"));
        assert (config.containsKey("resultFolder"));
        assert (config.containsKey("methodName"));
        // 运行算法
        Problem problem = new Problem(config.get("problem"), config.getStringList("objectiveOrder"));
        System.out.println("NSGA-II solving on " + config.get("problem"));
        NSGAII algorithm = new NSGAII();
        // 保存结果
        Results results =
            algorithm.solve(problem, config.getInteger("iterations"),
                            config.getInteger("populationSize"), config.getInteger("maxEvaluations"),
                            config.getDouble("crossoverProbability"), config.getDouble("mutationProbability")
                            );
        Path folder = Paths.get(Paths.get(System.getProperty("user.dir")).toString(), "result");
        folder = Paths.get(folder.toString(), config.get("resultFolder"), config.get("problem"));
        folder = Paths.get(folder.toString(), config.get("methodName"));
        results.dump(folder, config.get("methodName"));
    }
}
```

## 单元测试

Nen 项目测试文件均在 `nen/test` 文件夹下, 由 `unittest` 所支持.

所有文件均通过测试 @ 2022/06/29::01:00, 这些测试文件能够保证基本概念的逻辑大体无虞, 大部分求解流程可以进行. 建议对相应文件进行修改后, 重新进行测试; 以及在创造重要的类或方法时, 也应该编写相应的单元测试文件/方法.

## 注意事项

### 可能的问题

#### 找不到模块 `nen`

请将代码文件置于工程文件 `Nen` 下, 或在 .py 代码文件最上面添加:

```Python
import sys
sys.path.append(PROJECT_PATH)
# PROJECT_PATH is folder/to/Nen, such as 'C:/User/someone/Develop/Nen'
```

注意: windows 文件路径的 '\' 需要改为 '/' 区别于转义符号.

#### .jar 求解器找不到问题文件

请将代码文件置于工程文件 `Nen` 下



