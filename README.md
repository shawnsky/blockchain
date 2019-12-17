# blockchain
参考 naivecoin tutorial: https://lhartikk.github.io/

本项目是 naivecoin 的 python 实现版本，包括区块链的数据结构、“挖矿”、节点同步的功能。

## 环境

- Python >= 3.4
- Flask == 1.1.1

## 介绍

区块链是什么？核心就是一句话，区块链是一个分布式数据库，它维护着一个持续不断增长的、有序的记录列表。

比如比特币是区块链技术的一个比较出名的应用。在数字货币的系统中，分布式数据库里保存的就是一条一条交易转账信息。在本次技术分享中，会用 Python 编程实现一个简单的区块链，包括区块链的数据结构、“挖矿”、节点同步的功能。具体来说，将会解决以下问题：

- 区块以及区块链的数据结构
- 如何创建区块
- 定义区块之间的关系
- 向区块链中添加区块
- 区块链网络中的节点同步
- 一个简单的区块链 HTTP 管理接口

## 区块

在一个系统中如何持续不断的存储数据呢？可能会遇到如下困难

- 怎么让数据逐渐增加
- 怎么对之前的数据进行修改

### 区块的数据结构

主要包括以下核心元素: 

- index 区块的递增编号
- timestamp 时间戳
- data 该区块所保存的数据
- hash 该区块的hash值
- previous_hash 前一个区块的hash值，从⽽将区块串联了起来 

于是我们可以得到如下所示的代码

```python
class Block:
    def __init__(self,index,transactions,timestamp,previous_hash,difficulty=3,nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
```

### 区块的哈希值

我们有一个共识，就是我们不会去修改已经保存了的区块数据。可是仅凭大家的共识没有用，那该怎么去真正的去限制呢？

hash值是最重要的属性之一。hash值是对该块的所有数据进行计算的，也就是这个区块的摘要。这意味着如果块中的任何内容发生变化，原始hash值将不再有效。我们可以通过这个办法来检查区块数据是否被恶意的篡改。

所以，在 `Block` 类中，定义了一个 `compute_hash()` 方法来计算本区块的hash值。

```python
def compute_hash(self):
        block_json = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_json.encode()).hexdigest()
```

## 区块链

区块链保存着一个区块数组，以及定义了操作区块链的一些方法。

```python
class BlockChain:

    def __init__(self):
        self.blocks = []
        self.__create_genesis_block()

    def __create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "cuc0123456789")
        self.blocks.append(genesis_block)

    @property
    def last_block(self):
        return self.blocks[-1]
```

### 创世区块

创世区块就是区块链中的第一个区块，因为每一个区块都需要一个 `previous_hash` 属性，区块链中的第一个区块需要我们用硬编码的方式创建出来，它的 `previous_hash` 可以被随便设置一个字符串

```python
genesis_block = Block(0, [], time.time(), "cuc0123456789")
```

### 添加区块

分布式系统中，大家都可以添加区块，如何防止很多人一起添加造成的混乱呢？我们可以想出一种策略，大家同时去解一道数学难题，谁先解出来，谁就可以添加区块。

解出这道难题又叫做 Proof-of-Work（工作量证明），当你得到了这道难题的答案，大家就都会认可你解题的工作量。这个解题的过程通常被称为 “挖矿”。

一个好的题⽬要让计算机便于理解，运算规则相对简单，运算方式相对公平。于是结合Hash算法的题目被设计了了出来：

**找到一个特定区块，这个区块的Hash需要有特殊的前缀**。 

这个前缀越特殊，难度就越⼤大。于是我们可以定义出题⽬的难度 difficulty 为你所定义的特殊前缀是由几个0组成。例如，如果你只要求找到的区块的Hash前缀是一个0（difficulty=1），那么可能相对简单。但是如果要求找到的区块的Hash的前缀有10个0（difficulty=10），那么就有点难了。

那么有一个问题，怎么去找这个区块呢？

