OntCversion = '2.0.0'
from ontology.interop.Ontology.Contract import Migrate
from ontology.interop.System.App import DynamicAppCall
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import CheckWitness, Notify, Serialize, Deserialize
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash
from ontology.interop.Ontology.Native import Invoke
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.builtins import concat, state, append
from ontology.libont import AddressFromVmCode

ONTAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')
ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')

Admin = Base58ToAddress("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")
PreSaleReceiver = Base58ToAddress("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")
SelfContractAddress = GetExecutingScriptHash()
# GP means gift package
GP_PREFIX = "GPContent"
GP_LEFT_PREFIX = "GPLeft"
PROPERTY_REVERSED_HASH_KEY = "PropertyHash"
PRESALE_PAUSED_KEY = "Pause"
GP_MAX_PER_TX_KEY = "GPMaxPerTx"

def Main(operation, args):
    ############# Methods for Admin account only defination Starts  ################
    if operation == "setPropertyHash":
        assert (len(args) == 1)
        propertyReversedHash = args[0]
        return setPropertyHash(propertyReversedHash)
    if operation == "setGP":
        assert (len(args) == 4)
        gpId = args[0]
        gpLimit = args[1]
        price = args[2]
        gpContent = args[3]
        return setGP(gpId, gpLimit, price, gpContent)
    if operation == "setGPMaxPerTx":
        assert (len(args) == 1)
        limit = args[0]
        return setGPMaxPerTx(limit)
    if operation == "withdraw":
        return withdraw()
    if operation == "pause":
        return pause()
    if operation == "unpause":
        return unpause()
    if operation == "migrateContract":
        assert (len(args) == 7)
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        return migrateContract(code, needStorage, name, version, author, email, description)
    ############# Methods for Admin account only defination Ends  ################
    #################### Purchase method for player Starts  ######################
    if operation == "purchase":
        assert (len(args) == 3)
        account = args[0]
        gpId = args[1]
        gpAmount = args[2]
        return purchase(account, gpId, gpAmount)
    #################### Purchase method for player Ends  ######################
    #################### Pre-execute methods defination Starts  ######################
    if operation == "getPropertyReversedHash":
        return getPropertyReversedHash()
    if operation == "getGPMaxPerTx":
        return getGPMaxPerTx()
    if operation == "getGP":
        assert (len(args) == 1)
        gpId = args[0]
        return getGP(gpId)
    if operation == "getGPLeft":
        assert (len(args) == 1)
        gpId = args[0]
        return getGPLeft(gpId)
    #################### Pre-execute methods defination Ends  ######################
    return False

############# Methods for Admin account only defination Starts  ################
def setPropertyHash(propertyReversedHash):
    assert (CheckWitness(Admin))
    Put(GetContext(), PROPERTY_REVERSED_HASH_KEY, propertyReversedHash)
    Notify(["setPropertyHash", propertyReversedHash])
    return True


def setGP(gpId, gpLimit, price, gpContent):
    """
    :param gpId: token as the identity of gift package
    :param price: how many ong does this gpId will be sold
    :param gpLimit: how many gift packages (GP) will be available.
    :param gpContent: [[tokenId1, amount1], [tokenId2, amount2], ..., [tokenIdN, amountN]]
    :return:
    """
    assert (CheckWitness(Admin))
    gpKey = _concatkey(GP_PREFIX, gpId)
    assert (not Get(GetContext(), gpKey))
    gpMap = {"price":price}
    assert (gpLimit > 0)
    content = []
    # ta means [tokenId_n, amount_n]
    for ta in gpContent:
        tokenId = ta[0]
        amount = ta[1]
        # make sure the tokenId is legal
        assert (tokenId >= 1001 and tokenId <= 999999)
        # make sure the tokenId has been created in property contract <=> name of tokenId is NOT None
        res = DynamicAppCall(getPropertyReversedHash(), "name", [tokenId])
        assert ( res)
        assert (amount > 0)
        content.append([tokenId, amount])
    contentInfo = Serialize(content)
    gpMap["content"] = contentInfo
    # put the gp info into the storage
    Put(GetContext(), _concatkey(GP_PREFIX, gpId), Serialize(gpMap))
    # update the left gift package number in storage
    Put(GetContext(), _concatkey(GP_LEFT_PREFIX, gpId), gpLimit)
    Notify(["setGP", gpId, gpLimit, price, gpContent])
    return True

def setGPMaxPerTx(limit):
    assert (CheckWitness(Admin))
    assert (limit > 0)
    Put(GetContext(), GP_MAX_PER_TX_KEY, limit)
    Notify(["setMaxGPperTx", limit])
    return True

