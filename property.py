OntCversion = '2.0.0'
"""
This is the property smart contract of OEP-8 type
"""
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import CheckWitness, Notify, Deserialize, Serialize
from ontology.interop.System.Action import RegisterAction

from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.builtins import concat, len, append


############### RequireWitness (safetycheck) Defination Starts #################
def Revert():
    raise Exception(0xF1F1F2F2F3F3F4F4)

def Require(condition):
    if not condition:
        Revert()
    return True

def RequireWitness(witness):
    """
    Checks the tx sender is equal to the witness. If not
    satisfying, revert the transaction.
    """
    Require(CheckWitness(witness))
    return True
############### RequireWitness (safetycheck) Defination Ends ###################

########################### SafeMath Defination Starts ##########################
"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeMath.py
"""
def Add(a, b):
    """
	Adds two numbers, throws on overflow.
	"""
    c = a + b
    Require(c >= a)
    return c

def Sub(a, b):
    """
    Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a>=b)
    return a-b

########################### SafeMath Defination Ends ###########################


TransferEvent = RegisterAction("transfer", "fromAcct", "toAcct", "tokenId", "amount")
ApprovalEvent = RegisterAction("approval", "owner", "spender", "tokenId", "amount")

# modify to the admin address
CEO_ADDRESS_KEY = "CEO"
CTO_ADDRESS_KEY = "CTO"
COO_ADDRESS_KEY = "COO"
AUTHORIZED_LEVEL_PREFIX = "AuthorizedLevel"
CEOAddress = Base58ToAddress('ceoxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

CONTRACT_PAUSED_KEY = "Pause"
# NAME_PREFIX + tokenId --- to store the name of the tokenId token
NAME_PREFIX = 'Name'
# SYMBOL_PREFIX + tokenId --- to store the symbol of the tokenId token
SYMBOL_PREFIX = 'Symbol'
#  BALANCE_PREFIX + tokenId + address --- to store the balance of address in terms of the TOKEN_ID token
BALANCE_PREFIX = 'Balance'
# APPROVE_PREFIX + tokenId + owner + spender -- to store the approved TOKEN_ID amount to the spender by the owner
APPROVE_PREFIX = 'Approve'
# TOTAL_SUPPLY + tokenId  --- to store the total supply of the TOKEN_ID token
TOTAL_SUPPLY_PREFIX = 'TotalSupply'


def Main(operation, args):
    ########################## Methods that meet the OEP8 protocal Starts ############################
    if operation == "name":
        if len(args) != 1:
            return False
        tokenId = args[0]
        return name(tokenId)
    if operation == "symbol":
        if len(args) != 1:
            return False
        tokenId = args[0]
        return symbol(tokenId)
    if operation == "totalSupply":
        if len(args) != 1:
            return False
        tokenId = args[0]
        return totalSupply(tokenId)
    if operation == "balanceOf":
        if len(args) != 2:
            return False
        acct = args[0]
        tokenId = args[1]
        return balanceOf(acct, tokenId)
    if operation == "transfer":
        if len(args) != 4:
            return False
        fromAcct = args[0]
        toAcct = args[1]
        tokenId = args[2]
        amount = args[3]
        return transfer(fromAcct, toAcct, tokenId, amount)
    if operation == "transferMulti":
        return transferMulti(args)
    if operation == "approve":
        if len(args) != 4:
            return False
        owner = args[0]
        spender = args[1]
        tokenId = args[2]
        amount = args[3]
        return approve(owner, spender, tokenId, amount)
    if operation == "approveMulti":
        return approveMulti(args)
    if operation == "allowance":
        if len(args) != 3:
            return False
        owner = args[0]
        spender = args[1]
        tokenId = args[2]
        return allowance(owner, spender, tokenId)
    if operation == "transferFrom":
        if len(args) != 5:
            return False
        spender = args[0]
        fromAcct = args[1]
        toAcct = args[2]
        tokenId = args[3]
        amount = args[4]
        return transferFrom(spender, fromAcct, toAcct, tokenId, amount)
    if operation == "transferFromMulti":
        return transferFromMulti(args)
    ########################## Methods that meet the OEP8 protocal Ends ############################
    #################### Special methods for CEO only defination starts  ######################
    if operation == "setCLevel":
        if len(args) != 2:
            return False
        option = args[0]
        account = args[1]
        return setCLevel(option, account)
    if operation == "setAuthorizedLevel":
        if len(args) != 1:
            return False
        account = args[0]
        return setAuthorizedLevel(account)
    if operation == "removeAuthorizedLevel":
        if len(args) != 1:
            return False
        account = args[0]
        return removeAuthorizedLevel(account)
    if operation == "createToken":
        if len(args) != 3:
            return False
        tokenId = args[0]
        name = args[1]
        symbol = args[2]
        return createToken(tokenId, name, symbol)
    if operation == "multiCreateToken":
        return multiCreateToken(args)
    #################### Special methods for CEO only defination Ends  ######################
    ############# Special methods for C Level accounts only defination Starts  ################
    if operation == "pause":
        return pause()
    if operation == "unpause":
        return unpause()
    ############# Special methods for C Level accounts only defination Ends  ################
    ############# Special methods for C Level and authorized level defination Starts  ################
    if operation == "mintToken":
        if len(args) != 4:
            return False
        mintAcct = args[0]
        toAcct = args[1]
        tokenId = args[2]
        amount = args[3]
        return mintToken(mintAcct, toAcct, tokenId, amount)
    if operation == "multiMintToken":
        return multiMintToken(args)
    if operation == "burnToken":
        if len(args) != 3:
            return False
        account = args[0]
        tokenId = args[1]
        amount = args[2]
        return burnToken(account, tokenId, amount)
    if operation == "multiBurnToken":
        return multiBurnToken(args)
    ############# Special methods for C Level and authorized level defination Ends  ################
    #################### Optional methods defination starts  ######################
    if operation == "getCTO":
        return getCTO()
    if operation == "getCOO":
        return getCOO()
    if operation == "isAuthorizedLevel":
        Require(len(args) == 1)
        account = args[0]
        return isAuthorizedLevel(account)
    #################### Optional methods defination Ends ######################
    return False

########################## Methods that meet the OEP8 protocal Starts ############################
def name(tokenId):
    """
    :param tokenId: helps to format name key = NAME_PREFIX + tokenId
    :return: name of the token with tokenId
    """
    return Get(GetContext(), _concatkey(NAME_PREFIX, tokenId))


def symbol(tokenId):
    """
    :param tokenId: helps to format symbol key = SYMBOL_PREFIX + tokenId
    :return: symbol of token with tokenId
    """
    return Get(GetContext(), _concatkey(SYMBOL_PREFIX, tokenId))


def totalSupply(tokenId):
    """
    :param tokenId:  helps to format totalSupply key = TOTAL_SUPPLY + tokenId
    :return: total supply of token with tokenId
    """
    return Get(GetContext(), _concatkey(TOTAL_SUPPLY_PREFIX, tokenId))


def balanceOf(acct, tokenId):
    """
    get balance of account in terms of token with the tokenId
    :param acct: used to check the acct balance
    :param tokenId: the tokenId determines which token balance of acct needs to be checked
    :return: the balance of acct in terms of tokenId tokens
    """
    return Get(GetContext(), _concatkey(_concatkey(BALANCE_PREFIX, tokenId), acct))

def transfer(fromAcct, toAcct, tokenId, amount):
    """
    transfer amount of tokens in terms of tokenId token from fromAcct to the toAcct
    :param fromAcct:
    :param toAcct:
    :param tokenId:
    :param amount:
    :return:
    """
    Require(_whenNotPaused())
    RequireWitness(fromAcct)
    Require(_tokenExist(tokenId))
    Require(len(fromAcct) == 20)
    Require(len(toAcct) == 20)

    balanceKey = _concatkey(BALANCE_PREFIX, tokenId)
    fromKey = _concatkey(balanceKey, fromAcct)
    fromBalance = Get(GetContext(), fromKey)

    if amount > fromBalance or amount <= 0:
        return False

    # assert (amount <= fromBalance and amount > 0)

    if amount == fromBalance:
        Delete(GetContext(), fromKey)
    else:
        Put(GetContext(), fromKey, Sub(fromBalance, amount))

    toKey = _concatkey(balanceKey, toAcct)
    toBalance = Get(GetContext(), toKey)
    Put(GetContext(), toKey, Add(toBalance, amount))

    TransferEvent(fromAcct, toAcct, tokenId, amount)

    return True


def transferMulti(args):
    """
    multi transfer
    :param args:[[fromAccount1, toAccount1, tokenId1, amount1],[fromAccount2, toAccount2, tokenId2, amount2]]
    :return: True or raise exception
    """
    for p in args:
        if len(p) != 4:
            raise Exception('transferMulti failed - input error!')
        if transfer(p[0], p[1], p[2], p[3]) == False:
            raise Exception('transferMulti failed - transfer error!')
    return True


def approve(owner, spender, tokenId, amount):
    """
    approve amount of the tokenId token to toAcct address, it can overwrite older approved amount
    :param owner:
    :param spender:
    :param tokenId:
    :param amount:
    :return:
    """
    Require(_whenNotPaused())
    # make sure the invoker is the owner address
    RequireWitness(owner)
    # make sure the address is legal
    Require(len(spender) == 20)
    Require(_tokenExist(tokenId))

    ownerBalance = balanceOf(owner, tokenId)
    # you can use "if" to notify the corresponding message, or use assert to raise exception
    Require(ownerBalance >= amount)
    Require(amount > 0)
    key = _concatkey(_concatkey(_concatkey(APPROVE_PREFIX, tokenId), owner), spender)
    Put(GetContext(), key, amount)

    ApprovalEvent(owner, spender, tokenId, amount)

    return True



def approveMulti(args):
    """
    multi approve
    :param args: args:[[owner1, spender1, tokenId1, amount1],[owner2, spender2, tokenId2, amount2]]
    :return:
    """
    for p in args:
        if len(p) != 4:
            raise Exception('approveMulti failed - input error!')
        if approve(p[0], p[1], p[2], p[3]) == False:
            raise Exception('approveMulti failed - approve error!')
    return True


def allowance(owner, spender, tokenId):
    """
    :param owner:
    :param spender:
    :param tokenId:
    :return:
    """
    key = _concatkey(_concatkey(_concatkey(APPROVE_PREFIX, tokenId), owner), spender)
    return Get(GetContext(), key)



def transferFrom(spender, fromAcct, toAcct, tokenId, amount):
    """
    :param tokenId: this tokenId token should be approved by its owner to toAcct
    :param toAcct: spender
    :param amount: False or True
    :return:
    """
    Require(_whenNotPaused())
    RequireWitness(spender)
    Require(len(fromAcct) == 20)
    Require(len(toAcct) == 20)
    #RequireScriptHash(spender)
    #RequireScriptHash(fromAcct)
    #RequireScriptHash(toAcct)
    Require(_tokenExist(tokenId))

    fromKey = _concatkey(_concatkey(BALANCE_PREFIX, tokenId), fromAcct)
    fromBalance = Get(GetContext(), fromKey)
    Require(fromBalance >= amount)
    Require(amount > 0)
    toKey = _concatkey(_concatkey(BALANCE_PREFIX, tokenId), toAcct)


    approvedKey = _concatkey(_concatkey(_concatkey(APPROVE_PREFIX, tokenId), fromAcct), spender)
    approvedAmount = Get(GetContext(), approvedKey)

    if amount > approvedAmount:
        raise Exception('you are not allowed to withdraw that amount')
    elif amount == approvedAmount:
        Delete(GetContext(), approvedKey)
        Put(GetContext(), fromKey, Sub(fromBalance, amount))
    else:
        Put(GetContext(), approvedKey, Sub(approvedAmount, amount))
        Put(GetContext(), fromKey, Sub(fromBalance, amount))

    toBalance = Get(GetContext(), toKey)
    Put(GetContext(), toKey, Add(toBalance, amount))

    TransferEvent(fromAcct, toAcct, tokenId, amount)

    return True


def transferFromMulti(args):
    """
    multiple transferFrom
    :param args: args:[[spender1, fromAcct1, toAcct1, tokenId1, amount1],[spender2, fromAcct2, toAcct2, tokenId2, amount2]]
    :return:
    """
    for p in args:
        if len(p) != 5:
            raise Exception('transferFromMulti failed - input error!')
        if transferFrom(p[0], p[1], p[2], p[3], p[4]) == False:
            raise Exception('transferFromMulti failed - transfer error!')
    return True
########################## Methods that meet the OEP8 protocal Ends ############################



#################### Special methods for CEO only defination starts  ######################
def setCLevel(option, account):
    """
    :param option: can be "CTO", "COO"
    :param account: the account to be set as the CLevel account
    :return:
    """
    RequireWitness(CEOAddress)
    CLevelKey = None
    if option == "CTO":
        CLevelKey = CTO_ADDRESS_KEY
    elif option == "COO":
        CLevelKey = COO_ADDRESS_KEY
    Put(GetContext(), CLevelKey, account)
    Notify(["setCLevel", option, account])
    return True

def setAuthorizedLevel(account):
    RequireWitness(CEOAddress)
    Require(len(account) == 20)
    isAuthorized = Get(GetContext(), _concatkey(AUTHORIZED_LEVEL_PREFIX, account))
    if isAuthorized == "T":
        Notify(["alreadyInAuthorizedLevel", account])
        return True
    if not isAuthorized:
        Put(GetContext(), _concatkey(AUTHORIZED_LEVEL_PREFIX, account), "T")
    Notify(["setAuthorizedLevel", account])
    return True

def removeAuthorizedLevel(account):
    RequireWitness(CEOAddress)
    Require(len(account) == 20)
    # make sure account is authorized before.
    Require(isAuthorizedLevel(account))
    Delete(GetContext(),_concatkey(AUTHORIZED_LEVEL_PREFIX, account))
    Notify(["removeAuthorizedLevel", account])
    return True


def createToken(tokenId, name, symbol):
    RequireWitness(CEOAddress)
    Require(not _tokenExist(tokenId))
    Require(_checkLegalTokenId(tokenId))
    # Put name and symbol in storage
    Put(GetContext(), _concatkey(NAME_PREFIX, tokenId), name)
    Put(GetContext(), _concatkey(SYMBOL_PREFIX, tokenId), symbol)
    # By default, the total supply is zero

    Notify(["createToken", tokenId, name, symbol])
    return True

def multiCreateToken(args):
    """
    :param tokenIdList:
    :param nameList:
    :param symbolList:
    :return:
    """
    for p in args:
        Require(len(p) == 3)
        Require(createToken(p[0], p[1], p[2]))
    return True

#################### Special methods for CEO only defination Ends  ######################


############# Special methods for C Level accounts only defination Starts  ################
def pause():
    Require(_onlyCLevel())
    Put(GetContext(), CONTRACT_PAUSED_KEY, "T")
    Notify(["pause"])
    return True

def unpause():
    Require(_onlyCLevel())
    Put(GetContext(), CONTRACT_PAUSED_KEY, "F")
    Notify(["unpause"])
    return True
############# Special methods for C Level accounts only defination Ends  ################


############# Special methods for C Level and authorized level defination Starts  ################
def mintToken(mintAcct, toAcct, tokenId, amount):
    RequireWitness(mintAcct)
    Require(_whenNotPaused())
    Require(_onlyCLevel() or isAuthorizedLevel(mintAcct))
    # make sure the to address is legal
    Require(len(toAcct) == 20)
    # make sure the tokenId has been created already
    Require(_tokenExist(tokenId))
    # make sure the amount is legal, which is greater than ZERO
    Require(amount > 0)
    # update the to account balance
    Put(GetContext(), _concatkey(_concatkey(BALANCE_PREFIX, tokenId), toAcct), Add(balanceOf(toAcct, tokenId), amount))
    # update the total supply
    Put(GetContext(), _concatkey(TOTAL_SUPPLY_PREFIX, tokenId), Add(totalSupply(tokenId), amount))
    # make sure the total supply is not greater than 1 billion
    Require(totalSupply(tokenId) <= 10000000000)
    # Notify the event to the block chain
    TransferEvent("", toAcct, tokenId, amount)
    # Notify(["transfer", "", toAcct, tokenId, amount])
    return True

def multiMintToken(args):
    for p in args:
        Require(len(p) == 4)
        Require(mintToken(p[0], p[1], p[2], p[3]))
    return True

def burnToken(account, tokenId, amount):
    Require(_whenNotPaused())
    assert (_onlyCLevel() or isAuthorizedLevel(account))
    # make sure the tokenId has been created already
    Require(_tokenExist(tokenId))
    # make sure the amount is legal, which is greater than ZERO
    balance = balanceOf(account, tokenId)
    #assert (amount > 0 and amount <= balance)
    Require(amount <= balance)
    Require(amount > 0)
    # update the to account balance
    if amount == balance:
        Delete(GetContext(), _concatkey(_concatkey(BALANCE_PREFIX, tokenId), account))
    else:
        Put(GetContext(), _concatkey(_concatkey(BALANCE_PREFIX, tokenId), account), Sub(balance, amount))
    # update the total supply
    _totalSupply = totalSupply(tokenId)
    if _totalSupply == amount:
        Delete(GetContext(), _concatkey(TOTAL_SUPPLY_PREFIX, tokenId))
    else:
        Put(GetContext(), _concatkey(TOTAL_SUPPLY_PREFIX, tokenId), Sub(_totalSupply, amount))
    # Notify the event to the block chain
    TransferEvent(account, "", tokenId, amount)
    return True

def multiBurnToken(args):
    for p in args:
        Require(len(p) == 3)
        Require(burnToken(p[0], p[1], p[2]))
    return True
############# Special methods for C Level and authorized level defination Ends  ################



#################### Optional methods defination starts  ######################
def getCTO():
    """
    :return: the CTO address
    """
    return Get(GetContext(), CTO_ADDRESS_KEY)

def getCOO():
    """
    :return: the COO address
    """
    return Get(GetContext(), COO_ADDRESS_KEY)

def isAuthorizedLevel(account):
    isAuthorized = Get(GetContext(), _concatkey(AUTHORIZED_LEVEL_PREFIX, account))
    if isAuthorized == "T":
        return True
    return False
#################### Optional methods defination Ends ######################



#################### Private methods defination starts ######################
def _onlyCLevel():
    isCEO = CheckWitness(CEOAddress)
    isCTO = None
    isCOO = None
    CTOAddress = getCTO()
    if len(CTOAddress) == 20:
        isCTO = CheckWitness(CTOAddress)
    COOAddress = getCOO()
    if len(COOAddress) == 20:
        isCOO = CheckWitness(COOAddress)
    return isCEO or isCTO or isCOO

def _whenNotPaused():
    isPaused = Get(GetContext(), CONTRACT_PAUSED_KEY)
    if isPaused == "T":
        return False
    elif isPaused == "F":
        return True

def _checkLegalTokenId(tokenId):
    """
    AAA,BBB
    :param tokenId: integer AAA = 001, 002, 003, ..., 999; BBB = 001, 002, 003, ..., 999
    :return: True or False
    """
    return tokenId >= 1001 and tokenId <= 999999

def _tokenExist(tokenId):
    if name(tokenId):
        return True
    else:
        return False

def _concatkey(str1, str2):
    return concat(concat(str1, '_'), str2)
#################### Private methods defination Ends ######################