为了找到满足 difficulty 条件的Hash，我们需要对同一个区块计算出不同的Hash，明显这是不可能的。所以我们可以通过在区块中加⼊新的可变参数来实现Hash结果的变化，因为SHA256算法会因为数据的任何微⼩变化扩散为整个hash结果的完全变化。

于是我们添加了一个叫做 Nonce 的参数，并且不断的改变这个参数的值，直到挖到我们想要的Hash结果。于是我们 Block 类的定义变为这样

```python
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, difficulty=3, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = nonce

    def compute_hash(self):
        block_json = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_json.encode()).hexdigest()
```

在 “挖矿” 之前，我们先实例化一个 Block

```python
new_block = Block(index=last_block.index + 1,
                          transactions=[],
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash(),
                          difficulty=self.get_difficulty(self.blocks))
```

然后不断的去改变 `new_block` 的 `nonce` 属性的值，直到计算出了满足条件的hash值，我们定义一个方法来实现这个操作

```python
def do_a_difficult_work(block):
    block.nonce = 0
    computed_hash = block.compute_hash()
    while not computed_hash.startswith('0' * block.difficulty):
        block.nonce += 1
        computed_hash = block.compute_hash()
    return computed_hash
```

### 如何确定难度

虽然我们能够指定问题的难度，但是我们要如何设置难度呢？而且如何才能让网络的节点都认同这个难度呢？

让我们回归到区块链的本身。区块链无非是一个区块的链表，并且每隔一段时间会加入一个新的区块。而我们的题目就是在控制加入区块的难度，也就是加入的时间间隔，于是我们引入一个全局参数：

- `BLOCK_GENERATION_INTERVAL`：定义了多久产生一个区块

但是随着环境的变化，例如有更多的节点加入网络，我们并不能一致维持这个时间，因此我们每隔一段时间需要调整一下难度，于是我们引入第二个全局参数：

- `DIFFICULTY_ADJUSTMENT_INTERVAL`：定义了每隔多久调整一次难度

在我们的代码中，我们会设置间隔为10秒。

我们会根据预期和现实之间的差异决定如何调整难度。具体来说，判断差异是否到了2倍的范围，然后对difficulty进行`+1`或者`-1`的操作

```python
    def get_difficulty(self, blocks):
        last_block = self.last_block
        if last_block.index % self.DIFFICULTY_ADJUST_INTERVAL == 0 and last_block.index != 0:
            return self.get_adjusted_difficulty(last_block, blocks)
        else:
            return last_block.difficulty

    def get_adjusted_difficulty(self, last_block, blocks):
        previous_adjusted_block = blocks[len(blocks) - self.DIFFICULTY_ADJUST_INTERVAL]
        time_expected = self.BLOCK_GEN_INTERVAL * self.DIFFICULTY_ADJUST_INTERVAL
        time_taken = last_block.timestamp - previous_adjusted_block.timestamp

        if time_taken < (time_expected / 2):
            return previous_adjusted_block.difficulty + 1
        elif time_taken > (time_expected * 2):
            return previous_adjusted_block.difficulty - 1
        else:
            return previous_adjusted_block.difficulty
```

### 超长链攻击

存在一种情况，假如我们的数学难题被多个人同时解出来怎么办？这完全有可能，毕竟网络中的节点非常多。但是很少会有连续被多人同时解出来的情况，所以，在区块链中，对于这种“分叉”的情况，我们一般会选择最长的那一条链。

因此就会有恶意的攻击者通过自行设置低难度产生超长链，使网络中的节点信任他的恶意的超长链。面对这样的问题该如何解决呢？

我们可以实现一个难度评估函数，综合考虑整个链的实际难度，而不仅仅取决于链的长度。

```python
    def eval_real_difficulty(blocks):
        tot = 0
        for block in blocks:
            tot += math.pow(2, block.difficulty)
        return tot
```

## 节点通讯

因为在整个网络中有很多节点，大家都有可能去创建区块，这就需要大家通过协商通讯的方式达成共识，这需要以下三个基本能力：

- 某节点创建了一个区块，需要通知整个网络中的每个节点
- 新节点加入网络
- 节点收到消息后，可以验证链的合法性，更新自己的链