def withdraw():
    """
    In case someone transfers ong or ont into this contract by accident, Admin can withdraw all the money left in the contract.
    :return:
    """
    assert (CheckWitness(Admin))
    param = state(SelfContractAddress)
    totalOngAmount = Invoke(0, ONGAddress, 'balanceOf', param)
    if totalOngAmount > 0:
        assert (_tranferNativeAsset(ONGAddress, SelfContractAddress, PreSaleReceiver, totalOngAmount))
    totalOntAmount = Invoke(0, ONTAddress, 'balanceOf', param)
    if totalOntAmount > 0:
        assert (_tranferNativeAsset(ONTAddress, SelfContractAddress, PreSaleReceiver, totalOntAmount))
    Notify(["withdraw", PreSaleReceiver, totalOngAmount, totalOntAmount])
    return True

def pause():
    assert (CheckWitness(Admin))
    Put(GetContext(), PRESALE_PAUSED_KEY, "T")
    Notify(["pause"])
    return True

def unpause():
    assert (CheckWitness(Admin))
    Put(GetContext(), PRESALE_PAUSED_KEY, "F")
    Notify(["unpause"])
    return True

def migrateContract(code, needStorage, name, version, author, email, description):
    assert (CheckWitness(Admin))
    assert (_whenNotPaused() == False)
    param = state(SelfContractAddress)
    totalOngAmount = Invoke(0, ONGAddress, 'balanceOf', param)
    totalOntAmount = Invoke(0, ONTAddress, 'balanceOf', param)
    # Option1: TODO
    # newContractHash = AddressFromVmCode(code)
    # res = _tranferNativeAsset(ONGAddress, SelfContractAddress, newContractHash, totalOngAmount)
    # assert (res)

    # Option2: make sure there is no ong left
    assert (totalOngAmount == 0 and totalOntAmount == 0)

    res = Migrate(code, needStorage, name, version, author, email, description)
    assert (res)
    Notify(["migreate"])
    return True
############# Methods for Admin account only defination Ends  ################



#################### Purchase method for player Starts  ######################
def purchase(account, gpId, gpAmount):
    """
    Before purchase, make sure
    1. CEO in Property contract has make the preSaleProperty.py contract as the authorized account
    2. Admin has run setGP() to store the package info within preSaleProperty contract.
    :param account:
    :param gpId:
    :param gpAmount
    :return:
    """
    assert (_whenNotPaused())
    assert (CheckWitness(account))
    gpMaxPerTx = getGPMaxPerTx()
    if not gpMaxPerTx:
        assert (gpAmount > 0)
    else:
        assert (gpAmount > 0 and gpAmount <= gpMaxPerTx)
    # make sure there are enough available gift packages left
    gpLeft = getGPLeft(gpId)
    assert (gpLeft >= gpAmount)
    # get the gift package info
    priceContent = getGP(gpId)
    assert (len(priceContent) == 2)
    price = priceContent[0]
    content = priceContent[1]
    # transfer ONG from account to the contract
    ongToBeTransferred = price * gpAmount
    assert (_tranferNativeAsset(ONGAddress, account, PreSaleReceiver, ongToBeTransferred))
    # mint all the tokens within the gpId gift package.
    argsForMultiMintToken = []
    for ta in content:
        tokenId = ta[0]
        amount = ta[1] * gpAmount
        argsForMultiMintToken.append([account, tokenId, amount])
    assert (DynamicAppCall(getPropertyReversedHash(), "multiMintToken", argsForMultiMintToken))
    Put(GetContext(), _concatkey(GP_LEFT_PREFIX, gpId), gpLeft - gpAmount)
    Notify(["purchase", account, gpId, price, gpAmount])
    return True
#################### Purchase method for player Ends  ######################


#################### Pre-execute methods defination Starts  ######################
def getPropertyReversedHash():
    return Get(GetContext(), PROPERTY_REVERSED_HASH_KEY)

def getGPMaxPerTx():
    return Get(GetContext(), GP_MAX_PER_TX_KEY)

def getGP(gpId):
    gpMapInfo = Get(GetContext(), _concatkey(GP_PREFIX, gpId))
    if not gpMapInfo:
        return []
    gpMap = Deserialize(gpMapInfo)
    price = gpMap["price"]
    contentInfo = gpMap["content"]
    content = Deserialize(contentInfo)
    return [price, content]

def getGPLeft(gpId):
    return Get(GetContext(), _concatkey(GP_LEFT_PREFIX, gpId))
#################### Pre-execute methods defination Ends  ######################


#################### Private methods defination starts ######################
def _whenNotPaused():
    isPaused = Get(GetContext(), PRESALE_PAUSED_KEY)
    if isPaused == "T":
        return False
    elif isPaused == "F":
        return True


def _tranferNativeAsset(_nativeAssetAddress, _from, _to, _amount):
    param = state(_from, _to, _amount)
    res = Invoke(0, _nativeAssetAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False


def _concatkey(str1, str2):
    return concat(concat(str1, '_'), str2)
#################### Private methods defination Ends ######################
