import requests
import networkx

block_explorer_url = "https://blockexplorer.com/api/addrs/"


def get_all_transactions(bitcoin_address):
    transactions = []
    from_number = 0
    to_number = 50

    block_explorer_url_full = block_explorer_url + bitcoin_address + "/txs?from=%d&to=%d" % (from_number, to_number)

    response = requests.get(block_explorer_url_full)

    try:
        results = response.json()
    except:
        print("[!] Error retrieving bitcoin transactions. Please re-run this script.")
        return transactions

    if results['totalItems'] == 0:
        print("[*] No transactions for %s" % bitcoin_address)
        return transactions

    transactions.extend(results['items'])

    while len(transactions) < results['totalItems']:
        from_number += 50
        to_number += 50

        block_explorer_url_full = block_explorer_url + bitcoin_address + "/txs?from=%d&to=%d" % (from_number, to_number)

        response = requests.get(block_explorer_url_full)

        results = response.json()

        transactions.extend(results['items'])

    print("[*] Retrieved %d bitcoin transactions." % len(transactions))

    return transactions


def get_unique_bitcoin_addresses(transaction_list):
    bitcoin_addresses = []

    for transaction in transaction_list:

        # check the sending address
        if transaction['vin'][0]['addr'] not in bitcoin_addresses:
            bitcoin_addresses.append(transaction['vin'][0]['addr'])

        # walk through all recipients and check each address
        for receiving_side in transaction['vout']:

            if "addresses" in receiving_side['scriptPubKey']:

                for address in receiving_side['scriptPubKey']['addresses']:

                    if address not in bitcoin_addresses:
                        bitcoin_addresses.append(address)

    print("[*] Identified %d unique bitcoin addresses." % len(bitcoin_addresses))

    return bitcoin_addresses


def build_graph(source_bitcoin_address, transaction_list):
    graph = networkx.DiGraph()

    # graph the transactions by address
    for transaction in transaction_list:

        # check the sending address
        sender = transaction['vin'][0]['addr']
        value = transaction['vin'][0]['value']
        if sender == source_bitcoin_address:
            graph.add_node(sender, attr_dict={"type": "Target Bitcoin Wallet"})
        else:
            graph.add_node(sender, attr_dict={"type": "Bitcoin Wallet"})

        # walk through all recipients and check each address
        for receiving_side in transaction['vout']:

            if "addresses" in receiving_side['scriptPubKey']:
                for address in receiving_side['scriptPubKey']['addresses']:

                    if address == source_bitcoin_address:
                        graph.add_node(address, attr_dict={"type": "Target Bitcoin Address"})
                    else:
                        graph.add_node(address, attr_dict={"type": "Bitcoin Address"})

                    graph.add_edge(sender, address, weight=value)

        # write out the graph
    networkx.write_gexf(graph, "bitcoingraph.gexf")

    return

t = get_all_transactions('13swCVuXeZhWkmwEXod83Mv2YWKVqYeMVS')
print(t)
ba = get_unique_bitcoin_addresses(t)
print(ba)
build_graph(ba, t)