### 验证区块链是否合法

如果其他人给了我们一个区块链，我们如何验证这个链是正确的呢？这需要符合以下的基本要求：

- 区块之间的索引是+1递增的
- 每个区块的previous_hash需要和之前区块的Hash相同
- 每个区块自身的Hash需要正确，而且是一个正确的工作量证明

```python
    def is_valid_new_block(new_block, previous_block):
        # 检查索引是否正确
        if previous_block.index + 1 != new_block.index:
            print("Wrong index: " + str(new_block.index))
            return False
        # 检查hash是否正常连接
        elif previous_block.compute_hash() != new_block.previous_hash:
            print("Wrong previous hash: " + new_block.previous_hash)
            return False
        # 检查hash是否是一个正确的proof
        elif not new_block.compute_hash().startswith('0' * new_block.difficulty):
            print("Not a proof: " + new_block.compute_hash())
            return False
        return True

    def is_valid_chain(self, blocks):
        # skip genesis block
        for i in range(1, len(blocks)):
            if not self.is_valid_new_block(blocks[i], blocks[i - 1]):
                return False
        return True
```

### 更新本地的链

如果其他人给我们的区块链是合法的，而且比本地的链要新（实际难度更大），那么就用这个新链替换本地的链。

```python
def replace_chain(self, blocks):
    if self.is_valid_chain(blocks) and self.eval_real_difficulty(self.blocks) < self.eval_real_difficulty(blocks):
        self.blocks = blocks
        return True
    return False
```

### 为区块链创建控制接口

使用 HTTP API 的方式实现对区块链的管理，需要实现如下接口

- 查看本地区块链
- 添加区块
- 替换本地区块链
- 查看节点列表
- 注册节点

使用 Flask 微框架来快速实现这个功能，使用 `@app.route()` 装饰器快速创建 HTTP 控制器

如下代码，实现了操作本地区块链对象的 HTTP 接口

```python
@app.route('/chain', methods=['GET', 'POST'])
def chain_handler():
    if request.method == 'GET':
        return Response(__block_list_to_json(local_chain.blocks), mimetype='application/json')

    if request.method == 'POST':
        blocks_in_json = request.form['chain']
        blocks = json.loads(blocks_in_json, object_hook=Block.dict2block)
        print("Recv blocks: " + str(len(blocks)))
        # todo: check chain and replace local chain
        if local_chain.replace_chain(blocks):
            print("local chain replaced")
        return "OK"
```

### 网络节点

节点列表是通过 Python 的集合来维护的，节点在刚启动的时候，只有一个节点，也就是本身。如果想要加入到网络中，就需要先联络网络中的其中一个节点。

```python
@app.route('/peer', methods=['GET', 'POST'])
def peer_handler():
    if request.method == 'GET':
        dict_list = []
        for peer in peers:
            dict_list.append(peer)
        return Response(json.dumps(dict_list), mimetype='application/json')

    if request.method == 'POST':
        url = request.form['url']
        # todo: validate the url
        print("Recv url: " + url)
        peers.add(url)
        return 'OK'
```

### 消息广播

有两个场景需要消息广播

- 发现了新的区块
- 有新的节点加入网络

当新的节点加入到本地的 `peers` 集合内之后，需要对集合内所有节点发送一个 POST 请求来注册新节点

```python
def sync_peers():
    # post net node to each peer
    for peer in peers:
        if peer == local_server:
            continue
        for url in peers:
            r = requests.post('http://' + peer + '/peer',
                              data={'url': url})
    print("peers sync OK")
```

当我们发现了新的区块，就需要通知区块链网络中的每个节点，可以通过遍历 `peers` 集合，构造 POST 请求并发送区块链。对方收到区块链后，会去验证区块链的有效性并更新它本地的链

```python
def broadcast(blocks):
    for peer in peers:
        if peer == local_server:
            continue
        chain_json = __block_list_to_json(blocks)
        r = requests.post('http://' + peer + '/chain',
                          data={'chain': chain_json})
    print("local chan broadcast OK")
```











