from electroncash.bitcoin import regenerate_key, MySigningKey, Hash
from electroncash.address import Address, OpCodes as Op
import ecdsa
from math import ceil

import time
LOCKTIME_THRESHOLD = 500000000
UTXO=0
CONTRACT=1
MODE=2
PLEDGE_TIME=int((0*3600*24))#0.083
PLEDGE = 1000


def joinbytes(iterable):
    """Joins an iterable of bytes and/or integers into a single byte string"""
    return b''.join((bytes((x,)) if isinstance(x,int) else x) for x in iterable)


class MecenasContract:
    """Contract of Mecenas"""

    def __init__(self, addresses, initial_tx=None,v=0, data=None):
        self.version = v
        self.initial_tx = initial_tx
        self.addresses = addresses
        try:
            self.i_time = data[0]
            self.rpayment = data[1]

        except:
            print("except")
            self.rpayment = PLEDGE
            self.i_time = PLEDGE_TIME // 512
        self.i_time_bytes = self.i_time.to_bytes(2, 'little')

        self.rpayment_bytes = self.rpayment.to_bytes(ceil(self.rpayment.bit_length() / 8), 'little')

        assert len(self.i_time_bytes) == 2
        assert len(self.rpayment_bytes) < 76 # Better safe than sorry

        ## script version containing p2pkh part in protege challenge, future version 2 of the script?
        # self.redeemscript = joinbytes([
        #     len(addresses[0].hash160), addresses[0].hash160,
        #     len(addresses[1].hash160), addresses[1].hash160,
        #     len(self.rpayment_bytes), self.rpayment_bytes,
        #     Op.OP_3, Op.OP_PICK, Op.OP_TRUE, Op.OP_EQUAL,
        #     Op.OP_IF,
        #         Op.OP_10, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, Op.OP_4, Op.OP_EQUALVERIFY, Op.OP_9, Op.OP_PICK, Op.OP_SIZE,
        #         Op.OP_NIP, 1, 100, Op.OP_EQUALVERIFY, Op.OP_7, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, Op.OP_8,
        #         Op.OP_EQUALVERIFY, Op.OP_6, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, Op.OP_4, Op.OP_EQUALVERIFY, Op.OP_5,
        #         Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, 1, 32, Op.OP_EQUALVERIFY, Op.OP_4, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP,
        #         Op.OP_8, Op.OP_EQUALVERIFY, Op.OP_12, Op.OP_PICK, Op.OP_HASH160, Op.OP_3, Op.OP_PICK, Op.OP_EQUALVERIFY,
        #         Op.OP_11, Op.OP_PICK, Op.OP_13, Op.OP_PICK, Op.OP_CHECKSIGVERIFY, Op.OP_10, Op.OP_PICK, Op.OP_10,
        #         Op.OP_PICK, Op.OP_CAT, Op.OP_9, Op.OP_PICK, Op.OP_CAT, Op.OP_8, Op.OP_PICK, Op.OP_CAT, Op.OP_7, Op.OP_PICK,
        #         Op.OP_CAT, Op.OP_6, Op.OP_PICK, Op.OP_CAT, Op.OP_5, Op.OP_PICK, Op.OP_CAT, Op.OP_12, Op.OP_PICK, Op.OP_SIZE,
        #         Op.OP_1SUB, Op.OP_SPLIT, Op.OP_DROP, Op.OP_OVER, Op.OP_SHA256, Op.OP_15, Op.OP_PICK,
        #         Op.OP_CHECKDATASIGVERIFY, 2, 232, 3, Op.OP_2, Op.OP_PICK, Op.OP_8, Op.OP_NUM2BIN, Op.OP_10, Op.OP_PICK,
        #         Op.OP_BIN2NUM, Op.OP_4, Op.OP_PICK, Op.OP_SUB, Op.OP_2, Op.OP_PICK, Op.OP_SUB, Op.OP_8, Op.OP_NUM2BIN, 1,
        #         118, 1, 135, 1, 169, 1, 20, 1, 23, 1, 25, 1, 136, 1, 172, 1, 20, Op.OP_PICK, Op.OP_3, Op.OP_SPLIT,
        #         Op.OP_NIP, 3, self.i_time_bytes, 64, Op.OP_CHECKSEQUENCEVERIFY, Op.OP_DROP, 1, 23, Op.OP_PICK, Op.OP_BIN2NUM, Op.OP_2,
        #         Op.OP_GREATERTHANOREQUAL, Op.OP_VERIFY, Op.OP_9, Op.OP_PICK, Op.OP_5, Op.OP_PICK, Op.OP_CAT, Op.OP_7,
        #         Op.OP_PICK, Op.OP_CAT, Op.OP_6, Op.OP_PICK, Op.OP_CAT, Op.OP_OVER, Op.OP_HASH160, Op.OP_CAT, Op.OP_8,
        #         Op.OP_PICK, Op.OP_CAT, Op.OP_11, Op.OP_PICK, Op.OP_5, Op.OP_PICK, Op.OP_CAT, Op.OP_10, Op.OP_PICK,
        #         Op.OP_CAT, Op.OP_8, Op.OP_PICK, Op.OP_CAT, Op.OP_7, Op.OP_PICK, Op.OP_CAT, 1, 17, Op.OP_PICK, Op.OP_CAT,
        #         Op.OP_4, Op.OP_PICK, Op.OP_CAT, Op.OP_3, Op.OP_PICK, Op.OP_CAT, Op.OP_2DUP, Op.OP_CAT, Op.OP_HASH256, 1, 21,
        #         Op.OP_PICK, Op.OP_EQUAL, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
        #         Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
        #         Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
        #         Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
        #     Op.OP_ELSE,
        #         Op.OP_3, Op.OP_PICK, Op.OP_2, Op.OP_EQUAL,
        #         Op.OP_IF,
        #             Op.OP_5, Op.OP_PICK, Op.OP_HASH160, Op.OP_2, Op.OP_PICK, Op.OP_EQUALVERIFY, Op.OP_4, Op.OP_PICK, Op.OP_6,
        #             Op.OP_PICK, Op.OP_CHECKSIG, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
        #         Op.OP_ELSE,
        #             Op.OP_FALSE,
        #         Op.OP_ENDIF,
        #     Op.OP_ENDIF
        #
        # ])
        ## script version without p2pkh part in protege challenge, version 1 of the script?
        self.redeemscript = joinbytes([
            len(addresses[0].hash160), addresses[0].hash160,
            len(addresses[1].hash160), addresses[1].hash160,
            len(self.rpayment_bytes), self.rpayment_bytes,
            Op.OP_3, Op.OP_PICK, Op.OP_TRUE, Op.OP_EQUAL,
            Op.OP_IF,
                Op.OP_10, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, Op.OP_4, Op.OP_EQUALVERIFY, Op.OP_9, Op.OP_PICK, Op.OP_SIZE,
                Op.OP_NIP, 1, 100, Op.OP_EQUALVERIFY, Op.OP_7, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, Op.OP_8,
                Op.OP_EQUALVERIFY, Op.OP_6, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, Op.OP_4, Op.OP_EQUALVERIFY, Op.OP_5,
                Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP, 1, 32, Op.OP_EQUALVERIFY, Op.OP_4, Op.OP_PICK, Op.OP_SIZE, Op.OP_NIP,
                Op.OP_8, Op.OP_EQUALVERIFY, Op.OP_11, Op.OP_PICK, Op.OP_13, Op.OP_PICK, Op.OP_CHECKSIGVERIFY, Op.OP_10,
                Op.OP_PICK, Op.OP_10, Op.OP_PICK, Op.OP_CAT, Op.OP_9, Op.OP_PICK, Op.OP_CAT, Op.OP_8, Op.OP_PICK, Op.OP_CAT,
                Op.OP_7, Op.OP_PICK, Op.OP_CAT, Op.OP_6, Op.OP_PICK, Op.OP_CAT, Op.OP_5, Op.OP_PICK, Op.OP_CAT, Op.OP_12,
                Op.OP_PICK, Op.OP_SIZE, Op.OP_1SUB, Op.OP_SPLIT, Op.OP_DROP, Op.OP_OVER, Op.OP_SHA256, Op.OP_15, Op.OP_PICK,
                Op.OP_CHECKDATASIGVERIFY, 2, 232, 3, Op.OP_2, Op.OP_PICK, Op.OP_8, Op.OP_NUM2BIN, Op.OP_10, Op.OP_PICK,
                Op.OP_BIN2NUM, Op.OP_4, Op.OP_PICK, Op.OP_SUB, Op.OP_2, Op.OP_PICK, Op.OP_SUB, Op.OP_8, Op.OP_NUM2BIN, 1,
                118, 1, 135, 1, 169, 1, 20, 1, 23, 1, 25, 1, 136, 1, 172, 1, 20, Op.OP_PICK, Op.OP_3, Op.OP_SPLIT,
                Op.OP_NIP, 3, self.i_time_bytes, 64, Op.OP_CHECKSEQUENCEVERIFY, Op.OP_DROP, 1, 23, Op.OP_PICK, Op.OP_BIN2NUM, Op.OP_2,
                Op.OP_GREATERTHANOREQUAL, Op.OP_VERIFY, Op.OP_9, Op.OP_PICK, Op.OP_5, Op.OP_PICK, Op.OP_CAT, Op.OP_7,
                Op.OP_PICK, Op.OP_CAT, Op.OP_6, Op.OP_PICK, Op.OP_CAT, Op.OP_OVER, Op.OP_HASH160, Op.OP_CAT, Op.OP_8,
                Op.OP_PICK, Op.OP_CAT, Op.OP_11, Op.OP_PICK, Op.OP_5, Op.OP_PICK, Op.OP_CAT, Op.OP_10, Op.OP_PICK,
                Op.OP_CAT, Op.OP_8, Op.OP_PICK, Op.OP_CAT, Op.OP_7, Op.OP_PICK, Op.OP_CAT, 1, 17, Op.OP_PICK, Op.OP_CAT,
                Op.OP_4, Op.OP_PICK, Op.OP_CAT, Op.OP_3, Op.OP_PICK, Op.OP_CAT, Op.OP_2DUP, Op.OP_CAT, Op.OP_HASH256, 1, 21,
                Op.OP_PICK, Op.OP_EQUAL, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
                Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
                Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
                Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
            Op.OP_ELSE,
                Op.OP_3, Op.OP_PICK, Op.OP_2, Op.OP_EQUAL,
                Op.OP_IF,
                    Op.OP_5, Op.OP_PICK, Op.OP_HASH160, Op.OP_2, Op.OP_PICK, Op.OP_EQUALVERIFY, Op.OP_4, Op.OP_PICK, Op.OP_6,
                    Op.OP_PICK, Op.OP_CHECKSIG, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP, Op.OP_NIP,
                Op.OP_ELSE,
                    Op.OP_FALSE,
                Op.OP_ENDIF,
            Op.OP_ENDIF

        ])

        self.address = Address.from_multisig_script(self.redeemscript)

        data1 = self.address.to_ui_string() + ' ' + str(self.version)
        data2 = str(self.i_time) + ' ' + str(self.rpayment)
        self.op_return = joinbytes(
            [Op.OP_RETURN, 4, b'>sh\x00', len(data1), data1.encode('utf8'), len(data2), data2.encode('utf8')])

        #assert 76 < len(self.redeemscript) <= 255  # simplify push in scriptsig; note len is around 200.


