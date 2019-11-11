import json
from blockchain import BlockChain
from block import Block
from flask import Flask, request, Response
import requests
from utils import RSA

# RSA工具
rsa_tool = RSA()
rsa_tool.create_keys()
# 节点集合
peers = set()
# 区块链对象，保存着所有区块
local_chain = BlockChain()


# 消息广播
def broadcast(blocks):
    for peer in peers:
        if peer == local_server:
            continue
        chain_json = __block_list_to_json(blocks)
        r = requests.post('http://' + peer + '/chain',
                          data={'chain': chain_json})
    print("local chan broadcast OK")
    sync_peers()


# 网络节点同步，把本地节点集合广播给所有节点
def sync_peers():
    # post net node to each peer
    for peer in peers:
        if peer == local_server:
            continue
        for url in peers:
            r = requests.post('http://' + peer + '/peer',
                              data={'url': url})
    print("peers sync OK")


def __block_list_to_json(blocks):
    dict_list = []
    for block in blocks:
        dict_list.append(block.__dict__)
    return json.dumps(dict_list)


host = input("host: ")
port = input("port: ")
local_server = host + ':' + str(port)
peers.add(local_server)


app = Flask(__name__)


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


@app.route('/mine', methods=['GET'])
def mine_handler():
    transaction = 'Blank'
    text = request.args.get('text')
    if text:
        transaction = text
    transaction += ' '
    signature = rsa_tool.encrypt(transaction)
    transaction += signature.decode("utf-8","ignore")
    transaction += ' ' + rsa_tool.get_pk()

    block = local_chain.find_block(transaction)
    broadcast(local_chain.blocks)
    return 'OK'


@app.route('/broadcast', methods=['GET'])
def broadcast_handler():
    broadcast(local_chain.blocks)
    return 'OK'


app.run(debug=False, host=host, port=port)