class ContractManager:
    """A device that spends from a Mecenas Contract in two different ways."""
    def __init__(self, contracts, keypairs, public_keys, wallet):
        self.contracts = contracts
        self.contract_index=0
        self.chosen_utxo = 0
        self.tx = contracts[self.contract_index][UTXO][self.chosen_utxo]
        self.contract = contracts[self.contract_index][CONTRACT]
        self.mode = contracts[self.contract_index][MODE][0]
        self.keypair = keypairs
        self.pubkeys = public_keys
        self.wallet = wallet
        self.rpayment = self.contract.rpayment
        self.dummy_scriptsig = '00'*(110 + len(self.contract.redeemscript))
        if self.mode == 0:
            self.sequence=2**22+self.contract.i_time
        else:
            self.sequence = 0
        self.value = int(self.tx.get('value'))
        self.txin = dict()

    def choice(self, contract, utxo_index, m):
        self.value=0
        self.txin=[]
        self.chosen_utxo=utxo_index
        self.contract = contract[CONTRACT]
        self.contract_index = self.contracts.index(contract)
        self.rpayment = contract[CONTRACT].rpayment
        self.mode = m
        if self.mode == 0:
            self.sequence=2**22+self.contract.i_time
        else:
            self.sequence = 0
        print([self.pubkeys[self.contract_index][self.mode]])
        utxo = contract[UTXO][utxo_index]
        if (utxo_index == -1) and (self.mode != 0):
            for u in contract[UTXO]:
                self.value += int(u.get('value'))
                self.txin.append( dict(
                    prevout_hash=u.get('tx_hash'),
                    prevout_n=int(u.get('tx_pos')),
                    sequence=self.sequence,
                    scriptSig=self.dummy_scriptsig,
                    type='unknown',
                    address=self.contract.address,
                    scriptCode=self.contract.redeemscript.hex(),
                    num_sig=1,
                    signatures=[None],
                    x_pubkeys=[self.pubkeys[self.contract_index][self.mode]],
                    value=int(u.get('value')),
                ))
        else:
            self.value = int(utxo.get('value'))
            self.txin = [dict(
                prevout_hash=utxo.get('tx_hash'),
                prevout_n=int(utxo.get('tx_pos')),
                sequence=self.sequence,
                scriptSig=self.dummy_scriptsig,
                type='unknown',
                address=self.contract.address,
                scriptCode=self.contract.redeemscript.hex(),
                num_sig=1,
                signatures=[None],
                x_pubkeys=[self.pubkeys[self.contract_index][self.mode]],
                value=int(utxo.get('value')),
            )]


    def signtx(self, tx):
        """generic tx signer for compressed pubkey"""
        tx.sign(self.keypair)


    def completetx(self, tx):
        """
        Completes transaction by creating scriptSig. You need to sign the
        transaction before using this (see `signtx`).
        This works on multiple utxos if needed.
        """
        pub = bytes.fromhex(self.pubkeys[self.contract_index][self.mode])
        for txin in tx.inputs():
            # find matching inputs
            if txin['address'] != self.contract.address:
                continue
            sig = txin['signatures'][0]
            if not sig:
                continue
            sig = bytes.fromhex(sig)
            if txin['scriptSig'] == self.dummy_scriptsig:
                script = [
                    len(pub), pub,
                    len(sig), sig,
                    Op.OP_2, 77, len(self.contract.redeemscript).to_bytes(2, 'little'), self.contract.redeemscript,
                    ]
                print("scriptSig length " + str(joinbytes(script).hex().__sizeof__()))
                txin['scriptSig'] = joinbytes(script).hex()
        # need to update the raw, otherwise weird stuff happens.
        tx.raw = tx.serialize()

    def completetx_ref(self, tx):

        pub = bytes.fromhex(self.pubkeys[self.contract_index][self.mode])

        for i, txin in enumerate(tx.inputs()):
            # find matching inputs
            if txin['address'] != self.contract.address:
                continue
            preimage=bytes.fromhex(tx.serialize_preimage(i))
            sig = txin['signatures'][0]
            if not sig:
                continue
            sig = bytes.fromhex(sig)
            print("Signature size:" + str(len(sig)))
            if txin['scriptSig'] == self.dummy_scriptsig:
                self.checkd_data_sig(sig, preimage, self.pubkeys[self.contract_index][self.mode])

                ver=preimage[:4]
                hPhSo=preimage[4:104]
                scriptCode=preimage[104:-52]
                value=preimage[-52:-44]
                nSequence=preimage[-44:-40]
                hashOutput=preimage[-40:-8]
                tail=preimage[-8:]


                script = [
                    len(pub), pub,
                    len(sig), sig,
                    len(ver), ver,
                    76, len(hPhSo), hPhSo,
                    77, len(scriptCode).to_bytes(2, 'little'), scriptCode,
                    len(value), value,
                    len(nSequence), nSequence,
                    len(hashOutput), hashOutput,
                    len(tail), tail,
                    Op.OP_1, 77, len(self.contract.redeemscript).to_bytes(2, 'little'), self.contract.redeemscript,
                    ]
                print("scriptSig length "+ str(joinbytes(script).hex().__sizeof__()))
                txin['scriptSig'] = joinbytes(script).hex()
        # need to update the raw, otherwise weird stuff happens.
        tx.raw = tx.serialize()

    def checkd_data_sig(self,sig,pre,pk):
        sec, compressed = self.keypair.get(pk)
        pre_hash = Hash(pre)
        pkey = regenerate_key(sec)
        secexp = pkey.secret
        private_key = MySigningKey.from_secret_exponent(secexp, curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        print("Data signature ok:")
        print(public_key.verify_digest(sig[:-1], pre_hash, sigdecode=ecdsa.util.sigdecode_der))

